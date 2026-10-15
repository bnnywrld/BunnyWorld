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
	check(str(ProjectSettings.get_setting("application/config/version"))=="0.2.0.10","application version")
	check(main.state.countries.size()==223,"223 countries load")
	main._start_selection();main._show_country("POL",false);main._begin_campaign();await settle()
	check(main.screen=="playing" and main.state.player_country=="POL","fresh campaign starts")
	main._map_changed(0);main.show_regions=true
	for tag: String in ["POL","GER","USA","ENG","FRA","ITA","BEL","SWI","EGY","NGR","SAU","SOV","RAJ","CHI","IND","JAP","GRN","HLS","AFG","SYR","CRO","URG","PMR","UKR","SOL","PHI","AUS","SWE","FIN","VEN","GEO"]:
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
	# Exercise actual GUI dispatch, including a scrollable child and blank panel.
	main._close_panels();main.inspect_region=0;main.inspect_province=0
	main._show_country("POL",false);await create_timer(.3).timeout
	var initial_distance: float=main.distance
	var point: Vector2=main.control_panel.get_global_rect().get_center()
	await wheel(point,MOUSE_BUTTON_WHEEL_DOWN)
	check(is_equal_approx(main.distance,initial_distance),"wheel over own-country panel does not zoom")
	var scroll: ScrollContainer=main.control_panel.get_child(0)
	scroll.scroll_vertical=0;await settle()
	point=scroll.get_global_rect().get_center()
	await wheel(point,MOUSE_BUTTON_WHEEL_DOWN)
	check(is_equal_approx(main.distance,initial_distance),"wheel over scroll content does not zoom")
	check(scroll.get_v_scroll_bar().max_value<=scroll.get_v_scroll_bar().page or scroll.scroll_vertical>0,"panel content still scrolls")
	main._show_country("JAP",false);await create_timer(.3).timeout
	point=main.right_panel.get_global_rect().get_center();initial_distance=main.distance
	await wheel(point,MOUSE_BUTTON_WHEEL_UP)
	check(is_equal_approx(main.distance,initial_distance),"wheel over diplomacy panel does not zoom")
	var sid: int=int(main.state.countries["JAP"]["capital"])
	main.inspect_region=sid;main.inspect_province=int(main.state.regions[str(sid)]["provinces"][0]);main._show_country("JAP",false)
	main.territory_collapsed=false;main._position_panels();await create_timer(.3).timeout
	point=main.territory_panel.get_global_rect().intersection(main.territory_clip.get_global_rect()).get_center();initial_distance=main.distance
	await wheel(point,MOUSE_BUTTON_WHEEL_UP)
	check(is_equal_approx(main.distance,initial_distance),"wheel over territory drawer does not zoom")
	for panel: Control in [main.control_panel,main.right_panel,main.territory_panel,main.clock_box,main.map_box]:
		check(not panel.mouse_force_pass_scroll_events,"panel terminates forced wheel propagation "+str(panel.name))
	var drag:=InputEventMouseMotion.new();drag.position=point-main.view_container.global_position;drag.relative=Vector2(50,20);drag.button_mask=MOUSE_BUTTON_MASK_RIGHT
	main.dragging=true;main.rotation_velocity=Vector2.ONE
	var angle: Vector3=main.planet.rotation
	main._globe_input(drag)
	check(main.planet.rotation.is_equal_approx(angle) and not main.dragging and main.rotation_velocity==Vector2.ZERO,"drag entering UI stops camera movement")
	main._close_panels();await settle();main.distance=2.0;main._update_camera_pose()
	point=main.view_container.get_global_rect().get_center()
	check(not main._ui_blocks_globe(point-main.view_container.global_position),"uncovered globe remains interactive")
	await wheel(point,MOUSE_BUTTON_WHEEL_UP)
	check(main.distance<2.0,"wheel over exposed map still zooms")
	await wheel(main.map_box.get_global_rect().get_center(),MOUSE_BUTTON_WHEEL_UP)
	var after_distance: float=main.distance
	await wheel(main.clock_box.get_global_rect().get_center(),MOUSE_BUTTON_WHEEL_UP)
	check(is_equal_approx(main.distance,after_distance),"wheel over top controls does not zoom")
	# State owners and actual palette bytes agree around the Åland transfer.
	var owners: Image=main.owners_texture.get_image()
	for row: Dictionary in main.state.regions.values():
		if row["owner"] not in ["SWE","FIN"]:continue
		var color: Color=owners.get_pixel(int(row["id"]),0)
		var index: int=int(round(color.r*255))+256*int(round(color.g*255))
		check(index==int(main.state.countries[row["owner"]]["index"]),"border owner palette "+str(row["name"]))
	for query: String in ["Warsaw","Tokyo","London","California","Bavaria","Greenland"]:
		check(not main.places.find_places(query).is_empty(),"search new catalog "+query)
	var view: Dictionary=main._view_state() if main.has_method("_view_state") else {"rotation":[0,0],"distance":1.2,"map_mode":0,"organization":"EU","show_regions":true,"inspection_active":false,"relations_reverse":false}
	check(main.state.save_game("user://tests/geography_0210.json",view),"new geography save")
	check(not main.state.load_game("user://tests/geography_0210.json").is_empty(),"new geography load")
	var path:=OS.get_environment("BUNNY_VALIDATION_DIR")
	if not path.is_empty():
		var f:=FileAccess.open(path.path_join("integration_results.json"),FileAccess.WRITE)
		f.store_string(JSON.stringify({"checks":checks,"failures":failures},"\t"))
	print("GEOGRAPHY_UI_COMPLETE checks=",checks.size()," failures=",failures)
	main.queue_free();await process_frame;quit(1 if failures else 0)

func wheel(point: Vector2, button: int) -> void:
	var event:=InputEventMouseButton.new()
	event.position=point;event.global_position=point;event.button_index=button;event.pressed=true
	root.push_input(event,true)
	await settle()
