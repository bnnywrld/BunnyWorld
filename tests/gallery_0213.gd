extends SceneTree
var main
var failures:=0
var checks: Array[String]=[]
var folder:=OS.get_environment("BUNNY_VALIDATION_DIR")
func _initialize() -> void:run.call_deferred()
func settle() -> void:
	for i: int in 3:await process_frame
func check(value: bool,name: String) -> void:
	checks.append(("PASS " if value else "FAIL ")+name)
	print(checks[-1])
	if not value:failures+=1
func shot(name: String) -> void:
	await settle();await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(folder.path_join(name+".png"))
func run() -> void:
	main=load("res://main.tscn").instantiate();root.add_child(main)
	while not main.boot_complete:await process_frame
	main.show_regions=true
	main._start_selection();main._show_country("JAP",false);main._begin_campaign()
	main._map_changed(6);main._close_panels();main._focus_country("CHI",false)
	if main.focus_tween!=null:main.focus_tween.kill()
	main.rotation_velocity=Vector2.ZERO;main.distance=2.0;main._update_camera_pose();main.country_label_layer.update_view(true)
	await shot("east_asia_names")
	check(main.country_labels_enabled,"names stay enabled")
	check(main.country_label_layer.label_material.get_shader_parameter("glyph_atlas") is ImageTexture,"country labels use runtime coverage texture")
	main.planet.rotation=Vector3(deg_to_rad(34.75),-deg_to_rad(138.4),0)
	main.distance=1.035;main.show_regions=true;main._update_camera_pose();main._update_detail_patch()
	main.inspect_region=1564;main.inspect_province=5172;main._show_country("JAP",false)
	main.territory_collapsed=false;main._position_panels();await create_timer(.3).timeout
	await shot("tokai_drawer")
	check(main.territory_panel.size.x>430,"territory drawer wider at 1440")
	check(main.territory_heading.has_node("SelectionBreadcrumb"),"state heading pinned outside scrolling content")
	for key: String in ["StateBuildings","StateResources","StateInfrastructure","SelectedProvince"]:
		check(main.territory_details.has_node(key),key+" section exists")
	var heading: Vector2=main.territory_heading.global_position
	main.territory_scroll.scroll_vertical=160;await settle()
	check(main.territory_heading.global_position.is_equal_approx(heading),"heading remains pinned during scroll")
	await shot("tokai_inventory")
	main.control_panel.hide();main.right_panel.hide();main.territory_clip.hide();main.territory_handle.hide()
	await shot("tokai_coast")
	main.inspect_region=0;main.inspect_province=0;main._show_country("JAP",false)
	main.inspect_region=1564;main.inspect_province=5172;main._show_country("JAP",false)
	main.get_window().size=Vector2i(1100,700);main.get_window().content_scale_size=Vector2i(1100,700)
	await settle();main._position_panels();await create_timer(.3).timeout
	check(main.territory_clip.global_position.x>=0 and main.territory_clip.get_global_rect().end.x<=1100,"drawer fits 1100-width window")
	check(main.territory_panel.size.x>=350,"drawer retains usable compact width")
	check(main.territory_scroll.get_h_scroll_bar().max_value<=main.territory_scroll.get_h_scroll_bar().page+1,"inventory needs no horizontal scroll")
	await shot("minimum_1100")
	main._toggle_territory();await create_timer(.3).timeout
	check(main.territory_collapsed and main.territory_handle.visible,"wide drawer collapses with handle accessible")
	var f:=FileAccess.open(folder.path_join("graphical_results.json"),FileAccess.WRITE)
	f.store_string(JSON.stringify({"checks":checks,"failures":failures,"renderer":RenderingServer.get_video_adapter_name()},"\t"))
	print("VISUAL_0213_COMPLETE checks=",checks.size()," failures=",failures)
	main.queue_free();await process_frame;quit(1 if failures else 0)
