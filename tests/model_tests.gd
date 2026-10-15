extends SceneTree

const State = preload("res://scripts/world_state.gd")
var failures: int = 0

func check(condition: bool, message: String) -> void:
	if not condition:
		failures += 1
		printerr("FAIL: ", message)

func _initialize() -> void:
	var db: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json"))
	var state := State.new()
	state.initialize(db)
	check(state.date_label() == "00:00  ·  1 January 2000", "scenario date")
	for tag: String in state.countries:
		check(float(state.countries[tag]["starting_stats"]["political_power"]) == 100, "uniform political power for " + tag)
		check(is_equal_approx(float(state.countries[tag]["starting_stats"]["stability"]), .65) and is_equal_approx(float(state.countries[tag]["starting_stats"]["war_support"]), .5), "uniform base values for " + tag)
	check(state.paused, "new game paused")
	state.advance(0.25)
	check(state.hour == 0, "paused clock must not advance")
	state.paused = false
	for i: int in 4:
		state.advance(0.25)
	check(state.hour == 1, "one hour at normal speed")
	state.speed = 30
	state.advance(0.25)
	check(state.hour == 8, "fast clock preserves whole hours")
	state.hour = 23
	state.speed = 1
	state.accumulator = 0.0
	for tick: int in 4: state.advance(0.25)
	check(state.date_label() == "00:00  ·  2 January 2000", "hour 23 rolls over at midnight")
	state.hour = 59 * 24
	check(state.date_label() == "00:00  ·  29 February 2000", "leap day")
	state.hour = 366 * 24 + 13
	check(state.date_label() == "13:00  ·  1 January 2001", "year rollover")
	check(state.memberships("GER").has("EU") and state.memberships("GER").has("NATO"), "many-to-many membership")
	check(state.organizations["EU"]["members"].size() == 15, "dated EU membership")
	check(state.organizations["ASEAN"]["members"].size() == 10, "ASEAN membership")
	var sample_region: int = int(state.countries["SIN"]["capital"])
	var singapore_before: int = int(state.country_metrics("SIN")["population"])
	var before_total: int = 0
	for region: Dictionary in state.regions.values():
		before_total += int(region["population"])
	var singapore_pop: int = int(state.regions[str(sample_region)]["population"])
	var thai_population: int = int(state.country_metrics("SIA")["population"])
	check(state.transfer_region(sample_region, "SIA"), "regional ownership can change")
	check(int(state.country_metrics("SIA")["population"]) == thai_population + singapore_pop, "transfer moves population with region")
	check(state.country_metrics("SIN")["population"] == singapore_before - singapore_pop, "transfer removes old ownership")
	check(not state.transfer_region(sample_region, "INVALID"), "reject unknown owner")
	state.organizations["ASEAN"]["budget"] = 2.5
	state.countries["POL"]["starting_stats"]["stability"] = 0.82
	state.countries["POL"]["cosmetic"] = "POL_AUTH"
	state.player_country = "POL"
	state.selected_country = "SIA"
	state.selected_region = sample_region
	var pid: int = int(state.regions[str(sample_region)]["provinces"][0])
	state.selected_province = pid
	state.provinces[str(pid)]["buildings"] = {"airfield": 1}
	state.countries["POL"]["color_override"] = [23, 45, 67]
	check(state.province_owner(pid) == "SIA", "province follows region transfer")
	var view := {"rotation": [0.3, -1.1], "distance": 1.06, "map_mode": 6, "organization": "ASEAN", "show_regions": true, "inspection_active": true, "relations_reverse": false}
	check(state.set_opinion("JAP", "CHI", -73), "set directional relation")
	var inverse := state.opinion("CHI", "JAP")
	check(state.opinion("JAP", "CHI") == -73, "directed opinion")
	var path := "user://tests/model_roundtrip.json"
	check(state.save_game(path, view), "save world")
	state.reset()
	var loaded := state.load_game(path)
	if loaded.is_empty():
		printerr("Roundtrip load error: ", state.last_error)
	check(loaded.get("organization") == view["organization"] and int(loaded.get("map_mode", -1)) == view["map_mode"] and loaded.get("show_regions") == true, "map mode roundtrip")
	check(is_equal_approx(float(loaded.get("distance", 0)), 1.06) and is_equal_approx(float(loaded.get("rotation", [0, 0])[0]), 0.3) and is_equal_approx(float(loaded.get("rotation", [0, 0])[1]), -1.1), "camera roundtrip")
	check(is_equal_approx(float(state.countries["POL"]["starting_stats"]["stability"]), 0.82) and state.countries["POL"]["cosmetic"] == "POL_AUTH", "country values persist")
	check(state.selected_province == pid and state.provinces[str(pid)]["buildings"].get("airfield") == 1, "province selection and future buildings persist")
	check(state.country_color("POL") == [23, 45, 67], "cosmetic color persists")
	check(state.opinion("JAP", "CHI") == -73 and state.opinion("CHI", "JAP") == inverse, "directional relations persist independently")
	check(state.player_country == "POL", "player country persists separately from inspection")
	check(state.organizations["CSTO"]["members"].size() == 6, "CSTO membership")
	check(state.hour == 366 * 24 + 13 and state.selected_country == "SIA", "clock and selected country roundtrip")
	check(state.regions[str(sample_region)]["owner"] == "SIA", "territory roundtrip")
	check(state.organizations["ASEAN"]["budget"] == 2.5, "organization roundtrip")
	check(state.selected_region == sample_region and state.paused, "selected region and safe paused load")
	var after_total: int = 0
	for region: Dictionary in state.regions.values():
		after_total += int(region["population"])
	check(before_total == after_total, "population conserved across transfer and reload")
	check(state.save_game(path, view), "second save")
	check(FileAccess.file_exists(path + ".bak"), "previous-save backup")
	var file := FileAccess.open("user://tests/corrupt.json", FileAccess.WRITE)
	file.store_string('{"format":"BunnyWorldSave","payload":"broken","checksum":"wrong"}')
	file.close()
	var old_day := state.day
	check(state.load_game("user://tests/corrupt.json").is_empty(), "reject damaged save")
	check(state.day == old_day and state.regions[str(sample_region)]["owner"] == "SIA", "failed load must not mutate world")
	var envelope: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(path))
	var invalid_payload: Dictionary = JSON.parse_string(envelope["payload"])
	invalid_payload["regions"][str(sample_region)]["population"] = -10
	var invalid_body := JSON.stringify(invalid_payload)
	file = FileAccess.open("user://tests/invalid.json", FileAccess.WRITE)
	file.store_string(JSON.stringify({"format": "BunnyWorldSave", "payload": invalid_body, "checksum": invalid_body.sha256_text()}))
	file.close()
	check(state.load_game("user://tests/invalid.json").is_empty(), "reject negative population even with correct checksum")
	check(state.day == old_day, "validated load is atomic")
	for bad_view: Dictionary in [{"distance": 1.0}, {"map_mode": 8}]:
		invalid_payload = JSON.parse_string(envelope["payload"])
		for field: String in bad_view:
			invalid_payload["view"][field] = bad_view[field]
		invalid_body = JSON.stringify(invalid_payload)
		file = FileAccess.open("user://tests/invalid_view.json", FileAccess.WRITE)
		file.store_string(JSON.stringify({"format": "BunnyWorldSave", "payload": invalid_body, "checksum": invalid_body.sha256_text()}))
		file.close()
		check(state.load_game("user://tests/invalid_view.json").is_empty(), "reject invalid view")
		check(state.player_country == "POL" and state.day == old_day, "invalid view does not change campaign")
	if failures == 0:
		print("MODEL_TESTS_PASS: dates, clock, ownership, memberships, save/load, corruption rejection, conservation")
	quit(failures)
