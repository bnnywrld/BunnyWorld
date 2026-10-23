extends SceneTree
# Save the pre-change surface include outside the checkout, then run with:
# BUNNYWORLD_SHADER_BASELINE=<absolute include path>, BUNNYWORLD_QA_DIR=<external folder>.
# Compares actual GL viewport pixels with animation frozen only in test shaders.
# Alternating batches report uncapped wall-frame intervals and viewport GPU time.
var failures := 0
var game
var report: Array[Dictionary] = []
var output_dir: String
var baseline: Array[Shader] = []
var candidate: Array[Shader] = []

func _initialize() -> void: run.call_deferred()

func make_shader(source: String, physical: bool) -> Shader:
	var shader := Shader.new()
	var prefix := "shader_type spatial;\nrender_mode unshaded;\n"
	if physical: prefix += "#define PHYSICAL_MAP\n"
	shader.code = prefix + source.replace("TIME", "1.25")
	return shader

func use_shader(shader: Shader) -> void:
	var parameters: Dictionary = {}
	for parameter: Dictionary in game.planet_material.shader.get_shader_uniform_list():
		var value = game.planet_material.get_shader_parameter(parameter["name"])
		if value != null: parameters[parameter["name"]] = value
	game.planet_material.shader = shader
	for key: String in parameters:
		game.planet_material.set_shader_parameter(key, parameters[key])

func draw_frames(count: int) -> void:
	for i: int in count:
		await process_frame
		await RenderingServer.frame_post_draw

func capture(shader: Shader) -> Image:
	use_shader(shader)
	await draw_frames(4)
	return game.world_view.get_texture().get_image()

func compare_images(a: Image, b: Image) -> Dictionary:
	if a.get_size() != b.get_size() or a.get_format() != b.get_format():
		return {"equal":false, "error":"viewport image format or size differs"}
	var x := a.get_data()
	var y := b.get_data()
	var changed := 0
	var maximum := 0
	for i: int in x.size():
		var delta: int = absi(int(x[i]) - int(y[i]))
		if delta > 0: changed += 1
		maximum = maxi(maximum, delta)
	# Shader compiler rounding may move a few channels by one 8-bit level.
	# Reject larger differences or a change affecting over 0.01% of channels.
	return {"equal":maximum <= 1 and changed <= x.size() / 10000, "bit_identical":changed == 0, "changed_channels":changed, "max_channel_delta":maximum, "size":[a.get_width(),a.get_height()]}

func measure(shader: Shader) -> Dictionary:
	use_shader(shader)
	await draw_frames(8)
	var start := Time.get_ticks_usec()
	var gpu_ms := 0.0
	for i: int in 40:
		await draw_frames(1)
		gpu_ms += RenderingServer.viewport_get_measured_render_time_gpu(game.world_view.get_viewport_rid())
	return {"frame_ms":float(Time.get_ticks_usec() - start) / 40000.0,"gpu_ms":gpu_ms / 40.0}

