extends SceneTree
const State = preload("res://scripts/world_state.gd")
const Demographics = preload("res://scripts/demography.gd")
const Facilities = preload("res://scripts/facility_catalog.gd")
var checks := 0
var failures := 0
func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok: failures += 1; push_error(message)
func _initialize() -> void: run.call_deferred()
func run() -> void:
	var world := State.new()
	world.initialize(JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json")))
	var model = world.employment
	var demographics := Demographics.new()
	var totals: Dictionary = {}
	var capacity_before: Dictionary = {}
	for sid: String in world.regions:
		var region: Dictionary = world.regions[sid]
		var seed: Dictionary = world.state_economy["states"][sid]
		check(region["cores"] == seed["cores"] and region["claims"] == seed["claims"], "MD territorial rights seeded")
		for tag: String in region["cores"] + region["claims"]: check(not world.country_record(tag).is_empty(), "every flag has country metadata")
		for resource: String in region["resources"]: totals[resource] = float(totals.get(resource,0)) + float(region["resources"][resource])
		capacity_before[sid] = int(region["construction_slots"])
		check(Facilities.slots(region)["capacity"] == region["construction_slots"], "inspector/queue capacity agree")
		var workforce: Dictionary = demographics.state_metrics(world,int(sid))["workforce"]
		var entry: Dictionary = model.states[sid]
		var assigned := 0
		for key: String in entry["workers"]:
			assigned += int(entry["workers"][key])
			check(entry["workers"][key] >= 0 and entry["workers"][key] <= entry["demand"][key], "staffing bounded by vacancies")
		check(assigned + int(entry["other_employment"]) == int(workforce["employed"]), "existing workers conserved")
		check(entry["unemployed"] == workforce["unemployed"] and entry["inactive"] == workforce["outside_labour_force"], "unemployment/inactivity preserved")
	for resource: String in world.state_economy["report"]["resource_totals"]:
		check(absf(float(totals.get(resource,0))-float(world.state_economy["report"]["resource_totals"][resource])) < .00001, "resource pools not duplicated or lost")
	check(world.state_economy["report"]["unmapped_resource_sources"].is_empty(), "all resource sources represented")
	check(world.country_record("PAU")["name"] == "Palau", "new inactive core country has source name")
	check(world.state_economy["workers_per_level"]["industrial_complex"] == 206000 and world.state_economy["workers_per_level"]["offices"] == 473000, "MD base worker counts")
	check(world.state_economy["diplomatic_actions"].size() == 83, "full inactive diplomacy catalogue")
	for action: Dictionary in world.state_economy["diplomatic_actions"].values(): check(action["inactive"], "diplomacy stays inactive")
	world.hour = 366*24
	world.society.advance_months()
	var expanded := 0
	for sid: String in world.regions:
		var region: Dictionary = world.regions[sid]
		check(region["construction_slots"] >= capacity_before[sid], "population growth never removes capacity")
		check(region["construction_slots"] >= world.construction.capacity(region["area_km2"], int(region["population"])), "monthly capacity follows current population")
		if region["construction_slots"] > capacity_before[sid]: expanded += 1
	check(expanded > 0, "real default growth opens slots where thresholds crossed")
	world.reset()
	for id: String in world.regions:
		var sample: Dictionary = world.regions[id]
		var previous_slots := int(sample["construction_slots"])
		var previous_curve: int = world.construction.capacity(sample["area_km2"], int(sample["population"]))
		if previous_slots <= previous_curve or int(sample["population"]) < 1000: continue
		sample["population"] = int(sample["population"]) * 2
		world.construction.refresh_capacities()
		var curve_growth: int = world.construction.capacity(sample["area_km2"], int(sample["population"])) - previous_curve
		check(curve_growth > 0, "population component grows for inventory-heavy state")
		check(int(sample["construction_slots"]) == previous_slots + curve_growth, "starting headroom does not suppress population-driven slot growth")
		break
	world.reset()
	world.player_country = "GER"
	var sid := str(int(world.countries["GER"]["capital"]))
	var region: Dictionary = world.regions[sid]
	world.countries["GER"]["starting_stats"]["treasury_usd"] = 1e12
	check(world.construction.add(sid,"offices"), "queue staffed building")
	var job: Dictionary = world.construction.queue[0]
	job["progress"] = float(job["points"]) - .0001
	world.construction.advance_days(1)
	check(world.construction.queue.is_empty(), "construction completes with available staffed industry")
	check(region["construction_output"].has("offices") and model.gdp_output(sid) > 0, "completed building has staffing-scaled output")
	var original_workforce: Dictionary = {}
	for id: String in world.regions:
		if world.regions[id]["owner"] == "GER":
			original_workforce[id] = world.regions[id]["workforce"].duplicate()
			world.regions[id]["workforce"]["participation_rate"] = 0
	model.refresh()
	check(world.construction.add(sid,"industrial_complex"), "queue may wait for employees")
	job = world.construction.queue[0]
	check(world.construction.rate(job,10) == 0, "unstaffed industry supplies no construction work")
	world.construction.advance_days(1)
	check(job["progress"] == 0 and model.gdp_output(sid) == 0, "unstaffed new buildings generate no output")
	for id: String in original_workforce: world.regions[id]["workforce"] = original_workforce[id]
	model.refresh()
	check(world.construction.rate(job,10) > 0 and model.gdp_output(sid) > 0, "staffing restores operational output")
	var directory := OS.get_environment("TEMP").path_join("bunnyworld-economy-qa")
	DirAccess.make_dir_recursive_absolute(directory)
	var path := directory.path_join("staffing.bws")
	var view := {"rotation":[0,0],"distance":2.,"map_mode":0,"organization":"EU","show_regions":false,"inspection_active":false,"relations_reverse":false}
	var expected_output := model.gdp_output(sid)
	var expected_workers: Dictionary = model.states[sid].duplicate(true)
	check(world.save_game(path,view), "save workforce and output inputs")
	world.reset()
	check(not world.load_game(path).is_empty(), "load staffing: " + world.last_error)
	check(model.states[sid] == expected_workers and is_equal_approx(model.gdp_output(sid),expected_output), "staffing and output rebuild from saved inputs")
	var envelope: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(path))
	var payload: Dictionary = JSON.parse_string(envelope["payload"])
	payload["regions"][sid]["construction_output"]["offices"] = -1
	var body := JSON.stringify(payload)
	var bad := directory.path_join("invalid-staffing.bws")
	var file := FileAccess.open(bad,FileAccess.WRITE)
	file.store_string(JSON.stringify({"format":"BunnyWorldSave","payload":body,"checksum":body.sha256_text()}));file.close()
	check(world.load_game(bad).is_empty() and model.states[sid] == expected_workers, "invalid output save rejected atomically")
	print("STATE_ECONOMY_MODEL checks=",checks," failures=",failures," expanded_states=",expanded)
	quit(0 if failures==0 else 1)
