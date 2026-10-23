extends SceneTree
const State = preload("res://scripts/world_state.gd")
const Institutions = preload("res://scripts/research_institutions.gd")
var checks := 0
var failures := 0
func check(ok: bool, description: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		push_error(description)

func _initialize() -> void:
	var world := State.new()
	world.initialize(JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json")))
	world.player_country = "JAP"
	var r = world.research
	var universities := Institutions.for_country(world, "JAP")
	check(r.catalog.size() == 1230 and r.categories.size() == 11, "full imported modern technology catalog")
	check(r.completed["JAP"].has("nanofibers_3") and not r.completed["JAP"].has("nanofibers_4"), "actual Japan 2000 history")
	check(r.completed["USA"] != r.completed["JAP"], "country-specific starting technologies")
	for tech: String in r.catalog:
		var t: Dictionary = r.catalog[tech]
		check(t["days"] > 0 and not t["name"].is_empty(), "valid cost/name: " + tech)
		for parent: String in t["parents"] + t["dependencies"]:
			check(r.catalog[parent]["row"] < t["row"], "graph descends: " + parent + " -> " + tech)
	check(r.reason("JAP", "nanofibers_5").begins_with("Requires"), "cannot skip prerequisites")
	check(not r.start("JAP", universities[0], "nanofibers_5"), "locked selection rejected")
	check(not r.start("USA", "Harvard University", "nanofibers_4"), "non-player research rejected")
	check(not r.start("JAP", "Invented University", "nanofibers_4"), "unknown institution rejected")
	check(r.start("JAP", universities[0], "nanofibers_4"), "research starts at selected university")
	check(not r.start("JAP", universities[1], "nanofibers_4"), "duplicate active project rejected")
	var economic: Dictionary = world.countries["JAP"]["starting_stats"].duplicate(true)
	world.hour = 23
	world.paused = true
	world.accumulator = 1
	world.advance(0)
	check(r.progress["JAP"].is_empty(), "paused simulation preserves progress")
	world.paused = false
	world.advance(0)
	check(is_equal_approx(r.progress["JAP"]["nanofibers_4"], world.economy.research_multiplier("JAP")), "midnight advances one day")
	check(is_equal_approx(r.penalty("nanofibers_4"), 1.0) and r.penalty("nanofibers_5") > 5.9, "future technology remains available with time penalty")
	var before: float = r.penalty("nanofibers_5")
	world.day = 366
	check(r.penalty("nanofibers_5") < before, "ahead penalty declines with campaign date")
	check(r.start("JAP", universities[0], "printing_4"), "switch university project")
	check(is_equal_approx(r.progress["JAP"]["nanofibers_4"], world.economy.research_multiplier("JAP")), "switched project keeps national progress")
	check(r.start("JAP", universities[1], "nanofibers_4"), "resume at another university")
	var days: int = maxi(r.remaining_days("JAP", "nanofibers_4"), r.remaining_days("JAP", "printing_4"))
	world.day += days
	r.advance_days(days)
	check(r.completed["JAP"].has("nanofibers_4") and r.completed["JAP"].has("printing_4"), "universities complete independent projects")
	check(r.assignments["JAP"].is_empty() and r.notifications.size() == 2, "completion frees slots and produces notifications")
	check(not world.paused and world.countries["JAP"]["starting_stats"]["treasury_usd"] == economic["treasury_usd"], "completion never pauses or applies economic effects")
	check(r.reason("JAP", "nanofibers_5").is_empty(), "completion unlocks next technology")
	check(r.start("JAP", universities[0], "nanofibers_5"), "start ahead-of-time project")
	world.day += 5
	r.advance_days(5)
	check(r.progress["JAP"]["nanofibers_5"] > 0 and r.progress["JAP"]["nanofibers_5"] < 5, "ahead-of-time penalty reduces daily progress")
	check(r.start("JAP", universities[1], "printing_5"), "start second future project")
	world.day += 3
	r.advance_days(3)
	r.stop("JAP", universities[1])
	var data: Dictionary = r.export_state()
	check(r.valid(data, "JAP", world.hour), "valid research save accepted")
	var invalid := data.duplicate(true)
	invalid["progress"]["JAP"]["nanofibers_5"] = -1
	check(not r.valid(invalid, "JAP", world.hour), "negative saved progress rejected")
	invalid = data.duplicate(true)
	invalid["assignments"]["JAP"][universities[2]] = "nanofibers_5"
	check(not r.valid(invalid, "JAP", world.hour), "duplicate saved project rejected")
	invalid = data.duplicate(true)
	invalid["notifications"][0]["hour"] = world.hour + 24
	check(not r.valid(invalid, "JAP", world.hour), "future completion notification rejected")
	var view := {"rotation":[0,0],"distance":2.0,"map_mode":0,"organization":"EU","show_regions":false,"inspection_active":false,"relations_reverse":false}
	var directory := OS.get_environment("BUNNYWORLD_QA_DIR")
	if directory.is_empty(): directory = OS.get_environment("TEMP").path_join("bunnyworld-research-qa")
	DirAccess.make_dir_recursive_absolute(directory)
	var path := directory.path_join("research-save.json")
	world.society.advance_months()
	check(world.save_game(path, view), "save campaign research")
	r.reset()
	check(not world.load_game(path).is_empty(), "load campaign research")
	check(r.assignments == data["assignments"], "assignments round-trip")
	check(r.completed == data["completed"], "unlocks round-trip")
	check(r.notifications.size() == data["notifications"].size(), "notification count round-trip")
	for index: int in r.notifications.size():
		for key: String in ["tag", "tech", "institution", "hour"]:
			check(r.notifications[index][key] == data["notifications"][index][key], "notification field round-trip: " + key)
	check(is_equal_approx(r.progress["JAP"]["nanofibers_5"], data["progress"]["JAP"]["nanofibers_5"]), "progress round-trip")
	check(is_equal_approx(r.progress["JAP"]["printing_5"], data["progress"]["JAP"]["printing_5"]) and r.assignments["JAP"].size() == 1, "unassigned technology retains work through save/load")
	var envelope: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(path))
	var payload: Dictionary = JSON.parse_string(envelope["payload"])
	payload["research"]["assignments"]["JAP"][universities[2]] = "unknown_technology"
	var body := JSON.stringify(payload)
	var bad_path := directory.path_join("research-invalid.json")
	var file := FileAccess.open(bad_path, FileAccess.WRITE)
	file.store_string(JSON.stringify({"format":"BunnyWorldSave", "payload":body, "checksum":body.sha256_text()}))
	file.close()
	var before_load: Dictionary = r.export_state()
	check(world.load_game(bad_path).is_empty() and r.export_state() == before_load, "invalid research save rejected before live state changes")
	r.dismiss(0)
	check(r.notifications.size() == 1, "notification dismissed independently")
	r.advance_days(0)
	check(r.notifications.size() == 1, "completion notification is not repeated")
	print("RESEARCH_MODEL checks=", checks, " failures=", failures)
	quit(0 if failures == 0 else 1)
