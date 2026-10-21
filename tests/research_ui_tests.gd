extends SceneTree
const Rules = preload("res://scripts/government_rules.gd")
const Institutions = preload("res://scripts/research_institutions.gd")
var checks := 0
var failures := 0
func check(value: bool, description: String) -> void:
	checks += 1
	if not value:
		failures += 1
		push_error(description)
func _initialize() -> void: run.call_deferred()
func click_at(point: Vector2) -> void:
	var motion := InputEventMouseMotion.new()
	motion.position = point
	root.push_input(motion, true)
	for pressed: bool in [true, false]:
		var click := InputEventMouseButton.new()
		click.button_index = MOUSE_BUTTON_LEFT
		click.position = point
		click.pressed = pressed
		root.push_input(click, true)
	await process_frame
func escape() -> void:
	var event := InputEventKey.new()
	event.keycode = KEY_ESCAPE
	event.pressed = true
	root.push_input(event, true)
	await process_frame
func run() -> void:
	root.size = Vector2i(1440, 900)
	var game = load("res://main.tscn").instantiate()
	root.add_child(game)
	while not game.boot_complete: await process_frame
	game._start_selection()
	game.state.selected_country = "JAP"
	game._begin_campaign()
	var world = game.state
	var pp_before: float = world.political_power("JAP")
	var laws_before: Dictionary = world.government_properties.duplicate(true)
	game._show_feature("Government")
	await create_timer(.25).timeout
	var politics = game.control_details.get_node("PoliticalPanel")
	var first: Button = politics.property_buttons["form_of_government"]
	var second: Button = politics.property_buttons["executive"]
	await click_at(first.get_global_rect().get_center())
	for frame: int in 4: await process_frame
	check(politics.choice_dialog.size.y < 400, "law picker stays compact after layout settles")
	check(politics.choice_dialog.visible, "actual law click opens styled panel")
	check(politics.choice_dialog is PanelContainer and not politics.choice_dialog is Window, "law popup is an in-game panel")
	check(not game.foundation.modals_visible(), "law popup does not block other controls")
	var popup_id: int = politics.choice_dialog.get_instance_id()
	check(not politics.choice_dialog.get_global_rect().intersects(second.get_global_rect()), "next law remains exposed")
	await click_at(second.get_global_rect().get_center())
	check(politics.choice_dialog.visible and politics.active_property["key"] == "executive", "single click switches law")
	check(politics.choice_dialog.title == "Executive System", "new law title and options replace previous law")
	check(politics.choice_dialog.get_instance_id() == popup_id, "one reusable law window")
	check(not politics.choice_buttons.has("Republic") and politics.choice_buttons.has("Presidential"), "stale choices removed")
	check(world.political_power("JAP") == pp_before, "switching law popup costs no PP")
	await escape()
	check(not politics.choice_dialog.visible and game.control_panel.visible, "Escape closes popup before Government tab")
	await click_at(first.get_global_rect().get_center())
	await click_at(politics.choice_dialog.close_button.get_global_rect().get_center())
	check(not politics.choice_dialog.visible, "styled close button works")
	await click_at(first.get_global_rect().get_center())
	game._show_feature("Research")
	await create_timer(.25).timeout
	var research = game.control_details.get_node("ResearchPanel")
	check(not is_instance_valid(politics), "old Government panel removed")
	check(research.institution_buttons.size() == 5, "Japan has five university slots")
	check(research.institution_buttons[0].text.begins_with("University of Tokyo"), "named university shown")
	check(get_nodes_in_group("floating_ui").size() == 1, "old law window freed with its tab")
	await click_at(research.institution_buttons[0].get_global_rect().get_center())
	for frame: int in 4: await process_frame
	check(research.tech_window.size.y <= 600, "tree respects requested window height after layout settles")
	check(game.get_viewport_rect().encloses(research.tech_window.get_global_rect()), "settled tree stays within viewport")
	check(research.tech_window.visible, "university click opens technology tree")
	check(research.active_institution == "University of Tokyo", "tree identifies selected university")
	check(research.tree_canvas.get_child_count() == 0, "technology tree is empty")
	check(research.tech_window.get_theme_stylebox("panel").bg_color == game.control_panel.get_theme_stylebox("panel").bg_color, "research window uses existing panel background")
	await escape()
	check(not research.tech_window.visible and game.control_panel.visible, "Escape closes tree before Research tab")
	research.open_tree(research.institutions[1])
	check(research.institution_label.text == "Kyoto University", "second institution updates tree header")
	await click_at(research.tech_window.close_button.get_global_rect().get_center())
	check(not research.tech_window.visible, "tree close button works")
	for tag: String in world.countries:
		var names: Array[String] = Institutions.for_country(world, tag)
		check(names.size() >= 2 and names.size() <= 6, "country has bounded slot count")
		check(names == Institutions.for_country(world, tag), "institution names deterministic")
		var seen := {}
		for institution: String in names:
			check(not institution.is_empty() and not seen.has(institution), "institution names unique and nonempty")
			seen[institution] = true
	research.open_tree(research.institutions[0])
	root.size = Vector2i(1024, 768)
	await process_frame
	await process_frame
	var bounds: Rect2 = game.get_viewport_rect()
	check(bounds.encloses(research.tech_window.get_global_rect()), "tree fits smaller viewport")
	game._show_feature("Research")
	check(not research.tech_window.visible and not game.control_panel.visible, "toggling Research hides its window")
	game._show_feature("Government")
	await process_frame
	await process_frame
	check(get_nodes_in_group("floating_ui").size() == 1, "repeated tab changes leave no orphan windows")
	check(world.political_power("JAP") == pp_before and world.government_properties == laws_before, "UI browsing changes no PP or laws")
	game.queue_free()
	await process_frame
	check(get_nodes_in_group("floating_ui").is_empty(), "all floating panels freed with game")
	print("RESEARCH_UI_RESULT checks=", checks, " failures=", failures)
	quit(0 if failures == 0 else 1)
