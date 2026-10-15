extends SceneTree
func _initialize() -> void: run.call_deferred()
func run() -> void:
	var main = load("res://main.tscn").instantiate()
	root.add_child(main)
	if main.has_method("_loading_stage"):
		while not main.boot_complete: await process_frame
	else: await create_timer(.5).timeout
	main._start_selection()
	main._begin_campaign()
	main._map_changed(6)
	main.set_process(false)
	main.distance=1.025
	var times: Array[float] = []
	for point: Vector2 in [Vector2(139.75,35.66),Vector2(121.5,31.2),Vector2(29,41),Vector2(14,37.5),Vector2(2.3,48.9),Vector2(121.5,31.2),Vector2(29,41),Vector2(139.75,35.66)]:
		main.planet.rotation=Vector3(deg_to_rad(point.y),-deg_to_rad(point.x),0)
		var started := Time.get_ticks_usec()
		main._update_camera_pose()
		main._update_detail_patch()
		times.append(float(Time.get_ticks_usec()-started)/1000.0)
		await process_frame
	times.sort()
	print("CAMERA_PATCH_BENCHMARK version=",ProjectSettings.get_setting("application/config/version")," median_ms=",times[4]," max_ms=",times[-1]," samples=",times)
	main.queue_free()
	await process_frame
	quit()
