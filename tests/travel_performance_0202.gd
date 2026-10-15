extends SceneTree
func _initialize() -> void: run.call_deferred()
func run() -> void:
	var main = load("res://main.tscn").instantiate()
	root.add_child(main)
	while not main.boot_complete: await process_frame
	main._start_selection();main._begin_campaign();main._map_changed(6);main.distance=1.04
	var mesh_id: int = main.detail_patch.mesh.get_instance_id()
	var texture_id: int = main.resident_terrain.texture.get_instance_id()
	var builds: int = main.urban_scenery.mesh_builds
	var samples: Array[float] = []
	var fixtures := [Vector2(139.75,35.66),Vector2(121.5,31.2),Vector2(29,41),Vector2(14,37.5),Vector2(2.3,48.9),Vector2(-112,33.5),Vector2(87,28),Vector2(0,-80)]
	for step: int in 80:
		var city: Vector2 = fixtures[step % fixtures.size()]
		var before := Time.get_ticks_usec()
		main.planet.rotation=Vector3(deg_to_rad(city.y),-deg_to_rad(city.x),0)
		main._update_camera_pose();main._update_detail_patch()
		await process_frame
		await process_frame
		if step>=8:samples.append(float(Time.get_ticks_usec()-before)/2000.0)
		if main.detail_patch.mesh.get_instance_id()!=mesh_id or main.resident_terrain.texture.get_instance_id()!=texture_id or main.urban_scenery.mesh_builds!=builds:
			printerr("TRAVEL_RESOURCE_REBUILT");quit(1);return
	samples.sort()
	print("TRAVEL_0202_PASS layers=",main.resident_terrain.texture.get_layers()," texture_width=",main.resident_terrain.texture.get_width()," immutable_meshes=true whole_frame_two_frame_average_ms median=",samples[samples.size()/2]," p95=",samples[int(samples.size()*.95)]," maximum=",samples.back()," environment=Linux_Mesa_software_not_Windows_FPS")
	quit()
