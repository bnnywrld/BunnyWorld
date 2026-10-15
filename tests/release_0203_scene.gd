extends SceneTree
var failures := 0
func check(ok: bool, description: String) -> void:
	if not ok: failures += 1; printerr("FAIL: ",description)
func _initialize() -> void: run.call_deferred()
func capture(main, name: String, point: Vector2, zoom: float, tooltip: bool=false) -> void:
	if main.focus_tween!=null: main.focus_tween.kill()
	main._map_changed(6);main.distance=zoom
	main.planet.rotation=Vector3(deg_to_rad(point.y),-deg_to_rad(point.x),0)
	main._update_camera_pose();main._update_detail_patch()
	for i: int in 8: await process_frame
	if tooltip:
		Input.warp_mouse(main.view_container.global_position+main.view_container.size*.5)
		main._update_map_hover(Vector2(main.world_view.size)*.5)
		await process_frame
	await RenderingServer.frame_post_draw
	var directory := OS.get_environment("BUNNY_VALIDATION_DIR")
	if directory.is_empty(): directory="user://validation_0203"
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(directory))
	var out := directory.path_join(name+"_final.png")
	check(main.get_viewport().get_texture().get_image().save_png(out)==OK,"capture "+name)
	main.hover_panel.hide()
func run() -> void:
	var main = load("res://main.tscn").instantiate()
	root.add_child(main)
	while not main.boot_complete: await process_frame
	check(str(ProjectSettings.get_setting("application/config/version"))=="0.2.0.3","embedded release identity")
	main._start_selection()
	check(main.map_mode==6 and main.map_picker.selected==6,"Start uses physical map")
	main._map_changed(0);main._begin_campaign()
	check(main.map_mode==6,"Play uses physical map")
	if main.focus_tween!=null: main.focus_tween.kill()
	main.planet.rotation=Vector3(deg_to_rad(35.686963),-deg_to_rad(139.749462),0);main.distance=1.04
	main._update_camera_pose();main._update_detail_patch()
	for i: int in 4: await process_frame
	var centre := Vector2(main.world_view.size)*.5
	main._update_map_hover(centre)
	check(main.hover_flag.visible and main.hover_flag.texture!=null and "Japan" in main.hover_text.text,"flag before country name")
	check(main.flags.hover_page.get_width()==2304,"compact tooltip atlas")
	var flag_id: int = main.hover_flag.texture.get_instance_id()
	for i: int in 8: main._update_map_hover(centre)
	check(main.hover_flag.texture.get_instance_id()==flag_id,"hover texture reused")
	check(main.resident_terrain.texture.get_width()==(2048 if main.graphics_setting==1 else 4096),"selected texture library")
	var mesh_id: int = main.detail_patch.mesh.get_instance_id()
	var texture_id: int = main.resident_terrain.texture.get_instance_id()
	var builds: int = main.urban_scenery.mesh_builds
	var samples: Array[float] = []
	var fixtures := [Vector2(139.75,35.66),Vector2(121.5,31.2),Vector2(29,41),Vector2(14,37.5),Vector2(2.3,48.9),Vector2(-112,33.5),Vector2(87,28),Vector2(0,-80)]
	for step: int in 80:
		var point: Vector2 = fixtures[step%fixtures.size()]
		var before := Time.get_ticks_usec()
		main.planet.rotation=Vector3(deg_to_rad(point.y),-deg_to_rad(point.x),0)
		main._update_camera_pose();main._update_detail_patch()
		await process_frame;await process_frame
		if step>=8:samples.append(float(Time.get_ticks_usec()-before)/2000.0)
		check(main.detail_patch.mesh.get_instance_id()==mesh_id and main.resident_terrain.texture.get_instance_id()==texture_id and main.urban_scenery.mesh_builds==builds,"immutable travel resources")
		check(main.urban_scenery.visible_buildings<=2048 and main.urban_scenery.active.size()<=96,"bounded scenery")
	samples.sort()
	print("FINAL_TRAVEL_0203 layers=8 width=",main.resident_terrain.texture.get_width()," median_ms=",samples[int(samples.size()*.5)]," p95_ms=",samples[int(samples.size()*.95)]," maximum_ms=",samples.back()," environment=Linux_Mesa_software_not_native_Windows_FPS")
	for passage: Dictionary in main.water_passages:
		var p: Array = passage["coordinates"][passage["coordinates"].size()/2]
		main.planet.rotation=Vector3(deg_to_rad(float(p[1])),-deg_to_rad(float(p[0])),0);main.distance=1.015
		main._update_camera_pose()
		check(main._region_at(centre)==0,"passage remains selectable water")
		check(main._sea_at(centre)==int(passage["ends"][0]),"passage sea ID")
	await capture(main,"nile",Vector2(31.2,29.8),1.025)
	await capture(main,"aland",Vector2(20.3,60.2),1.025)
	await capture(main,"hongkong",Vector2(114.17,22.30),1.025,true)
	if failures:
		quit(1);return
	print("RELEASE_0203_SCENE_PASS: version, physical defaults, compact cached flags, immutable travel resources, caps, passage picking and captures")
	main._enter_menu()
	await main._run_smoke_test()
