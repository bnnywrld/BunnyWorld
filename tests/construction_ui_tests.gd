extends SceneTree
var checks := 0
var failures := 0
func check(value: bool, text: String) -> void:
	checks += 1
	if not value: failures += 1; push_error(text)
func _initialize() -> void: run.call_deferred()
func click(button: Button) -> void:
	var point := button.get_global_rect().get_center()
	var motion := InputEventMouseMotion.new()
	motion.position = point
	root.push_input(motion, true)
	for pressed: bool in [true,false]:
		var event := InputEventMouseButton.new()
		event.position = point
		event.button_index = MOUSE_BUTTON_LEFT
		event.pressed = pressed
		root.push_input(event,true)
	await process_frame
func capture(file: String) -> void:
	var dir := OS.get_environment("BUNNYWORLD_QA_DIR")
	if dir.is_empty() or DisplayServer.get_name()=="headless": return
	await process_frame
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(dir.path_join(file))
func run() -> void:
	root.size = Vector2i(1440,900)
	var game = load("res://main.tscn").instantiate()
	root.add_child(game)
	while not game.boot_complete: await process_frame
	game._start_selection()
	game.state.selected_country = "GER"
	game._begin_campaign()
	if game.focus_tween!=null: game.focus_tween.kill()
	game.rotation_velocity = Vector2.ZERO
	game._focus_country("GER",false)
	game.distance = 1.5
	game._update_camera_pose()
	game._map_changed(0)
	var count: int = game.map_picker.item_count
	game._show_feature("Construction")
	await create_timer(.3).timeout
	var ui = game.control_details.get_node("ConstructionPanel")
	check(game.map_mode == 8 and game.active_feature=="Construction", "construction tab enters private mode")
	check(game.map_picker.item_count==count and count==8 and game.map_picker.disabled, "private mode is not in general map picker")
	check(ui.building_buttons.size()==23, "all approved state buildings selectable")
	check("Manufactured Goods" in ui.summary.text, "manufactured goods factory count shown")
	await click(ui.building_buttons["infrastructure"])
	check(game.construction_building=="infrastructure", "actual pointer selects building")
	var sid := str(int(game.state.countries["GER"]["capital"]))
	var before: int = game.state.construction.queue.size()
	game._construction_click(int(sid))
	check(game.state.construction.queue.size()==before+1 and game.active_feature=="Construction", "state click queues building without opening country inspector")
	check(game.construction_flags.get_image().get_pixel(int(sid),0).r>.99, "queued state has stripe palette bit")
	check(game.planet_material.get_shader_parameter("construction_mode"), "shader stripe mode active")
	check(game._view_state()["map_mode"]==0, "save stores previous normal map mode")
	var foreign := str(int(game.state.countries["FRA"]["capital"]))
	game._construction_click(int(foreign))
	check(game.state.construction.queue.size()==before+1, "foreign click does not queue or leave tab")
	var r: Dictionary = game.state.regions[sid]
	var old_slots := int(r["construction_slots"])
	r["construction_slots"] = game.state.construction.shared_used(r["buildings"])
	game._select_construction_building("industrial_complex")
	game._rebuild_palette()
	var blue: Color = game.palette_texture.get_image().get_pixel(int(sid),0)
	check(blue.is_equal_approx(Color("286fba")), "full shared state is blue")
	r["construction_slots"] = old_slots
	game._rebuild_palette()
	game._update_view_uniforms()
	check(game.show_regions and game.planet_material.get_shader_parameter("province_opacity")==0, "construction shows state divisions without province clutter")
	# Exercise the real globe ray-pick path as well as model dispatch.
	var map_point := Vector2(game.world_view.size) / 2.0
	var picked: int = game._region_at(map_point)
	if game.state.regions.has(str(picked)) and game.state.regions[str(picked)]["owner"]=="GER":
		game.construction_building = "offices"
		var click_event := InputEventMouseButton.new()
		click_event.position = map_point
		click_event.button_index = MOUSE_BUTTON_LEFT
		click_event.pressed = true
		var old_size: int = game.state.construction.queue.size()
		game._globe_input(click_event)
		check(game.state.construction.queue.size()==old_size+1, "actual globe ray click creates queued building")
	else: check(false, "test focus exposes a German state under globe center")
	await capture("construction_1440.png")
	var save_path := "user://tests/construction_ui.json"
	check(game.state.save_game(save_path,game._view_state()), "save while in private mode")
	check(game._load_from(save_path,false) and not game.map_picker.disabled and game.map_mode==0, "load exits private mode and restores picker")
	DirAccess.remove_absolute(save_path)
	DirAccess.remove_absolute(save_path+".bak")
	game._show_feature("Construction")
	await process_frame
	var revision: int = game.state.construction.revision
	game.state.paused = true
	for i: int in 10: game._process(1.0/60)
	check(game.state.construction.revision == revision, "idle construction performs no simulation updates")
	game._show_feature("Government")
	await create_timer(.25).timeout
	check(game.map_mode==0 and not game.map_picker.disabled and not game.planet_material.get_shader_parameter("construction_mode"), "switching tabs restores previous mode and disables stripes")
	game._map_changed(6)
	game._show_feature("Construction")
	await process_frame
	game._show_feature("Construction")
	check(game.map_mode==6 and not game.control_panel.visible, "toggle closes construction and restores physical mode")
	game._show_feature("Construction")
	await create_timer(.2).timeout
	var event := InputEventKey.new()
	event.keycode=KEY_ESCAPE;event.pressed=true
	root.push_input(event,true)
	await process_frame
	check(game.map_mode==6 and not game.control_panel.visible, "Escape closes construction and restores map")
	game._show_feature("Construction")
	await process_frame
	game._map_changed(1)
	check(game.map_mode==1 and game.active_feature!="Construction", "external map switch cannot strand private mode")
	game._show_feature("Construction")
	await create_timer(.2).timeout
	root.size=Vector2i(1024,768)
	await process_frame
	await process_frame
	check(game.get_viewport_rect().encloses(game.control_panel.get_global_rect()), "construction fits smaller viewport")
	await capture("construction_1024.png")
	game.queue_free()
	await process_frame
	print("CONSTRUCTION_UI checks=",checks," failures=",failures)
	quit(0 if failures==0 else 1)
