extends SceneTree
var checks := 0
var failures := 0
func check(ok: bool, message: String) -> void:
	checks += 1
	if not ok: failures += 1; push_error(message)
func _initialize() -> void: run.call_deferred()
func settle() -> void:
	await create_timer(.3).timeout
	await process_frame
func capture(label: String) -> void:
	var directory := OS.get_environment("BUNNYWORLD_QA_DIR")
	if directory.is_empty() or DisplayServer.get_name() == "headless": return
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(directory.path_join(label + ".png"))
func run() -> void:
	root.size = Vector2i(1600,900)
	var game = load("res://main.tscn").instantiate()
	root.add_child(game)
	while not game.boot_complete: await process_frame
	game._start_selection()
	game.state.selected_country = "JAP"
	game._begin_campaign()
	game.set_process(false)
	if game.focus_tween != null: game.focus_tween.kill()
	var world = game.state
	game._show_feature("Research")
	await settle()
	var research = game.control_details.get_node("ResearchPanel")
	var tech := ""
	for key: String in world.research.catalog:
		if world.research.reason("JAP",key).is_empty(): tech = key; break
	world.research.start("JAP",research.institutions[0],tech)
	world.research.progress["JAP"][tech] = float(world.research.catalog[tech]["days"])*.55
	world.research.changed.emit()
	var card = research.institution_buttons[0]
	check(is_equal_approx(card.progress,.55) and card.fill.visible,"research slot progress fill")
	check(card.caption.text == card.text and card.caption.get_theme_color("font_color").a == 1,"progress text stays opaque in foreground")
	check(card.fill.get_index() < card.caption.get_parent().get_index(),"fill draws below text")
	await capture("research-progress")
	game._show_feature("Construction")
	check(game.panel_tweens.has(game.control_panel) and game.control_panel.modulate.a < 1,"feature switching animates")
	await settle()
	check(is_equal_approx(game.control_panel.position.x,game._panel_target(game.control_panel)),"slide lands on panel target")
	var construction = game.control_details.get_node("ConstructionPanel")
	check(construction.building_buttons.has("data_center"),"Data Center construction picker")
	game._show_feature("Trade")
	await settle()
	var trade = game.control_details.get_node("TradePanel")
	check(trade.resource_buttons.size() == 10,"all ten goods tabs")
	check(game.control_panel.size.x >= 590 and trade.size.x <= game.control_panel.size.x,"trade fits expanded panel")
	var money: Dictionary = world.countries["JAP"]["starting_stats"].duplicate(true)
	trade.resource_buttons["steel"].pressed.emit()
	check(trade.resource == "steel" and trade.resource_buttons["steel"].button_pressed,"resource tab changes ledger")
	check(world.countries["JAP"]["starting_stats"] == money,"trade scaffold has no economic effects")
	await capture("trade-framework")
	game._show_feature("Government")
	await settle()
	var panel = game.control_details.get_node("PoliticalPanel")
	var summary = panel.get_node("PoliticalSummary")
	check(summary.office_names["head_of_state"].text == "Emperor Akihito" and summary.office_names["head_of_government"].text == "Keizo Obuchi","leader names in correct offices")
	check(summary.office_portraits["head_of_state"].get_child_count() == 1 and summary.office_portraits["head_of_government"].get_child_count() == 1,"available MD portraits displayed")
	check("Liberal Democratic" in summary.government_caption.text,"government coalition displayed")
	check(summary.government_caption.size.y > 20,"government/coalition caption has visible height")
	check(panel.agenda_button.get_index() < panel.property_buttons["religion"].get_parent().get_parent().get_index(),"agenda above laws")
	world.countries["JAP"]["starting_stats"]["political_power"] = 5000
	world.change_government_property("JAP","form_of_government","Republic")
	world.agenda.advance_days(15)
	check(is_equal_approx(panel.agenda_button.progress,.5) and "15 days" in panel.agenda_button.text,"agenda button timer and fill")
	await capture("government-agenda")
	panel.agenda_button.pressed.emit()
	await settle()
	check(game.active_feature == "Agenda" and game.control_details.has_node("AgendaPanel/Reform_form_of_government"),"Agenda button opens queue")
	await capture("agenda-queue")
	var notices = game.game_ui.get_node("ResearchNotifications")
	world.agenda.advance_days(15)
	check(notices.transient.size() == 1,"agenda completion popup")
	world.completion_notice.emit("Construction completed","Data Center\nTokyo")
	check(notices.transient.size() == 2 and world.paused,"construction popup does not unpause")
	await settle()
	await capture("completion-popups")
	notices.expire(Time.get_ticks_msec()+60001)
	check(notices.transient.is_empty(),"popups expire after real minute while paused")
	world.research.progress["JAP"][tech] = float(world.research.catalog[tech]["days"])-.000001
	world.research.advance_days(1)
	check(world.research.notifications.size() == 1,"research popup tracked")
	notices.expire(Time.get_ticks_msec()+60001)
	check(world.research.notifications.is_empty(),"research popup expires too")
	root.size = Vector2i(1024,768)
	game._show_feature("Trade")
	await settle()
	game._position_panels()
	await process_frame
	trade = game.control_details.get_node("TradePanel")
	for button: Button in trade.resource_buttons.values():
		check(button.get_global_rect().end.x <= 1024 and button.get_global_rect().position.x >= 0,"resource selector fits smaller viewport")
	await capture("trade-smaller")
	game._show_sea(int(world.sea_regions.keys()[0]))
	check(world.selected_sea > 0,"sea region selected before Escape")
	var escape := InputEventKey.new()
	escape.keycode = KEY_ESCAPE
	escape.pressed = true
	game._input(escape)
	check(world.selected_sea == 0 and not game.territory_panel.visible,"Escape clears sea selection")
	world.agenda.reset()
	game._show_feature("Agenda")
	await settle()
	check(game.control_details.get_node("AgendaPanel").get_child_count() == 1,"idle agenda empty state")
	check(game.urban_scenery.SIZE_MULTIPLIER == 2.1 and game.urban_scenery.AREA_SCALE < 1,"urban buildings and area reduced")
	game.queue_free()
	await process_frame
	print("AGENDA_TRADE_UI checks=",checks," failures=",failures)
	quit(0 if failures == 0 else 1)
