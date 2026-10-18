extends SceneTree
const Rules = preload("res://scripts/government_rules.gd")
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
	var world = game.state
	var map_before: Dictionary = world.regions.duplicate(true)
	game._show_country("POL", false)
	await process_frame
	await process_frame
	var summary = game.control_details.get_node("PoliticalSummary")
	var stats = game.control_details.get_node("CountrySummary")
	check(summary.get_index() < stats.get_index(), "portraits/parliament above stats")
	check(stats.columns == 3 and stats.get_child_count() == 6, "compact 3 by 2 stats")
	for label: Node in stats.find_children("*", "Label", true, false):
		check("POLITICAL POWER" not in label.text, "no country PP stat")
	check(summary.parliament.can_activate, "own parliament clickable")
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	summary.parliament._gui_input(click)
	await process_frame
	check(game.active_feature == "Government", "own parliament opens Government")
	var panel = game.control_details.get_node("PoliticalPanel")
	check(game.control_panel.size.x <= 610, "compact government width")
	check(game.control_panel.size.y <= 490, "government height fits its content")
	check(panel.property_buttons.size() == 5, "five property buttons")
	check(panel.find_children("*", "OptionButton", true, false).is_empty(), "no dropdown properties")
	world.countries["POL"]["starting_stats"]["political_power"] = 350.0
	panel.open_property(Rules.PROPERTIES[0])
	await process_frame
	check(panel.choice_dialog.visible and game.foundation.modals_visible(), "property choice is modal")
	check(panel.choice_buttons.size() == 3, "constitutional choices")
	panel.choice_buttons["Republic"].pressed.emit()
	check(world.political_power("POL") == 250, "change deducts exactly 100 PP")
	check(world.government_property("POL", "constitution") == "Republic", "choice applied")
	check(not panel.choice_dialog.visible, "choice closes window")
	check(not world.change_government_property("POL", "constitution", "Republic"), "same choice rejected")
	check(world.political_power("POL") == 250, "same choice free of charges")
	check(not world.change_government_property("GER", "constitution", "Republic"), "foreign country protected")
	check(not world.change_government_property("POL", "invalid", "Republic"), "invalid property rejected")
	check(not world.change_government_property("POL", "constitution", "invalid"), "invalid value rejected")
	world.countries["POL"]["starting_stats"]["political_power"] = 99.5
	panel.open_property(Rules.PROPERTIES[1])
	check(panel.choice_buttons["Presidential"].disabled, "insufficient balance disabled")
	panel.apply_choice("Presidential")
	check(world.political_power("POL") == 99.5 and world.government_property("POL", "executive").is_empty(), "insufficient PP never spent")
	world.countries["POL"]["starting_stats"]["political_power"] = 100.0
	panel.refresh()
	check(not panel.choice_buttons["Presidential"].disabled, "affordability refreshes")
	panel.apply_choice("Presidential")
	check(world.political_power("POL") == 0, "exact balance allowed")
	for property: Dictionary in Rules.PROPERTIES:
		for option: String in property["options"]:
			world.countries["POL"]["starting_stats"]["political_power"] = 100
			var same: bool = world.government_property("POL", property["key"]) == option
			check(world.change_government_property("POL", property["key"], option) == not same, "every valid choice works")
			check(world.political_power("POL") == (100 if same else 0), "all options use same default cost")
	game._show_country("GER", false)
	await process_frame
	summary = game.control_details.get_node("PoliticalSummary")
	check(not summary.parliament.can_activate, "foreign parliament read only")
	summary.parliament._gui_input(click)
	check(game.active_feature == "", "foreign parliament does not open Government")
	check(game.control_panel.size.x < 500, "country panel retains narrow width")
	game._show_country("POL", false)
	summary = game.control_details.get_node("PoliticalSummary")
	summary.parliament._gui_input(click)
	await process_frame
	panel = game.control_details.get_node("PoliticalPanel")
	check("Republic" in Rules.PROPERTIES[0]["options"], "property rules available")
	world.countries["POL"]["starting_stats"]["political_power"] = 200.0
	world.political_power_modifiers.clear()
	world.hour = 23
	world.accumulator = 0
	world.speed = 1
	world.paused = true
	world.advance(.25)
	check(world.hour == 23 and world.political_power("POL") == 200, "paused gives no PP")
	world.paused = false
	world.accumulator = 1
	world.advance(0)
	check(world.hour == 24 and world.political_power("POL") == 201, "one PP at midnight")
	world.accumulator = 1
	world.advance(0)
	check(world.political_power("POL") == 201, "no duplicate daily grant")
	world.accumulator = 48
	world.advance(0)
	check(world.political_power("POL") == 203, "multiple crossed days counted")
	for speed: int in world.SPEEDS:
		world.hour = 23
		world.accumulator = 0
		world.speed = speed
		world.countries["POL"]["starting_stats"]["political_power"] = 200
		for tick: int in 4: world.advance(.25)
		check(world.political_power("POL") == 200 + world.day, "speed independent midnight income")
	world.countries["POL"]["starting_stats"]["political_power"] = 203
	world.speed = 1
	world.political_power_modifiers["POL"] = {"Test penalty":-2.0, "Test bonus":.25}
	check(is_equal_approx(world.daily_political_power("POL"), -.75), "additive daily breakdown")
	world.hour = 95
	world.accumulator = 1
	world.advance(0)
	check(is_equal_approx(world.political_power("POL"), 202.25), "negative daily gain applied")
	world.paused = true
	game._update_country_bar()
	var indicator = game.foundation.indicators["Political power"]["cell"]
	var tooltip: String = indicator.breakdown_bbcode()
	check("#ef8585]-0.75" in tooltip and "Test penalty" in tooltip and "Test bonus" in tooltip, "negative tooltip colored and itemized")
	world.political_power_modifiers.erase("POL")
	check("#76d9a1]+1.00" in indicator.breakdown_bbcode() and "Base gain" in indicator.breakdown_bbcode(), "positive base tooltip green")
	world.political_power_modifiers["POL"] = {"Test bonus":.5}
	var saved_pp: float = world.political_power("POL")
	var saved_properties: Dictionary = world.government_properties.duplicate(true)
	var save_path := "user://political_ui_test.bws"
	check(world.regions == map_before, "political operations leave map data untouched")
	check(world.save_game(save_path, game._view_state()), "save succeeds")
	world.countries["POL"]["starting_stats"]["political_power"] = 999
	world.government_properties.clear()
	world.political_power_modifiers.clear()
	check(game._load_from(save_path, false), "load succeeds")
	check(world.political_power("POL") == saved_pp and world.government_properties.get("POL", {}) == saved_properties.get("POL", {}), "balance and choices round trip")
	check(world.daily_political_power("POL") == 1.5, "modifiers round trip")
	check(world.paused, "loaded world paused")
	world.paused = false
	world.accumulator = 1
	world.advance(0)
	check(world.political_power("POL") == saved_pp, "load does not re-grant completed day")
	world.paused = true
	# Corrupted political fields must be rejected before changing the current world.
	var original := FileAccess.get_file_as_string(save_path)
	var envelope: Dictionary = JSON.parse_string(original)
	var payload: Dictionary = JSON.parse_string(envelope["payload"])
	payload["national"]["POL"]["government_properties"] = {"invalid":"value"}
	envelope["payload"] = JSON.stringify(payload)
	envelope["checksum"] = str(envelope["payload"]).sha256_text()
	var file := FileAccess.open(save_path, FileAccess.WRITE)
	file.store_string(JSON.stringify(envelope))
	file.close()
	check(world.load_game(save_path).is_empty(), "invalid political save rejected")
	check(world.political_power("POL") == saved_pp and world.government_properties.get("POL", {}) == saved_properties.get("POL", {}), "bad save leaves world unchanged")
	DirAccess.remove_absolute(ProjectSettings.globalize_path(save_path))
	DirAccess.remove_absolute(ProjectSettings.globalize_path(save_path + ".bak"))
	check(equivalent(world.regions, map_before), "map and population unchanged after JSON round trip")
	game._start_selection()
	check(world.government_properties.is_empty() and world.political_power_modifiers.is_empty(), "new campaign resets politics")
	print("POLITICAL_UI_RESULT checks=", checks, " failures=", failures)
	quit(0 if failures == 0 else 1)

func equivalent(a: Variant, b: Variant) -> bool:
	if a is Dictionary and b is Dictionary:
		if a.size() != b.size(): return false
		for key: Variant in a:
			if not b.has(key) or not equivalent(a[key], b[key]): return false
		return true
	if a is Array and b is Array:
		if a.size() != b.size(): return false
		for i: int in a.size():
			if not equivalent(a[i], b[i]): return false
		return true
	if (a is int or a is float) and (b is int or b is float):
		return absf(float(a) - float(b)) < 1e-10
	return a == b
