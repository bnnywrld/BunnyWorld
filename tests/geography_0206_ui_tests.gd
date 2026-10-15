extends SceneTree
var failures := 0
var checks: Array[String] = []
func _initialize() -> void: run.call_deferred()
func check(value: bool, name: String) -> void:
	checks.append(("PASS " if value else "FAIL ")+name)
	print(checks[-1])
	if not value:failures+=1
func settle() -> void:
	for i: int in 3:await process_frame
func run() -> void:
	var main=load("res://main.tscn").instantiate()
	root.add_child(main)
	while not main.boot_complete:await process_frame
	check(str(ProjectSettings.get_setting("application/config/version"))=="0.2.0.6","application version")
	check(main.state.countries.size()==223,"223 countries load")
	main._start_selection();main._show_country("POL",false);main._begin_campaign();await settle()
	check(main.screen=="playing" and main.state.player_country=="POL","fresh campaign starts")
	main._map_changed(0);main.show_regions=true
	for tag: String in ["POL","GER","USA","ENG","FRA","ITA","BEL","SWI","EGY","NGR","SAU","SOV","RAJ","CHI","IND","JAP","GRN","HLS"]:
		var sid: int=int(main.state.countries[tag]["capital"])
		var province: int=int(main.state.regions[str(sid)]["provinces"][0])
		main.inspect_region=sid;main.inspect_province=province;main._show_country(tag,false);await settle()
		check(main.state.selected_region==sid and main.territory_clip.visible,"inspect new State "+tag)
		check(main.state.province_owner(province)==tag,"province owner follows new State "+tag)
		var record: Dictionary=main.state.regions[str(sid)]
		var point: Array=record["map_center"]
		if main.focus_tween!=null:main.focus_tween.kill()
		main.planet.rotation=Vector3(deg_to_rad(90-float(point[1])*180),-deg_to_rad(float(point[0])*360-180),0)
		main.distance=1.2;main._update_camera_pose();main._update_detail_patch();await settle()
		var hit: int=main._region_at(Vector2(main.world_view.size)*.5)
		check(hit==sid,"globe State picking agrees with new map "+tag)
	main.inspect_region=int(main.state.countries["POL"]["capital"])
	main.inspect_province=int(main.state.regions[str(main.inspect_region)]["provinces"][0])
	main._show_country("POL",false);main.territory_handle.pressed.emit();await create_timer(.3).timeout
	check(main.territory_collapsed and main.territory_handle.visible,"territory drawer still collapses")
	for query: String in ["Warsaw","Tokyo","London","California","Bavaria","Greenland"]:
		check(not main.places.find_places(query).is_empty(),"search new catalog "+query)
	var view: Dictionary=main._view_state() if main.has_method("_view_state") else {"rotation":[0,0],"distance":1.2,"map_mode":0,"organization":"EU","show_regions":true,"inspection_active":false,"relations_reverse":false}
	check(main.state.save_game("user://tests/geography_0206.json",view),"new geography save")
	check(not main.state.load_game("user://tests/geography_0206.json").is_empty(),"new geography load")
	var path:=OS.get_environment("BUNNY_VALIDATION_DIR")
	if not path.is_empty():
		var f:=FileAccess.open(path.path_join("integration_results.json"),FileAccess.WRITE)
		f.store_string(JSON.stringify({"checks":checks,"failures":failures},"\t"))
	print("GEOGRAPHY_UI_COMPLETE checks=",checks.size()," failures=",failures)
	main.queue_free();await process_frame;quit(1 if failures else 0)
