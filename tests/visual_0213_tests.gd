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
	check(str(ProjectSettings.get_setting("application/config/version"))=="0.2.0.13","application version")
	check(main.state.countries.size()==223,"223 countries load")
	main._start_selection();main._show_country("POL",false);main._begin_campaign();await settle()
	check(main.screen=="playing" and main.state.player_country=="POL","fresh campaign starts")
	main._map_changed(0);main.show_regions=true;main.distance=1.2;main._update_camera_pose()
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
	var scroll: ScrollContainer=main.control_details.get_parent()
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
	main.national_profile_expanded=false;main._show_country("POL",false);await create_timer(.3).timeout
	var summary: GridContainer=main.control_details.get_node("CountrySummary")
	check(summary.columns==2 and summary.get_child_count()==6,"six national summary cards in two columns")
	var chart=main.control_details.get_node("NationalDemographics")
	check(not chart.visible and summary.get_index()<chart.get_index(),"national chart starts collapsed below summary")
	main.control_details.get_node("NationalProfileToggle").set_pressed_no_signal(true);main.control_details.get_node("NationalProfileToggle").pressed.emit();await settle()
	check(chart.visible and main.national_profile_expanded,"profile disclosure opens chart")
	for metric: String in ["age","religion","education","activity"]:
		chart.selectors.get_node(metric).pressed.emit();check(chart.selected==metric,"national demographic switch "+metric)
	main.national_profile_expanded=false;main.foundation.open_country_demographics();await settle()
	check(main.control_details.get_node("NationalDemographics").visible,"toolbar shortcut expands national profile")
	check(main.country_label_layer.preparation_runs==1 and main.country_label_layer.entries.size()>150,"country labels prepare once for substantial countries")
	main.country_labels_enabled=true
	var reads: int=main.country_label_layer.preparation_reads
	for tag: String in ["USA","GER","FRA","JAP"]:
		main._close_panels();main._focus_country(tag,false);main.distance=2.0 if tag!="USA" else 2.4;main._update_camera_pose();await settle();main.country_label_layer.update_view(true)
		var shown: Array=main.country_label_layer.visible_labels.map(func(e:Dictionary):return e["tag"])
		check(tag in shown,"major country name visible "+tag+": "+str(shown))
	for i: int in 8:main.planet.rotation.y+=.03;main.country_label_layer.update_view(true)
	check(main.country_label_layer.preparation_reads==reads and main.country_label_layer.preparation_runs==1,"camera movement does not read geography or rebuild labels")
	main._toggle_country_labels();check(main.country_label_layer.visible_labels.is_empty(),"Aa toggle hides names")
	main._toggle_country_labels();await settle();check(not main.country_label_layer.visible_labels.is_empty(),"Aa toggle restores names")
	main.distance=1.1;main._update_camera_pose();main.country_label_layer.update_view(true);check(main.country_label_layer.visible_labels.is_empty(),"country names fade out at province zoom")
	main.distance=1.5;main._update_camera_pose();await settle()
	for material: ShaderMaterial in main.border_materials:check(is_equal_approx(float(material.get_shader_parameter("camera_distance")),1.5),"border zoom uniform follows camera")
	check(main.country_label_layer.mouse_filter==Control.MOUSE_FILTER_IGNORE,"labels do not intercept map input")
	var labels=main.country_label_layer
	check(labels.geometry_builds==1 and labels.label_mesh.mesh.get_surface_count()==1,"country glyphs prepared as one mesh")
	var sizes: Array=labels.entries.map(func(e:Dictionary):return e["world_height"])
	var builds: int=labels.geometry_builds
	var uploads: int=main.display_coverage.upload_count
	for zoom: float in [3.0,2.5,2.0,1.5,1.25]:
		main.distance=zoom;main._update_camera_pose();labels.update_view(true);await settle()
	check(sizes==labels.entries.map(func(e:Dictionary):return e["world_height"]),"world-space name sizes unchanged through zoom")
	check(labels.geometry_builds==builds,"zoom never rebuilds text geometry")
	check(main.display_coverage.upload_count==uploads,"camera movement never uploads selection coverage")
	main._close_panels();main.inspect_region=int(main.state.countries["JAP"]["capital"]);main.inspect_province=int(main.state.regions[str(main.inspect_region)]["provinces"][0]);main.distance=1.12;main._update_camera_pose();main._show_country("JAP",false);await create_timer(.3).timeout
	check(bool(main.planet_material.get_shader_parameter("state_coverage_enabled")),"selected State has prepared smooth coverage")
	check(bool(main.planet_material.get_shader_parameter("province_coverage_enabled")),"selected province has prepared smooth coverage")
	check(main.territory_heading.has_node("SelectionBreadcrumb"),"territory selection breadcrumb present")
	var pinned: Control=main.diplomatic_heading
	var pinned_before: Vector2=pinned.global_position
	main.diplomatic_details.get_parent().scroll_vertical=200;await settle()
	check(pinned.global_position.is_equal_approx(pinned_before),"country flag and heading stay pinned while scrolling")
	check(main.header_flag.get_parent()==main.command_stack.get_parent(),"larger flag shares command frame with stats and toolbar")
	check(main.stats_row.get_parent()==main.navigation_row.get_parent(),"stats and category buttons share two-row stack")
	check(main.stats_row.global_position.y<main.navigation_row.global_position.y,"stats above category buttons")
	main.territory_heading.get_node("SelectionBreadcrumb").get_child(2).pressed.emit();await settle()
	check(main.state.selected_province==0 and main.state.selected_region>0,"State breadcrumb exits province inspection")
	main.territory_heading.get_node("SelectionBreadcrumb").get_child(0).pressed.emit();await settle()
	check(main.state.selected_region==0,"country breadcrumb exits State inspection")
	main.foundation.open_country_demographics();await settle()
	check(main.foundation.demographic_button.button_pressed,"demographic shortcut shows active state")
	main.control_details.get_node("NationalProfileToggle").set_pressed_no_signal(false);main.control_details.get_node("NationalProfileToggle").pressed.emit();await settle()
	check(not main.foundation.demographic_button.button_pressed,"collapsing profile clears active shortcut")
	var changed_state: int=int(main.state.countries["POL"]["capital"])
	var prior_builds: int=labels.geometry_builds
	main.state.transfer_region(changed_state,"GER");main._rebuild_palette()
	check(labels.geometry_builds==prior_builds+1,"ownership change refreshes fixed name geometry")
	main.state.transfer_region(changed_state,"POL");main._rebuild_palette()
	check(labels.geometry_builds==prior_builds+2,"restored ownership refreshes names once")
	for query: String in ["Warsaw","Tokyo","London","California","Bavaria","Greenland"]:
		check(not main.places.find_places(query).is_empty(),"search new catalog "+query)
	var view: Dictionary=main._view_state() if main.has_method("_view_state") else {"rotation":[0,0],"distance":1.2,"map_mode":0,"organization":"EU","show_regions":true,"inspection_active":false,"relations_reverse":false}
	check(main.state.save_game("user://tests/visual_0213.json",view),"new geography save")
	check(not main.state.load_game("user://tests/visual_0213.json").is_empty(),"new geography load")
	var path:=OS.get_environment("BUNNY_VALIDATION_DIR")
	if not path.is_empty():
		var f:=FileAccess.open(path.path_join("integration_results.json"),FileAccess.WRITE)
		f.store_string(JSON.stringify({"checks":checks,"failures":failures},"\t"))
	print("GEOGRAPHY_UI_COMPLETE checks=",checks.size()," failures=",failures)
	if OS.get_environment("BUNNY_VISUAL_SHOTS")=="1":
		main._close_panels();main.state.player_country="JAP";main._map_changed(6)
		if main.focus_tween!=null:main.focus_tween.kill()
		main.planet.rotation=Vector3(deg_to_rad(35.686963),-deg_to_rad(139.749462),0)
		main.distance=1.035;main._update_camera_pose();main._update_detail_patch();await settle()
		var coast_point: Vector2=Vector2(main.world_view.size)*.5
		main.inspect_region=main._region_at(coast_point);main.inspect_province=main._province_at(coast_point);main._show_country("JAP",false)
		await create_timer(.3).timeout;await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png(OS.get_environment("BUNNY_VALIDATION_DIR").path_join("tokyo_final.png"))
	main.queue_free();await process_frame;quit(1 if failures else 0)

func wheel(point: Vector2, button: int) -> void:
	var event:=InputEventMouseButton.new()
	event.position=point;event.global_position=point;event.button_index=button;event.pressed=true
	root.push_input(event,true)
	await settle()
