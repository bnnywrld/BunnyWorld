extends SceneTree
var main
var folder: String
func _initialize() -> void: run.call_deferred()
func settle() -> void:
 for i: int in 5:await process_frame
 await create_timer(.3).timeout
func shot(name: String) -> void:
 await settle();main.country_label_layer.update_view();await RenderingServer.frame_post_draw
 root.get_texture().get_image().save_png(folder.path_join(name+".png"))
 print("VISUAL_CAPTURE ",name," labels=",main.country_label_layer.visible_labels.map(func(e:Dictionary):return e["tag"]))
func view(tag: String, zoom: float, mode: int, own: bool=true) -> void:
 main._close_panels();main.inspect_region=0;main.inspect_province=0;main.national_profile_expanded=false
 if own:main.state.player_country=tag;main._update_country_bar()
 main._map_changed(mode);main._show_country(tag,false);main._focus_country(tag,false)
 if main.focus_tween!=null:main.focus_tween.kill()
 main.distance=zoom;main._update_camera_pose();main._update_detail_patch();await settle()
func run() -> void:
 folder=OS.get_environment("BUNNY_VALIDATION_DIR")
 main=load("res://main.tscn").instantiate();root.add_child(main)
 while not main.boot_complete:await process_frame
 main.country_labels_enabled=true
 main._start_selection();main._show_country("JAP",false);main._begin_campaign()
 await view("JAP",1.5,0);await shot("japan_political")
 main.control_details.get_node("NationalProfileToggle").set_pressed_no_signal(true);main.control_details.get_node("NationalProfileToggle").pressed.emit();await shot("japan_profile")
 await view("USA",2.4,0);main._close_panels();await shot("north_america_names")
 await view("GER",2.0,0);main._close_panels();await shot("europe_names")
 await view("CHI",2.9,6);main._close_panels();await shot("asia_physical_names")
 if OS.get_environment("GALLERY_LABELS_ONLY")=="1":
  print("VISUAL_LABEL_GALLERY_COMPLETE");main.queue_free();await process_frame;quit();return
 await view("NRY",1.35,6,false);await shot("norway_coasts")
 await view("JAP",1.035,6);main.planet.rotation=Vector3(deg_to_rad(35.686963),-deg_to_rad(139.749462),0);main._update_camera_pose();main._update_detail_patch();await settle()
 var point: Vector2=Vector2(main.world_view.size)*.5;main.show_regions=true;main.inspect_region=main._region_at(point);main.inspect_province=main._province_at(point);main._show_country("JAP",false);await shot("tokyo_province")
 main.get_window().size=Vector2i(1100,700);main.get_window().content_scale_size=Vector2i(1100,700);await settle();await shot("minimum_1100")
 main._show_organization();await shot("organization_panel")
 print("VISUAL_GALLERY_COMPLETE")
 main.queue_free();await process_frame;quit()
