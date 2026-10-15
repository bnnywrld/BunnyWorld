extends SceneTree
const State = preload("res://scripts/world_state.gd")
const Demo = preload("res://scripts/demography.gd")
var failed := false
func check(value: bool, name: String) -> void:
	print(("PASS " if value else "FAIL ") + name)
	if not value: failed = true
func _initialize() -> void:
	var state := State.new()
	state.initialize(JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json")))
	var demo := Demo.new()
	var total := 0
	for sid: String in state.regions:
		var entry := demo.state_metrics(state,int(sid))
		total += int(entry["population"])
		for key: String in entry["metrics"]:
			var sum := 0
			for count: Variant in entry["metrics"][key]["counts"].values():sum += int(count)
			if sum != int(entry["metrics"][key]["denominator"]): check(false,"category accounting "+sid+" "+key)
	check(total == 6144737528,"all State populations preserved")
	var japan := demo.country_metrics(state,"JAP")
	check(int(japan["population"]) == 126806606,"Japan total preserved")
	check(int(japan["urban"])+int(japan["shared"]) == int(japan["population"]),"city areas + remainder pools counted once")
	check(japan["metrics"]["age"]["counts"].keys().size() == 3,"three age groups")
	check(int(japan["metrics"]["age"]["counts"]["Retired"]) > 0,"retirement-age residents represented")
	check(is_equal_approx(float(state.countries["JAP"]["starting_stats"]["treasury_usd"]),528e9),"Japan named-variable Treasury imported in USD")
	check(is_equal_approx(float(state.countries["JAP"]["starting_stats"]["debt_usd"]),4267.287e9),"Japan named-variable Debt imported in USD")
	check(is_equal_approx(float(state.countries["JAP"]["starting_stats"]["gdp_per_capita_usd"]),36323),"GDP-per-capita units verified")
	var state_id := int(state.country_metrics("JAP")["regions"][0])
	var before := demo.state_metrics(state,state_id)
	state.countries["JAP"]["starting_stats"]["retirement_age"] = 70
	var after := demo.state_metrics(state,state_id)
	check(int(after["population"]) == int(before["population"]) and int(after["metrics"]["age"]["counts"]["Retired"]) < int(before["metrics"]["age"]["counts"]["Retired"]),"retirement threshold reclassifies without population growth")
	var polish_before: int = demo.country_metrics(state,"POL")["population"]
	var residents: int = state.regions[str(state_id)]["population"]
	state.transfer_region(state_id,"POL")
	check(int(demo.country_metrics(state,"POL")["population"]) == polish_before+residents,"ownership transfer aggregates resident profiles")
	check(Demo.allocate(7,{"A":.33,"B":.33,"C":.34}).values().reduce(func(a:int,b:int):return a+b,0) == 7,"whole-person largest remainder")
	state.world_tension = 12.0
	state.tension_events = [{"date":"1 January 2000","description":"Test record","increase":12}]
	var view := {"rotation":[0,0],"distance":3.2,"map_mode":0,"show_regions":false,"organization":"EU","inspection_active":false,"relations_reverse":false}
	check(state.save_game("user://foundation_test.json",view),"same-version save")
	state.reset()
	check(not state.load_game("user://foundation_test.json").is_empty(),"same-version load")
	check(state.world_tension == 12 and state.tension_events.size() == 1,"tension and history persisted")
	check(is_equal_approx(float(state.countries["JAP"]["starting_stats"]["treasury_usd"]),528e9),"starting finances persisted")
	quit(1 if failed else 0)
