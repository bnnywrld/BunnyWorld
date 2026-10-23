extends SceneTree
const Religions = preload("res://scripts/religion_catalog.gd")
const Pie = preload("res://scripts/pie_chart.gd")
const Rules = preload("res://scripts/government_rules.gd")
var checks := 0
var failures := 0
func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok: failures += 1; push_error(message)
func _initialize() -> void: run.call_deferred()
func capture(label: String) -> void:
	var directory := OS.get_environment("BUNNYWORLD_QA_DIR")
	if directory.is_empty() or DisplayServer.get_name() == "headless": return
	await process_frame
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(directory.path_join(label + ".png"))
func run() -> void:
	root.size = Vector2i(1600, 900)
	var game = load("res://main.tscn").instantiate()
	root.add_child(game)
	while not game.boot_complete: await process_frame
	game._start_selection()
	game.state.selected_country = "JAP"
	game._begin_campaign()
	game.set_process(false)
	if game.focus_tween != null: game.focus_tween.kill()
	game.foundation.open_country_demographics()
	await process_frame
	await process_frame
	check(game.active_feature == "Society", "toolbar opens dedicated Society")
	var panel = game.control_details.get_node("SocietyPanel")
	check(panel.tabs.get_child_count() == 4, "four Society sections")
	check(panel.find_children("Chart_*", "", true, false).size() == 4, "all four demographic charts together")
	check(game.control_panel.size.x <= 610, "same shared panel dimensions")
	for row: Node in panel.page.get_children():
		if row is HBoxContainer:
			check(row.size.y < 35, "compact statistic row")
			check(row.get_child(1).size.x > 5, "statistic value has readable width")
	var initial: Dictionary = game.state.society.export_state()
	for tab: Button in panel.tabs.get_children():
		tab.pressed.emit()
		await process_frame
		check(panel.selected == tab.text and tab.button_pressed, "subtab switches")
		for button: Button in panel.page.find_children("*", "Button", true, false):
			if "Planned" in button.text: check(button.disabled, "unfinished actions disabled")
	check(initial == game.state.society.export_state(), "browsing tabs has no simulation effects")
	game.state.hour = 743
	game.state.accumulator = 1
	game.state.paused = false
	game.state.advance(0)
	game.state.paused = true
	game._process(0)
	check(game.society_seen_revision == game.state.society.revision, "monthly revision reaches visible UI")
	panel.selected = "Population"
	panel.refresh()
	await process_frame
	check(panel.page.get_child(0).get_child(0).text.ends_with(preload("res://scripts/display_format.gd").people(game.state.country_metrics("JAP")["population"])), "visible population matches authoritative states after growth")
	await capture("society-population")
	panel.selected = "Public Attitudes"
	panel.refresh()
	await capture("society-attitudes")
	panel.selected = "Political Support"
	panel.refresh()
	await process_frame
	await capture("society-parties")
	var party_button: Button = panel.page.get_node("Party_1")
	party_button.pressed.emit()
	await process_frame
	check(panel.party_popup.visible and "Liberal Democratic Party" in panel.party_popup.content.get_child(0).text, "party details and initials fallback")
	var popup = panel.party_popup
	game._show_feature("Government")
	await process_frame
	check(not is_instance_valid(popup), "party popup disappears with owner tab")
	var government = game.control_details.get_node("PoliticalPanel")
	var summary = government.get_node("PoliticalSummary")
	var snapshot: Array = game.state.society.seat_parties("JAP")
	check(summary.parliament.party_seats == snapshot, "Government uses shared parliament snapshot")
	var religion: Dictionary = {}
	for property: Dictionary in Rules.PROPERTIES:
		if property["key"] == "religion": religion = property
	government.open_property(religion)
	await process_frame
	check(government.choice_dialog.title == "Religion & State", "renamed law")
	check(government.choice_buttons["Theocracy"].disabled, "faith requirement visible")
	game.state.countries["JAP"]["starting_stats"]["political_power"] = 2000
	government.affiliation_picker.select(government.affiliations.find("Buddhist")+1)
	government.affiliation_picker.item_selected.emit(government.affiliation_picker.selected)
	check(not government.choice_buttons["State Religion"].disabled, "explicit affiliation unlocks choice")
	await capture("society-religion-law")
	government.choice_buttons["State Religion"].pressed.emit()
	check(game.state.society.nations["JAP"]["affiliation"] == "", "UI proposal defers affiliation")
	game.state.agenda.advance_days(120)
	check(game.state.society.nations["JAP"]["affiliation"] == "Buddhist" and game.state.political_power("JAP") == 1600, "UI law applies one PP charge")
	game._show_country("JAP", false)
	await process_frame
	summary = game.control_details.get_node("PoliticalSummary")
	check(summary.parliament.party_seats == snapshot, "country inspector shares same seats")
	var motion := InputEventMouseMotion.new()
	motion.position = summary.parliament.seats[0]
	summary.parliament._gui_input(motion)
	check("seats" in summary.parliament.tooltip_text and "support" in summary.parliament.tooltip_text, "seat hover shows party data")
	var first := Pie.new()
	var second := Pie.new()
	first.configure({"Sunni":50,"Atheist":10}, "religion")
	second.configure({"Catholic":30,"Atheist":40,"Sunni":20}, "religion")
	check(first.colors["Sunni"] == second.colors["Sunni"] and first.colors["Atheist"] == second.colors["Atheist"], "chart color independent of order and country")
	first.free()
	second.free()
	game._show_feature("Society")
	await process_frame
	root.size = Vector2i(1024,768)
	game._position_panels()
	await process_frame
	await process_frame
	panel = game.control_details.get_node("SocietyPanel")
	check(panel.get_global_rect().end.x < 1024 and panel.tabs.get_global_rect().end.x < 1024, "Society fits narrower viewport")
	await capture("society-small")
	game.queue_free()
	await process_frame
	print("SOCIETY_UI checks=", checks, " failures=", failures)
	quit(0 if failures == 0 else 1)
