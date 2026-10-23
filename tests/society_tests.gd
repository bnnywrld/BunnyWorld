extends SceneTree
const State = preload("res://scripts/world_state.gd")
const Demographics = preload("res://scripts/demography.gd")
const Religions = preload("res://scripts/religion_catalog.gd")
var checks := 0
var failures := 0
func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok: failures += 1; push_error(message)
func _initialize() -> void: run.call_deferred()
func same(a: Variant, b: Variant) -> bool:
	if a is Dictionary and b is Dictionary:
		if a.size() != b.size(): return false
		for key: Variant in a:
			if not b.has(key) or not same(a[key], b[key]): return false
		return true
	if (a is int or a is float) and (b is int or b is float): return absf(float(a)-float(b)) <= 1e-10
	return a == b
func run() -> void:
	var world := State.new()
	world.initialize(JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json")))
	var model = world.society
	var demographic := Demographics.new()
	var baseline: Dictionary = world.regions.duplicate(true)
	check(model.nations.size() == 224, "all countries seeded")
	for tag: String in world.countries:
		check(world.countries[tag]["outlook"] in model.OUTLOOKS or world.countries[tag]["outlook"] == "Unspecified", "only supported outlooks")
		check(is_equal_approx(float(model.rules["annual_population_growth"]), .01) and model.annual_growth_rate(tag)>0, "shared base rate plus initial healthcare modifier")
		var total := 0
		for party: Dictionary in model.parties(tag):
			check(party["outlook"] in model.OUTLOOKS, "excluded outlook never imported")
			check(not str(party["name"]).is_empty() and "£" not in str(party["name"]), "displayable party name")
			var seats := int(model.nations[tag]["seats"].get(party["id"], 0))
			if float(party["support"]) < 1: check(seats == 0, "strict one percent threshold")
			total += seats
		check(total == 100 or total == 0, "100 seats allocated when any eligible party exists")
		check(model.nations[tag]["approval"] == null and world.economy.nations[tag]["education_quality"] >= 0, "unsupported scores absent")
	var japan: Dictionary = model.parties("JAP")[1]
	check("Liberal Democratic Party" in japan["name"] and is_equal_approx(japan["support"], 52.6), "MD Japanese party and support")
	check(model.unrepresented("SAU") > 70, "excluded source support not reassigned")
	var allocation: Dictionary = model.allocate_seats({"a":.999, "b":1., "c":99.})
	check(not allocation.has("a") and allocation["b"] == 1 and allocation["c"] == 99, "exactly 1 percent qualifies")
	check(model.allocate_seats({"a":.5, "b":.8}).is_empty(), "no eligible party means no invented seats")
	world.hour = 743
	world.accumulator = 1
	world.advance(0)
	check(world.regions == baseline, "paused prevents population growth")
	world.paused = false
	world.advance(0)
	check(model.last_month == 2000*12+1, "first of February tick")
	var one_month: Dictionary = world.regions.duplicate(true)
	model.advance_months()
	check(world.regions == one_month, "same month cannot grow twice")
	world.hour = 366*24
	model.advance_months()
	for sid: String in baseline:
		check(world.regions[sid]["population"] >= 0 and model.remainders[sid]>=0 and model.remainders[sid]<1, "population and fractional remainders remain bounded with economic modifiers")
		var entry := demographic.state_metrics(world, int(sid))
		for key: String in ["age", "religion", "education"]:
			var total := 0
			for count: Variant in entry["metrics"][key]["counts"].values(): total += int(count)
			check(total == int(entry["metrics"][key]["denominator"]), "demographic count conservation")
	check(Religions.canonical("Nonreligious") == "Atheist" and Religions.canonical("Other / unspecified") != "Atheist", "unknown not conflated with atheism")
	check(Religions.shares({"Maronite":2,"Catholic":3}) == {"Catholic":5.}, "aliases merge without people loss")
	check(Religions.color("Greek Catholic") == Religions.color("Catholic"), "global colors follow canonical identity")
	var stats: Dictionary = world.countries["JAP"]["starting_stats"].duplicate(true)
	var population_before := demographic.country_metrics(world, "JAP")
	world.countries["JAP"]["starting_stats"]["political_power"] = 2000
	check(not world.change_government_property("JAP", "religion", "State Religion"), "affiliated policy requires explicit faith")
	check(not world.change_government_property("JAP", "religion", "State Religion", "Unknown"), "unknown cannot be state affiliation")
	check(world.change_government_property("JAP", "religion", "State Religion", "Buddhist"), "explicit religion selection")
	check(world.political_power("JAP") == 1600, "two-step jump charged once")
	check(model.nations["JAP"]["affiliation"] == "", "faith awaits agenda completion")
	world.agenda.advance_days(120)
	check(model.nations["JAP"]["affiliation"] == "Buddhist", "affiliation stored")
	check(population_before == demographic.country_metrics(world, "JAP"), "policy does not convert citizens")
	check(world.change_government_property("JAP", "religion", "State Religion", "Shinto / Buddhist") == false, "ambiguous combined label cannot endorse an invented branch")
	check(world.change_government_property("JAP", "religion", "State Religion", "Sunni") and world.political_power("JAP") == 1500, "affiliation reform one shared base cost")
	world.agenda.advance_days(30)
	check(not world.change_government_property("USA", "religion", "Theocracy", "Catholic"), "foreign laws protected")
	for field: String in stats:
		if field != "political_power": check(stats[field] == world.countries["JAP"]["starting_stats"][field], "no unfinished stat effects")
	var directory := OS.get_environment("TEMP").path_join("bunnyworld-society-qa")
	DirAccess.make_dir_recursive_absolute(directory)
	var path := directory.path_join("society-save.bws")
	var view := {"rotation":[0,0],"distance":2.,"map_mode":0,"organization":"EU","show_regions":false,"inspection_active":false,"relations_reverse":false}
	var saved: Dictionary = model.export_state()
	check(world.save_game(path,view), "save society")
	world.reset()
	check(not world.load_game(path).is_empty(), "load society: " + world.last_error)
	check(same(model.export_state(), saved), "all demographic remainders, policy and party snapshots round trip")
	check(world.regions != one_month, "loaded grown world retained")
	var national: Dictionary = {}
	for tag: String in world.countries: national[tag] = {"government_properties":world.government_properties[tag]}
	for broken: String in ["remainder", "month", "faith", "support", "seat", "approval"]:
		var bad := saved.duplicate(true)
		match broken:
			"remainder": bad["remainders"][str(bad["remainders"].keys()[0])] = 1.1
			"month": bad["last_month"] -= 1
			"faith": bad["nations"]["JAP"]["affiliation"] = "Invented"
			"support": bad["nations"]["JAP"]["polls"]["1"] = 101
			"seat": bad["nations"]["JAP"]["seats"]["1"] = 101
			"approval": bad["nations"]["JAP"]["approval"] = 50
		check(not model.valid(bad, world.hour, national), "reject invalid " + broken)
	var envelope: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(path))
	var payload: Dictionary = JSON.parse_string(envelope["payload"])
	payload["society"]["remainders"][str(world.regions.keys()[0])] = -1
	var body := JSON.stringify(payload)
	var bad_path := directory.path_join("society-invalid.bws")
	var file := FileAccess.open(bad_path, FileAccess.WRITE)
	file.store_string(JSON.stringify({"format":"BunnyWorldSave","payload":body,"checksum":body.sha256_text()}))
	file.close()
	var before_bad: Dictionary = model.export_state()
	check(world.load_game(bad_path).is_empty() and model.export_state() == before_bad, "invalid society save rejected atomically")
	# Compare sequential and batched years, including tiny populations and an ownership transfer.
	world.reset()
	var sid := str(int(world.countries["SIN"]["capital"]))
	world.regions[sid]["population"] = 10
	world.hour = 366*24
	model.advance_months()
	check(world.regions[sid]["population"] == 10 and model.remainders[sid] > .09, "small population retains fractional growth")
	var residue: float = model.remainders[sid]
	check(world.transfer_region(int(sid), "JAP") and model.remainders[sid] == residue, "ownership transfer preserves fractional residents")
	var started := Time.get_ticks_usec()
	world.hour = int((Time.get_unix_time_from_datetime_string("2010-01-01T00:00:00") - world.scenario_epoch)/3600)
	model.advance_months()
	check(world.regions[sid]["population"] >= 10, "decade growth on tiny state")
	print("SOCIETY_MODEL checks=", checks, " failures=", failures, " century_ms=", (Time.get_ticks_usec()-started)/1000.)
	quit(0 if failures == 0 else 1)
