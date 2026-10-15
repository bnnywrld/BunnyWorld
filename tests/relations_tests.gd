extends SceneTree
func _initialize() -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json"))
	var state := WorldState.new()
	state.initialize(data)
	assert(state.opinion("CHI", "JAP") == -40)
	assert(state.opinion("JAP", "CHI") == -20)
	assert(state.opinion("JAP", "CAN") == 20)
	assert(state.opinion("JAP", "POL") == 0)
	var definitions: Dictionary = state.relation_database["definitions"]
	definitions["TEST_DECAY"] = {"name":"Test", "value":20.0,"decay_per_month":2.0,"expires_hour":-1.0,"trade_only":false}
	definitions["TEST_TRADE"] = {"name":"Trade", "value":100.0,"decay_per_month":0.0,"expires_hour":-1.0,"trade_only":true}
	definitions["TEST_EXPIRY"] = {"name":"Expiry", "value":5.0,"decay_per_month":0.0,"expires_hour":24.0,"trade_only":false}
	state.relation_database["pairs"]["JAP|POL"] = ["TEST_DECAY", "TEST_TRADE", "TEST_EXPIRY"]
	assert(state.opinion("JAP", "POL") == 25.0)
	state.hour = 24
	assert(state.opinion("JAP", "POL") < 20.0)
	state.hour = 1461 # Two mean months.
	assert(is_equal_approx(state.opinion("JAP", "POL"), 16.0))
	assert(state.set_opinion("JAP", "POL", -70.0))
	assert(is_equal_approx(state.opinion("JAP", "POL"), -70.0))
	assert(state.opinion("POL", "JAP") != -70.0)
	assert(not state.set_opinion("JAP", "JAP", 20))
	print("RELATIONS_TESTS_PASS: known mod values, direction, trade exclusion, expiry, monthly decay, console offset")
	quit(0)