func run() -> void:
	var baseline_path := OS.get_environment("BUNNYWORLD_SHADER_BASELINE")
	output_dir = OS.get_environment("BUNNYWORLD_QA_DIR")
	if baseline_path.is_empty() or output_dir.is_empty() or DisplayServer.get_name() == "headless":
		push_error("GL display and external baseline/QA paths are required")
		quit(2)
		return
	DirAccess.make_dir_recursive_absolute(output_dir)
	var old_source := FileAccess.get_file_as_string(baseline_path)
	var new_source := FileAccess.get_file_as_string("res://scripts/clean_globe_surface.gdshaderinc")
	if old_source.is_empty():
		quit(2)
		return
	for physical: bool in [false,true]:
		baseline.append(make_shader(old_source,physical))
		candidate.append(make_shader(new_source,physical))
	root.size = Vector2i(1440,900)
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = 0
	game = load("res://main.tscn").instantiate()
	root.add_child(game)
	while not game.boot_complete: await process_frame
	game._start_selection()
	game._show_country("POL",false)
	game._begin_campaign()
	game.state.paused = true
	game.rotation_velocity = Vector2.ZERO
	if game.focus_tween != null: game.focus_tween.kill()
	game.set_process(false)
	Engine.max_fps = 0
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	game.world_view.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	RenderingServer.viewport_set_measure_render_time(game.world_view.get_viewport_rid(),true)
	# Fields: name, longitude, latitude, distance, map mode, selection kind.
	var fixtures := [
		["political_globe",14.0,45.0,3.65,0,"country"],
		["information_globe",14.0,45.0,3.65,2,"country"],
		["physical_globe",14.0,45.0,3.65,6,"country"],
		["pacific",-145.0,0.0,1.5,0,"none"],
		["pacific_information",-145.0,0.0,1.5,4,"none"],
		["pacific_physical",-145.0,0.0,1.5,6,"sea"],
		["japan_coast",139.75,35.66,1.025,6,"country"],
		["mediterranean",14.0,37.5,1.08,6,"sea"],
		["sahara",10.0,24.0,1.08,6,"none"],
		["amazon",-60.0,-4.0,1.08,6,"none"],
		["himalayas",87.0,28.0,1.025,6,"none"],
		["arctic",25.0,70.0,1.1,6,"none"],
		["antarctica",0.0,-80.0,1.08,6,"none"],
		["tiny_islands",179.2,-8.5,1.04,0,"none"],
		["one_pixel_micronesia",154.3066406,8.1152344,1.025,0,"state"],
		["one_pixel_japan",123.7792969,24.0527344,1.025,6,"state"],
		["one_pixel_distant",145.9277344,43.4472656,1.5,0,"country"],
		["japan_hover",139.75,35.66,1.08,0,"hover"],
		["suez",32.3,30.0,1.015,0,"sea"],
		["bosporus",29.05,41.12,1.015,6,"sea"],
		["state_selection",19.0,52.0,1.15,0,"state"],
		["province_selection",19.0,52.0,1.04,6,"state"],
		["organizations",14.0,45.0,1.5,1,"country"],
		["construction",14.0,45.0,1.5,8,"country"]
	]
	for fixture: Array in fixtures:
		var mode: int = fixture[4]
		game._map_changed(0 if mode == 8 else mode)
		if mode == 8: game._show_feature("Construction")
		game.distance = float(fixture[3])
		game.planet.rotation = Vector3(deg_to_rad(float(fixture[2])), -deg_to_rad(float(fixture[1])),0)
		game._update_camera_pose()
		game._update_view_uniforms()
		game._close_panels()
		var uv := Vector2((float(fixture[1]) + 180.0) / 360.0, (90.0 - float(fixture[2])) / 180.0)
		var pixel: Color = game.map_rendering.pixel_at_uv(uv)
		var pid := int(round(pixel.r * 255.0)) + int(round(pixel.g * 255.0)) * 256
		var sid: int = int(game.state.provinces.get(str(pid),{}).get("region",game.state.countries["POL"]["regions"][0]))
		var tag: String = game.state.regions[str(sid)]["owner"]
		if fixture[5] == "country": game._show_country(tag,false)
		elif fixture[5] == "state":
			game.inspection_active = true
			game.state.selected_country = tag
			game.state.selected_region = sid
			game.state.selected_province = pid if game.state.provinces.has(str(pid)) else int(game.state.regions[str(sid)]["provinces"][0])
		elif fixture[5] == "sea":
			var sea: int = game._sea_at(Vector2(game.world_view.size) * .5)
			game._show_sea(sea if sea > 0 else int(game.state.sea_regions.keys()[0]))
		game._update_selection_shader()
		game.planet_material.set_shader_parameter("hovered_country",float(game.state.countries[tag]["index"]) if fixture[5] == "hover" else 0.0)
		game.planet_material.set_shader_parameter("hover_amount",1.0 if fixture[5] == "hover" else 0.0)
		if mode == 8:
			var flags := Image.create(8192,1,false,Image.FORMAT_R8)
			flags.fill(Color.WHITE)
			game.planet_material.set_shader_parameter("construction_flags",ImageTexture.create_from_image(flags))
		game._update_border_visibility()
		var slot := 1 if mode == 6 else 0
		var before: Image = await capture(baseline[slot])
		var after: Image = await capture(candidate[slot])
		var result := compare_images(before,after)
		result["name"] = fixture[0]
		if not result["equal"]:
			failures += 1
			before.save_png(output_dir.path_join(str(fixture[0])+"_before.png"))
			after.save_png(output_dir.path_join(str(fixture[0])+"_after.png"))
		# Alternating order reduces bias from warmup and GPU clock changes.
		if fixture[0] in ["information_globe","pacific_information","japan_coast","amazon","himalayas"]:
			var old_ms: Array[float] = []
			var new_ms: Array[float] = []
			var old_gpu: Array[float] = []
			var new_gpu: Array[float] = []
			for round_index: int in 3:
				var old_sample: Dictionary
				var new_sample: Dictionary
				if round_index % 2 == 0:
					old_sample = await measure(baseline[slot])
					new_sample = await measure(candidate[slot])
				else:
					new_sample = await measure(candidate[slot])
					old_sample = await measure(baseline[slot])
				old_ms.append(old_sample["frame_ms"])
				new_ms.append(new_sample["frame_ms"])
				old_gpu.append(old_sample["gpu_ms"])
				new_gpu.append(new_sample["gpu_ms"])
			old_ms.sort()
			new_ms.sort()
			old_gpu.sort()
			new_gpu.sort()
			result["baseline_frame_ms"] = old_ms[1]
			result["candidate_frame_ms"] = new_ms[1]
			result["baseline_gpu_ms"] = old_gpu[1]
			result["candidate_gpu_ms"] = new_gpu[1]
		report.append(result)
		print("MAP_SHADER_FIXTURE ",JSON.stringify(result))
	var file := FileAccess.open(output_dir.path_join("shader_equivalence.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"adapter":RenderingServer.get_video_adapter_name(),"fixtures":report,"failures":failures},"\t"))
	print("MAP_SHADER_EQUIVALENCE fixtures=",report.size()," failures=",failures)
	game.queue_free()
	await process_frame
	quit(1 if failures else 0)
