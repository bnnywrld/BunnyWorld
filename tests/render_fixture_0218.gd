extends SceneTree
func _initialize() -> void:run.call_deferred()
func run() -> void:
 DirAccess.make_dir_recursive_absolute("res://validation_0218")
 # Use production construction/shaders/picking without preparing unrelated
 # city models or UI; the full application test covers those integration paths.
 var main=load("res://scripts/main.gd").new()
 main.state.initialize(JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json")))
 main.world_view=SubViewport.new();main.world_view.size=Vector2i(1280,800);main.world_view.render_target_update_mode=SubViewport.UPDATE_ALWAYS;root.add_child(main.world_view)
 main.relief_surface=load("res://scripts/relief_surface.gd").new();main.legend=Label.new();main.screen="playing";main._build_planet()
 for row: Array in [[1813,4655,2.3,99.2,1.07],[253,3093,35.08,33.24,1.022],[1569,5469,38.05,127.15,1.035],[464,4478,41.90406745,12.4531904,1.025]]:
  main.map_mode=6 if row[0]!=464 else 0;main.state.selected_country=main.state.regions[str(row[0])]["owner"];main.state.selected_region=row[0];main.state.selected_province=row[1];main.inspection_active=true
  main.distance=row[4];main.planet.rotation=Vector3(deg_to_rad(row[2]),-deg_to_rad(row[3]),0);main._update_camera_pose();main._update_detail_patch();main._rebuild_palette()
  main.planet_material.set_shader_parameter("camera_distance",main.distance);main.planet_material.set_shader_parameter("province_opacity",1.0);main.planet_material.set_shader_parameter("city_detail",1.0)
  for material: ShaderMaterial in main.border_materials:material.set_shader_parameter("camera_distance",main.distance)
  for i: int in 4:await process_frame
  await RenderingServer.frame_post_draw;main.world_view.get_texture().get_image().save_png("res://validation_0218/final_%s.png"%str(row[0]))
  if row[0]==464:assert(main._region_at(Vector2(640,400))==464,"Subpixel enclave picking must remain exact")
  print("RENDER_FIXTURE_PASS ",row[0])
 main.world_view.queue_free();main.legend.free();main.free();await process_frame;quit()
