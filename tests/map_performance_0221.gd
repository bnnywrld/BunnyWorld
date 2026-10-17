extends SceneTree
func _initialize() -> void: run.call_deferred()
func run() -> void:
 DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
 var output:=OS.get_environment("BUNNY_BENCH_OUTPUT")
 DirAccess.make_dir_recursive_absolute(output)
 var main=load("res://scripts/main.gd").new()
 main.state.initialize(JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json")))
 main.world_view=SubViewport.new();main.world_view.size=Vector2i(960,600);main.world_view.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(main.world_view)
 main.relief_surface=load("res://scripts/relief_surface.gd").new();main.legend=Label.new();main.screen="playing";main._build_planet()
 var results: Array=[]
 for row: Array in [[0,84,53.9,27.5,1.07,"minsk_political"],[0,1553,31.9,35.0,1.055,"israel_political"],[6,1813,2.3,99.2,1.07,"sumatra_physical"],[6,1499,46.0,7.5,1.025,"alps_physical"],[0,534,41.90406745,12.4531904,1.025,"rome_political"],[0,177,40.0,85.0,2.0,"asia_political"],[0,84,53.9,27.5,1.5,"europe_medium"],[0,534,30.0,20.0,3.5,"globe_political"]]:
  main.map_mode=row[0];main.state.selected_country=main.state.regions[str(row[1])]["owner"];main.state.selected_region=row[1];main.state.selected_province=0;main.inspection_active=true
  main.distance=row[4];main.planet.rotation=Vector3(deg_to_rad(row[2]),-deg_to_rad(row[3]),0);main._update_camera_pose();main._update_detail_patch();main._rebuild_palette()
  main.planet_material.set_shader_parameter("camera_distance",main.distance);main.planet_material.set_shader_parameter("province_opacity",clampf((1.2-main.distance)/.08,0,1));main.planet_material.set_shader_parameter("city_detail",clampf((1.5-main.distance)/.25,0,1))
  for material: ShaderMaterial in main.border_materials:material.set_shader_parameter("camera_distance",main.distance)
  main.waterways_material.set_shader_parameter("camera_distance",main.distance);main.waterways_material.set_shader_parameter("physical_mode",row[0]==6)
  main._update_border_visibility()
  for i: int in 6:await process_frame
  await RenderingServer.frame_post_draw
  main.world_view.get_texture().get_image().save_png(output.path_join(str(row[5])+".png"))
  var record: Dictionary={"case":row[5]}
  for moving: bool in [false,true]:
   var times: Array=[]
   for i: int in 10:
    var started:=Time.get_ticks_usec()
    if moving:main.planet.rotation.y+=.00012
    main._update_camera_pose();main._update_detail_patch()
    await process_frame
    await RenderingServer.frame_post_draw
    times.append(float(Time.get_ticks_usec()-started)/1000.0)
   times.sort();record["moving" if moving else "stationary"]={"median_ms":times[5],"p90_ms":times[9],"primitives":Performance.get_monitor(Performance.RENDER_TOTAL_PRIMITIVES_IN_FRAME),"draw_calls":Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)}
  results.append(record);print("MAP_BENCH ",JSON.stringify(record))
 var f:=FileAccess.open(output.path_join("results.json"),FileAccess.WRITE)
 f.store_string(JSON.stringify({"version":ProjectSettings.get_setting("application/config/version"),"renderer":RenderingServer.get_video_adapter_name(),"viewport":[960,600],"native_windows_tested":false,"cases":results},"\t"))
 main.world_view.queue_free();main.legend.free();main.free();await process_frame;quit()
