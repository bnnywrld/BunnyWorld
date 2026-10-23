extends SceneTree
const State = preload("res://scripts/world_state.gd")
const Resources = preload("res://scripts/resource_icons.gd")
const Roster = preload("res://scripts/government_roster.gd")
var checks := 0
var failures := 0
var notices: Array = []
func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok: failures += 1; push_error(message)
func _initialize() -> void: run.call_deferred()
func run() -> void:
	var world := State.new()
	world.initialize(JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json")))
	world.completion_notice.connect(func(kind: String,text: String): notices.append([kind,text]))
	world.countries["JAP"]["starting_stats"]["political_power"] = 10000
	check(world.change_government_property("JAP","form_of_government","Republic"),"constitutional reform accepted")
	check(world.government_property("JAP","form_of_government") == "Constitutional Monarchy","reform deferred")
	check(world.agenda.queue[0]["days"] == 30 and world.political_power("JAP") == 9900,"base 30 days, PP charged upfront once")
	check(not world.change_government_property("JAP","form_of_government","Absolute Monarchy"),"duplicate property rejected")
	check(not world.change_government_property("USA","executive","Parliamentary"),"foreign reforms rejected")
	check(world.change_government_property("JAP","religion","Theocracy","Buddhist"),"second reform queued")
	check(world.agenda.queue[1]["days"] == 270,"three-step drastic reform takes nine base durations")
	world.agenda.advance_days(29)
	check(world.government_property("JAP","form_of_government") == "Constitutional Monarchy" and world.agenda.queue[1]["elapsed"] == 0,"waiting reform makes no progress")
	world.hour = 23
	world.accumulator = 1
	world.advance(0)
	check(world.agenda.queue[0]["elapsed"] == 29,"paused clock freezes agenda")
	world.paused = false
	world.advance(0)
	check(world.government_property("JAP","form_of_government") == "Republic" and world.agenda.queue[0]["elapsed"] == 0,"midnight completes head, next begins next day")
	check(notices.size() == 1 and notices[0][0] == "Agenda completed","one completion event")
	check(world.government_property("JAP","religion") == "Secular State","faith policy stays unchanged while queued")
	world.agenda.advance_days(12)
	var view := {"rotation":[0,0],"distance":2.,"map_mode":0,"organization":"EU","show_regions":false,"inspection_active":false,"relations_reverse":false}
	var path := OS.get_environment("TEMP").path_join("bunnyworld-agenda-trade-qa/agenda.bws")
	DirAccess.make_dir_recursive_absolute(path.get_base_dir())
	check(world.save_game(path,view),"save agenda")
	var envelope: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(path))
	var saved: Dictionary = JSON.parse_string(envelope["payload"])
	var agenda: Array = saved["agenda"].duplicate(true)
	world.reset()
	check(not world.load_game(path).is_empty(),"load agenda: " + world.last_error)
	check(world.agenda.queue == agenda,"agenda progress/price/target persist")
	for field: String in ["elapsed","days","cost","from","faith","country","key"]:
		var bad := saved.duplicate(true)
		match field:
			"elapsed": bad["agenda"][0][field] = 270
			"days": bad["agenda"][0][field] = 30
			"cost": bad["agenda"][0][field] = 0
			"from": bad["agenda"][0][field] = "State Religion"
			"faith": bad["agenda"][0][field] = "Unknown"
			"country": bad["agenda"][0][field] = "USA"
			"key": bad["agenda"][0][field] = "unknown"
		var bad_path := path + ".bad"
		var file := FileAccess.open(bad_path,FileAccess.WRITE)
		var body := JSON.stringify(bad)
		file.store_string(JSON.stringify({"format":"BunnyWorldSave","payload":body,"checksum":body.sha256_text()}));file.close()
		check(world.load_game(bad_path).is_empty() and world.agenda.queue == agenda,"invalid agenda rejected atomically: " + field)
	world.agenda.advance_days(258)
	check(world.agenda.queue.is_empty() and world.government_property("JAP","religion") == "Theocracy" and world.society.nations["JAP"]["affiliation"] == "Buddhist","reform applies policy and affiliation together")
	check(world.political_power("JAP") == 9001,"completion does not charge a second time")
	world.reset()
	check(world.regions["1687"]["resources"]["oil"] == 21,"California retains MD's whole named resource pool")
	check(Resources.amount(.005) == "<0.01 RU" and Resources.amount(21) == "21 RU","RU display consistent")
	for key: String in Resources.ORDER: check(Resources.icon(key) != null,"resource symbol exists: " + key)
	var leaders: Dictionary = world.political_leaders["countries"]
	var portrait_count := 0
	for country: Dictionary in leaders.values():
		for role: String in ["head_of_state","head_of_government"]:
			var person: Variant = country[role]
			if person == null: continue
			check(not str(person["portrait"]).is_empty() and load(person["portrait"]) is Texture2D,"named office has a loadable MD portrait")
			portrait_count += 1
	check(portrait_count == 226,"all named offices have portraits")
	check(leaders["JAP"]["head_of_state"]["name"] == "Emperor Akihito" and leaders["JAP"]["head_of_government"]["name"] == "Keizo Obuchi","Japan named offices distinct")
	check(leaders["USA"]["head_of_state"]["name"] == "Bill Clinton" and leaders["USA"]["head_of_government"] == null,"single leader not duplicated")
	check(leaders["GER"]["head_of_government"]["name"] == "Gerhard Schröder" and leaders["GER"]["head_of_state"] == null,"parliamentary leader role and encoding")
	check(leaders["ENG"]["head_of_state"]["name"] == "Elizabeth II","named monarch from explicit starting flag")
	check(Roster.status(world,"GER","3") == "Ruling party" and Roster.status(world,"GER","17") == "Government coalition","explicit MD party IDs mark government")
	check(Roster.status(world,"GER","1") == "","opposition not assigned to government")
	check(leaders["LEB"]["head_of_state"] == null and leaders["LEB"]["head_of_government"] == null,"missing political leader never replaced by an army commander")
	var model = world.construction
	check(model.catalog["data_center"]["money_usd"] == 6e9 and model.catalog["data_center"]["points"] == 36000,"Data Center balance")
	check(world.state_economy["workers_per_level"]["data_center"] == 10000,"Data Center employee demand")
	var sid := ""
	for id: String in world.regions:
		if world.regions[id]["owner"] == "JAP" and model.blocked(id,"data_center").is_empty(): sid = id; break
	check(not sid.is_empty(),"Data Center placeable")
	var free: int = model.free_slots(sid)
	check(model.add(sid,"data_center") and model.free_slots(sid) == free-1,"Data Center reserves shared slot")
	var job: Dictionary = model.queue[0]
	job["progress"] = float(job["points"])-.00001
	model.advance_days(1)
	check(world.regions[sid]["buildings"]["data_center"] == 1 and model.queue.is_empty(),"Data Center completion")
	check(world.employment.states[sid]["demand"]["data_center"] == 10000,"completed Data Center participates in staffing")
	check(notices.back()[0] == "Construction completed","construction emits completion event")
	check(world.save_game(path,view),"new building saves")
	world.reset()
	check(not world.load_game(path).is_empty() and world.regions[sid]["buildings"]["data_center"] == 1,"Data Center survives load")
	print("AGENDA_TRADE_MODEL checks=",checks," failures=",failures)
	quit(0 if failures == 0 else 1)
