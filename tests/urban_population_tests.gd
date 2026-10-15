extends SceneTree
const State = preload("res://scripts/world_state.gd")
var failures := 0
func check(value: bool, message: String) -> void:
	if not value:
		failures += 1
		printerr("FAIL: ",message)
func _initialize() -> void:
	var world: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json"))
	var state := State.new()
	state.initialize(world)
	var total := 0
	for sid: String in state.regions:
		var allocation := state.population_allocation(int(sid))
		check(int(allocation["urban"]) + int(allocation["shared"]) == int(state.regions[sid]["population"]), "state conservation " + sid)
		var urban := 0
		for pid: String in allocation["provinces"]:
			check(int(allocation["provinces"][pid]) >= 0, "nonnegative urban population")
			urban += int(allocation["provinces"][pid])
		check(urban == int(allocation["total"]), "all province estimates sum to State " + sid)
		total += int(allocation["total"])
	check(total == 6144737528, "global conservation")
	for group: Dictionary in state.urban_database["groups"].values():
		check(state.urban_group_population(group["id"]) == int(group["population_2000"]), "initial group conservation " + str(group["name"]))
	var sample := 0
	for pid: String in state.provinces:
		if str(state.provinces[pid]["urban_group"]).is_empty():
			check(state.province_population(int(pid)) == int(state.provinces[pid]["population_2000"]), "rural province has individual estimate")
		else:
			check(state.province_population(int(pid)) == int(state.provinces[pid]["population_2000"]), "city includes whole province")
			sample = int(pid)
	var sid := str(int(state.provinces[str(sample)]["region"]))
	var original := int(state.regions[sid]["population"])
	for value: int in [0,1,7,original+123456,9999999999]:
		state.regions[sid]["population"] = value
		var allocation := state.population_allocation(int(sid))
		check(int(allocation["urban"]) + int(allocation["shared"]) == value, "debug changes keep pools consistent")
		check(int(allocation["shared"]) >= 0, "pool remains nonnegative")
	state.regions[sid]["population"] = original
	var group_id: String = state.provinces[str(sample)]["urban_group"]
	var before := state.urban_group_population(group_id)
	var owner: String = state.regions[sid]["owner"]
	var recipient := "POL" if owner != "POL" else "JAP"
	check(state.transfer_region(int(sid),recipient), "transfer succeeds")
	check(state.urban_group_population(group_id) == before, "city group keeps residents on transfer")
	var view := {"rotation":[0.1,0.2],"distance":1.05,"map_mode":6,"organization":"ASEAN","show_regions":true,"inspection_active":false,"relations_reverse":false}
	state.selected_province=sample;state.selected_region=int(sid)
	state.regions[sid]["population"] = original+999
	check(state.save_game("user://urban_test.bws",view), "new schema save")
	var saved_population := state.province_population(sample)
	state.reset()
	check(not state.load_game("user://urban_test.bws").is_empty(), "population-aware load")
	check(state.province_population(sample) == saved_population and int(state.regions[sid]["population"]) == original+999, "save/load preserves accounting after debug change")
	state.reset()
	check(state.urban_group_population(group_id) == before, "reset restores initial city population")
	if failures == 0: print("URBAN_POPULATION_TESTS_PASS: all states, groups, individual province estimates, zero/extreme changes, ownership, save/load, reset")
	quit(0 if failures == 0 else 1)
