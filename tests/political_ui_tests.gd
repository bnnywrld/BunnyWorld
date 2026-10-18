extends SceneTree
var checks := 0
var failures := 0
func check(value: bool, description: String) -> void:
	checks += 1
	if not value:
		failures += 1
		push_error(description)
func _initialize() -> void:
	call_deferred("run")
func run() -> void:
	var game = load("res://main.tscn").instantiate()
	root.add_child(game)
	while not game.boot_complete: await process_frame
	game._start_selection()
	game.state.selected_country = "POL"
	game._begin_campaign()
	var before := JSON.stringify(game.state.countries)
	var regions := JSON.stringify(game.state.regions)
	game._show_feature("Government")
	await process_frame
	await process_frame
	var panel = game.control_details.get_node("PoliticalPanel")
	check(panel.selectors.size() == 5, "five property selectors")
	check(game.control_panel.size.x >= 700, "government panel widened")
	for picker: OptionButton in panel.selectors.values():
		check(picker.get_global_rect().end.x <= panel.get_global_rect().end.x + 1, "property stays inside panel")
	for key in panel.selectors:
		var picker: OptionButton = panel.selectors[key]
		check(picker.selected == 0, "unknown defaults")
		for i in range(1, picker.item_count):
			picker.select(i)
			picker.item_selected.emit(i)
			check(game.political_ui_choices["POL"][key] == picker.get_item_text(i), "option applied")
		picker.select(0)
		picker.item_selected.emit(0)
		check(not game.political_ui_choices["POL"].has(key), "clear placeholder")
	panel.selectors["executive"].select(2)
	panel.selectors["executive"].item_selected.emit(2)
	game._show_feature("Government")
	check(not game.control_panel.visible, "same button closes panel")
	game._show_feature("Government")
	await process_frame
	panel = game.control_details.get_node("PoliticalPanel")
	check(panel.selectors["executive"].selected == 2, "choices survive reopening")
	game._show_country("GER", false)
	game._show_feature("Government")
	await process_frame
	check(game.political_ui_choices.has("POL") and not game.political_ui_choices.has("GER"), "always player government")
	check(JSON.stringify(game.state.countries) == before, "country data unchanged")
	check(JSON.stringify(game.state.regions) == regions, "state data unchanged")
	var save_path := "user://political_ui_test.bws"
	check(game.state.save_game(save_path, game._view_state()), "save still works")
	check(game._load_from(save_path, false), "load still works")
	check(game.political_ui_choices.is_empty(), "successful load clears UI choices")
	DirAccess.remove_absolute(ProjectSettings.globalize_path(save_path))
	game._show_feature("Economy")
	await process_frame
	check(game.control_panel.size.x < 500, "other panels return to narrow size")
	game._start_selection()
	check(game.political_ui_choices.is_empty(), "new campaign clears UI choices")
	print("POLITICAL_UI_RESULT checks=", checks, " failures=", failures)
	quit(0 if failures == 0 else 1)
