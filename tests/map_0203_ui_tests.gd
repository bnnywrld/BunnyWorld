extends SceneTree
var failures := 0
func check(ok: bool, description: String) -> void:
	if not ok: failures += 1; printerr("FAIL: ",description)
func _initialize() -> void: run.call_deferred()
func run() -> void:
	var main = load("res://main.tscn").instantiate()
	root.add_child(main)
	while not main.boot_complete: await process_frame
	main._start_selection()
	check(main.map_mode==6 and main.map_picker.selected==6,"Start opens physical map")
	main._map_changed(0)
	main._begin_campaign()
	check(main.map_mode==6 and main.map_picker.selected==6,"new campaign opens physical map")
	if main.focus_tween != null: main.focus_tween.kill()
	main.planet.rotation=Vector3(deg_to_rad(35.686963),-deg_to_rad(139.749462),0)
	main.distance=1.04; main._update_camera_pose();main._update_detail_patch()
	for i: int in 4: await process_frame
	var centre := Vector2(main.world_view.size)*.5
	main._update_map_hover(centre)
	check(main.hover_panel.visible and main.hover_flag.visible and main.hover_flag.texture!=null,"country tooltip displays a real flag image")
	check("Japan" in main.hover_text.text,"flag precedes correct country name")
	var texture_id: int = main.hover_flag.texture.get_instance_id() if main.hover_flag.texture!=null else 0
	for i: int in 10: main._update_map_hover(centre)
	check(main.hover_flag.texture.get_instance_id()==texture_id,"hover reuses cached flag texture")
	for pid: String in main.state.provinces:
		if str(main.state.provinces[pid].get("urban_group","")).is_empty():
			var text: String = main._province_population_tooltip(int(pid))
			check("estimate" in text and not "pool" in text,"rural province shows its individual estimate")
			break
	if failures==0: print("MAP_0203_UI_PASS: physical defaults, flagged cached tooltip, individual rural estimate")
	main.queue_free();await process_frame
	quit(0 if failures==0 else 1)
