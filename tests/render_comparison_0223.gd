extends SceneTree
func _initialize() -> void: run.call_deferred()
func frame() -> void:
	await process_frame
	await RenderingServer.frame_post_draw
func run_variant(script_path: String, variant: String) -> Dictionary:
	var main = load(script_path).new()
	main.state.initialize(JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json")))
	main.world_view=SubViewport.new();main.world_view.size=Vector2i(960,600)
	main.world_view.render_target_update_mode=SubViewport.UPDATE_ALWAYS
	root.add_child(main.world_view)
	main.relief_surface=load("res://scripts/relief_surface.gd").new()
	main.legend=Label.new();main.screen="playing";main._build_planet()
	# Only the tests freeze the glow phase, keeping comparisons deterministic.
	if variant == "after":
		for name: String in ["political_shader","physical_shader"]:
			var shader := Shader.new()
			shader.code=main.get(name).code.replace('#include "res://scripts/planet_surface.gdshaderinc"',FileAccess.get_file_as_string("res://scripts/planet_surface.gdshaderinc")).replace("sin(TIME*1.7)","sin(0.0)")
			main.set(name,shader)
	for material: ShaderMaterial in [main.planet_material]+main.border_materials:
		var shader := Shader.new()
		shader.code=material.shader.code.replace("sin(TIME*1.7)","sin(0.0)")
		var parameters: Dictionary={}
		for parameter: Dictionary in material.shader.get_shader_uniform_list():parameters[parameter["name"]]=material.get_shader_parameter(parameter["name"])
		material.shader=shader
		for key: String in parameters:material.set_shader_parameter(key,parameters[key])
	var views: Array=[]
	for row: Array in [[0,53.9,27.5,1.07,"minsk_close_political"],[6,46.0,7.5,1.025,"alps_close_physical"],[6,40.0,85.0,2.2,"asia_transition_physical"],[6,40.0,85.0,2.5,"asia_far_physical"],[6,75.0,-40.0,3.5,"arctic_far_physical"],[6,-75.0,20.0,3.5,"antarctic_far_physical"],[0,30.0,20.0,5.0,"far_political"],[6,40.0,85.0,5.0,"far_physical"]]:
		main.map_mode=row[0];main.distance=row[3]
		main.planet.rotation=Vector3(deg_to_rad(row[1]),-deg_to_rad(row[2]),0)
		main._update_camera_pose();main._update_detail_patch();main._rebuild_palette()
		main.planet_material.set_shader_parameter("camera_distance",main.distance)
		main.planet_material.set_shader_parameter("terrain_mix",clampf((2.0-main.distance)/.35,0,1) if main.map_mode==6 else 0.0)
		main.planet_material.set_shader_parameter("city_detail",clampf((1.5-main.distance)/.25,0,1))
		main.planet_material.set_shader_parameter("far_filter",clampf((main.distance-2.4),0,1))
		main.waterways_material.set_shader_parameter("camera_distance",main.distance)
		main.waterways_material.set_shader_parameter("physical_mode",main.map_mode==6)
		for material: ShaderMaterial in main.border_materials:material.set_shader_parameter("camera_distance",main.distance)
		for i: int in 4:await frame()
		main.world_view.get_texture().get_image().save_png("res://validation_0223/%s/%s.png"%[variant,row[4]])
		var times: Array=[]
		for i: int in 12:
			var start:=Time.get_ticks_usec();main.planet.rotation.y+=.00012
			main._update_camera_pose();main._update_detail_patch();await frame()
			times.append(float(Time.get_ticks_usec()-start)/1000.0)
		times.sort()
		views.append({"view":row[4],"moving_median_ms":times[6],"primitives":Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME),"draw_calls":Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)})
		print("RENDER_0223 ",variant," ",JSON.stringify(views[-1]))
	var result: Dictionary={"variant":variant,"views":views,"textures_bytes":Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED),"buffers_bytes":Performance.get_monitor(Performance.RENDER_BUFFER_MEM_USED)}
	main.world_view.queue_free();main.legend.free();main.free()
	for i: int in 4:await process_frame
	return result
func run() -> void:
	for name: String in ["before","after"]:DirAccess.make_dir_recursive_absolute("res://validation_0223/"+name)
	var before: Dictionary
	if OS.get_environment("BUNNY_COMPARE_AFTER_ONLY") == "1":
		before = JSON.parse_string(FileAccess.get_file_as_string("res://validation_0223/render_comparison.json"))["before"]
	else:
		before = await run_variant("res://validation_0223/reference_main_0222.gd","before")
	var after:=await run_variant("res://scripts/main.gd","after")
	var file:=FileAccess.open("res://validation_0223/render_comparison.json",FileAccess.WRITE)
	file.store_string(JSON.stringify({"scope":"0.2.0.22/23 production renderer comparison at 960x600, twelve moving samples per view. Initial same-process baseline retained for final shader recheck. Linux software rendering, not native GPU FPS; full UI/scenery excluded.","adapter":RenderingServer.get_video_adapter_name(),"before":before,"after":after},"\t"))
	quit()
