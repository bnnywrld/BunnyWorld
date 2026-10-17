extends SceneTree
# Focused old/new shader comparison in one process, with identical resources
# and fixed glow phase. Timings remain software-renderer diagnostics, not GPU FPS.
func _initialize() -> void: run.call_deferred()
func frame() -> void:
	await process_frame
	await RenderingServer.frame_post_draw
func run() -> void:
	DirAccess.make_dir_recursive_absolute("res://validation_0222/shader")
	var main = load("res://scripts/main.gd").new()
	main.state.initialize(JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json")))
	main.world_view = SubViewport.new()
	main.world_view.size = Vector2i(640,400)
	main.world_view.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	root.add_child(main.world_view)
	main.relief_surface = load("res://scripts/relief_surface.gd").new()
	main.legend = Label.new()
	main.screen = "playing"
	main._build_planet()
	var shaders: Array[Shader] = []
	for path: String in ["res://validation_0222/reference_planet_0221.gdshader", "res://scripts/planet.gdshader"]:
		var shader := Shader.new()
		shader.code = FileAccess.get_file_as_string(path).replace("sin(TIME*1.7)","sin(0.0)")
		shaders.append(shader)
	var cases: Array = []
	for row: Array in [[6,40.0,85.0,2.4,"asia_far_physical"],[6,30.0,20.0,3.5,"globe_far_physical"],[6,46.0,7.5,1.025,"alps_close_physical"],[0,53.9,27.5,1.5,"europe_political"]]:
		main.map_mode = row[0]
		main.distance = row[3]
		main.planet.rotation = Vector3(deg_to_rad(row[1]),-deg_to_rad(row[2]),0)
		main._update_camera_pose();main._update_detail_patch();main._rebuild_palette()
		main.planet_material.set_shader_parameter("terrain_mix",clampf((2.0-main.distance)/.35,0,1) if main.map_mode==6 else 0.0)
		main.planet_material.set_shader_parameter("city_detail",clampf((1.5-main.distance)/.25,0,1))
		main.planet_material.set_shader_parameter("camera_distance",main.distance)
		var parameters: Dictionary = {}
		for parameter: Dictionary in main.planet_material.shader.get_shader_uniform_list():
			parameters[parameter["name"]] = main.planet_material.get_shader_parameter(parameter["name"])
		var times: Array = [[],[]]
		for pass_id: int in [0,1,1,0]:
			main.planet_material.shader = shaders[pass_id]
			for key: String in parameters: main.planet_material.set_shader_parameter(key,parameters[key])
			for warm: int in 4: await frame()
			main.world_view.get_texture().get_image().save_png("res://validation_0222/shader/%s_%d.png" % [row[4],pass_id])
			for i: int in 8:
				var start := Time.get_ticks_usec()
				await frame()
				times[pass_id].append(float(Time.get_ticks_usec()-start)/1000.0)
		for values: Array in times: values.sort()
		cases.append({"case":row[4],"old_median_ms":times[0][8],"new_median_ms":times[1][8],"samples_each":16})
		print("SHADER_COMPARISON ",JSON.stringify(cases[-1]))
	var file := FileAccess.open("res://validation_0222/shader/results.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"scope":"Interleaved A/B/B/A, fixed resources and glow, Linux software renderer; not target GPU timings","adapter":RenderingServer.get_video_adapter_name(),"cases":cases},"\t"))
	main.world_view.queue_free();main.legend.free();main.free()
	await process_frame
	quit()
