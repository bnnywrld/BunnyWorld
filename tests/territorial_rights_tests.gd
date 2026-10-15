extends SceneTree
const State = preload("res://scripts/world_state.gd")
const Palette = preload("res://scripts/map_palette.gd")
var failures := 0
func check(condition: bool, message: String) -> void:
	if not condition: failures += 1; printerr("FAIL: ", message)
func _initialize() -> void:
	var db: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json"))
	var state := State.new(); state.initialize(db)
	var id := int(state.countries["USA"]["capital"])
	var cores: Array = state.regions[str(id)]["cores"].duplicate()
	var claims: Array = state.regions[str(id)]["claims"].duplicate()
	check(state.transfer_region(id,"CAN"),"transfer available")
	check(state.regions[str(id)]["cores"]==cores and state.regions[str(id)]["claims"]==claims,"ownership does not rewrite territorial rights")
	check(not state.country_record("CAL").is_empty(),"dormant core country exists")
	state.selected_sea=237
	var view := {"rotation":[0,0],"distance":1.5,"map_mode":6,"organization":"EU","show_regions":true,"inspection_active":false,"relations_reverse":false}
	var path := "user://tests/rights_roundtrip.json"
	check(state.save_game(path,view),"save rights and water selection")
	state.reset();check(not state.load_game(path).is_empty(),"load rights")
	check(state.selected_sea==237 and state.regions[str(id)]["cores"]==cores and state.regions[str(id)]["owner"]=="CAN","water and unchanged rights persist")
	var envelope: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(path))
	var payload: Dictionary = JSON.parse_string(envelope["payload"])
	payload["regions"][str(id)]["cores"]=["UNKNOWN"]
	var body := JSON.stringify(payload)
	var file := FileAccess.open("user://tests/invalid_rights.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"format":"BunnyWorldSave","payload":body,"checksum":body.sha256_text()}));file.close()
	check(state.load_game("user://tests/invalid_rights.json").is_empty(),"invalid claimant rejected")
	check(state.regions[str(id)]["cores"]==cores,"failed load keeps existing rights")
	check(Palette.relation(0).is_equal_approx(Color("f6d94d")),"neutral is yellow")
	check(Palette.relation(-100).r>Palette.relation(-100).g*2,"minus 100 visibly red")
	check(Palette.relation(-200).get_luminance()<Palette.relation(-100).get_luminance(),"minus 200 darker")
	check(Palette.relation(100).g>Palette.relation(100).r*2,"plus 100 visibly green")
	check(Palette.relation(200).get_luminance()<Palette.relation(100).get_luminance(),"plus 200 darker")
	for capita: bool in [false,true]:
		var previous := 2.0
		for value: float in ([100000000.0,1000000000.0,10000000000.0,100000000000.0,1000000000000.0,10000000000000.0] if not capita else [100.0,1000.0,10000.0,30000.0,50000.0,100000.0]):
			var color := Palette.economic(value,capita)
			check(color.r>=color.g and color.g>=color.b,"economic hue remains amber")
			check(color.get_luminance()<previous,"higher economic value gets darker");previous=color.get_luminance()
	if failures==0: print("TERRITORIAL_RIGHTS_TESTS_PASS: rights independence/persistence, dormant identities, selected waters, rejected invalid saves, requested palette behavior")
	quit(failures)
