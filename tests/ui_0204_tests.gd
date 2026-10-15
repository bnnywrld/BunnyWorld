extends SceneTree
var failures := 0
func check(ok: bool, description: String) -> void:
	print(("PASS: " if ok else "FAIL: ") + description)
	if not ok: failures += 1
func _initialize() -> void: run.call_deferred()
func settle() -> void:
	for i: int in 5: await process_frame
	await create_timer(.2).timeout
func capture(main, name: String) -> void:
	await settle()
	await RenderingServer.frame_post_draw
	main.get_viewport().get_texture().get_image().save_png(OS.get_environment("BUNNY_VALIDATION_DIR").path_join(name+".png"))
func run() -> void:
	var main = load("res://main.tscn").instantiate()
	root.add_child(main)
	while not main.boot_complete: await process_frame
	check(str(ProjectSettings.get_setting("application/config/version"))=="0.2.0.4","release version")
	main._start_selection(); main._show_country("POL", false); main._begin_campaign()
	await settle()
	check(not main.title_label.visible and not main.campaign_label.visible and not main.status.visible,"country name, playing-as and footer removed")
	check(main.stats_row.global_position.y < main.header_flag.global_position.y,"stats above flag and navigation")
	check(main.foundation.toolbar.size.y >= 46 and absf(main.foundation.toolbar.global_position.y-main.header_flag.global_position.y)<2,"larger navigation aligned with flag")
	check(main.view_container.size.y >= 735,"globe recovers vertical space at 1440×900")
	for record: Dictionary in main.foundation.indicators.values():
		check(record["cell"] is PanelContainer,"separate stat box")
		check(absf(record["icon"].global_position.y+record["icon"].size.y*.5-record["label"].global_position.y-record["label"].size.y*.5)<2,"icon/value vertical alignment")
	check(main.view_container.get_parent().get_child(0).get_node("FindPlace").text.is_empty(),"search uses magnifying glass")
	check(main.pause_button.size.x < 50,"compact clock controls")
	await capture(main,"campaign_1440")
	if main.focus_tween != null: main.focus_tween.kill()
	main.planet.rotation=Vector3(deg_to_rad(35.686963),-deg_to_rad(139.749462),0)
	main.distance=1.9;main._update_camera_pose();main._update_cities()
	check(main.city_layer.get("markers").is_empty(),"capital labels absent at old early zoom")
	main.distance=1.5;main._update_camera_pose();main._update_cities()
	check(not main.city_layer.get("markers").is_empty(),"capital labels at closer zoom")
	main.distance=1.025;main._update_camera_pose();main._update_detail_patch();main.show_regions=true
	await settle()
	var centre := Vector2(main.world_view.size)*.5
	main.inspect_region=main._region_at(centre);main.inspect_province=main._province_at(centre)
	main._show_country("JAP",false)
	await settle()
	check(main.territory_panel.visible and main.right_panel.visible,"territory drawer opens for clicked State/province")
	check(absf(main.territory_panel.position.x-main.right_panel.position.x-main.right_panel.size.x)<2,"drawer immediately to right of diplomacy")
	var territory := ""
	for child: Node in main.territory_details.get_children():
		if child is Label: territory += child.text+"\n"
	check("Province population:" in territory and "State population:" in territory,"population info moved into drawer")
	var diplomacy := ""
	for child: Node in main.diplomatic_details.get_children():
		if child is Label: diplomacy += child.text+"\n"
	check(not "SELECTED STATE" in diplomacy and not "Province population:" in diplomacy,"territory removed from diplomacy body")
	await capture(main,"territory_1440")
	main._hide_panel(main.territory_panel);await settle()
	check(absf(main.right_panel.position.x-main.view_container.size.x+330)<2,"closing drawer restores diplomacy to edge")
	main._close_panels()
	main.show_regions=false;main.distance=1.5;main._update_camera_pose()
	Input.warp_mouse(main.view_container.global_position+main.view_container.size*.5)
	await settle();main._update_map_hover(Vector2(main.world_view.size)*.5);await settle()
	check(main.hover_panel.visible and main.hover_panel.size.x < 180,"short country tooltip fits its content")
	await capture(main,"tooltip_1440")
	main.show_regions=true;main.distance=1.025;main._update_camera_pose();main._update_detail_patch()
	main.inspect_region=main._region_at(Vector2(main.world_view.size)*.5);main.inspect_province=main._province_at(Vector2(main.world_view.size)*.5)
	main._show_country("JAP",false)
	DisplayServer.window_set_size(Vector2i(1100,700));main.get_window().content_scale_size=Vector2i(1100,700);await settle()
	check(main.size.x <= 1100 and main.view_container.size.y > 530,"compact layout at 1100×700")
	check(main.right_panel.position.x >= 0 and main.territory_panel.position.x+main.territory_panel.size.x<=main.view_container.size.x+1,"drawer fits smaller viewport")
	await capture(main,"territory_1100")
	main._show_country("POL",false);await settle()
	check(not main.territory_panel.visible,"stale drawer closes on different country")
	main._open_place_search();await settle();check(main.place_dialog.visible,"icon search still opens working search")
	main.place_dialog.hide();main._resume_after_dialog()
	main._enter_menu();main._start_selection();await settle()
	check(not main.stats_row.visible and not main.foundation.toolbar.visible,"campaign-only controls hidden in selection")
	await capture(main,"selection_1100")
	print("UI_0204_TESTS_"+("PASS" if failures==0 else "FAIL"))
	if failures == 0 and OS.get_environment("BUNNY_RUN_SMOKE") == "1":
		DisplayServer.window_set_size(Vector2i(1440,900))
		main.get_window().content_scale_size=Vector2i(1440,900)
		main._enter_menu()
		await main._run_smoke_test()
		return
	main.queue_free();await process_frame
	quit(0 if failures==0 else 1)
