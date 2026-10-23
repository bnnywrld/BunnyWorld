extends SceneTree
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
	root.size = Vector2i(1600,900)
	var game = load("res://main.tscn").instantiate()
	root.add_child(game)
	while not game.boot_complete: await process_frame
	game._start_selection()
	game.state.selected_country = "JAP"
	game._begin_campaign()
	game.set_process(false)
	if game.focus_tween != null: game.focus_tween.kill()
	game._show_country("JAP",false)
	await process_frame
	await process_frame
	var currency: Label = game.control_details.get_node("CountrySummary").find_child("CurrencyName",true,false)
	check(currency.text == game.currency_names["JAP"]["name"] and currency.size.y >= 30 and currency.size.x > 30, "currency name has visible dimensions")
	await capture("currency-overview")
	game._show_feature("Government")
	await process_frame
	await process_frame
	var summary = game.control_details.get_node("PoliticalPanel/PoliticalSummary")
	var parliament = summary.parliament
	check(parliament.size.y >= 132 and parliament.size.x >= 230, "large Government parliament restored")
	check("20 Oct 2000" in summary.next_election.text, "MD next election restored below parliament")
	check(summary.next_election.get_global_rect().position.y >= parliament.get_global_rect().end.y, "election below seats")
	var counts: Dictionary = {}
	for party: Dictionary in parliament.seat_info:
		if not party.is_empty(): counts[party["id"]] = int(counts.get(party["id"],0))+1
	for party: Dictionary in parliament.party_seats: check(counts[party["id"]] == party["seats"], "party wedge preserves exact seat allocation")
	var seat := -1
	for i: int in parliament.seat_info.size():
		var party: Dictionary = parliament.seat_info[i]
		if not party.is_empty() and party["id"] == "1": seat = i; break
	var motion := InputEventMouseMotion.new()
	motion.position = parliament.seats[seat]
	parliament._gui_input(motion)
	check(parliament.hovered_party() == "1" and "Liberal Democratic Party" in parliament.tooltip_text, "hover targets whole party")
	check(parliament.group_shapes.has("1") and not parliament.group_shapes["1"].is_empty(), "party has union outline")
	for i: int in parliament.seats.size():
		var belongs := false
		for polygon: PackedVector2Array in parliament.group_shapes["1"]:
			if Geometry2D.is_point_in_polygon(parliament.seats[i],polygon): belongs = true
		check(belongs == (parliament.seat_info[i].get("id","") == "1"), "outline groups this party and excludes other seats")
	await process_frame
	await capture("parliament-party-highlight")
	game._show_country("GER",false)
	await process_frame
	await process_frame
	var actions = game.diplomacy_actions
	check(actions.action_rows.get_child_count() == 83, "all diplomatic actions accessible")
	for button: Button in actions.action_rows.get_children(): check(button.disabled, "diplomatic action inactive")
	for id: String in ["propose_mutual_investment_treaty","diplo_action_assume_debt","request_mil_gnss_access","war"]:
		check(actions.action_rows.has_node("Action_"+id), "MD action present")
	var scroll: ScrollContainer = actions.action_rows.get_parent()
	check(scroll.get_v_scroll_bar().max_value > scroll.size.y, "long diplomacy list scrolls")
	actions.action_filter.select(4)
	actions.action_filter.item_selected.emit(4)
	check(actions.action_rows.get_child_count() == 18, "space category filters MD satellite access actions")
	await process_frame
	await capture("diplomacy-actions")
	actions.arrow.pressed.emit()
	check(not actions.frame.visible, "actions still collapse behind arrow")
	game._show_country("SIN",false)
	game.state.selected_region = 983
	game._show_territory()
	await process_frame
	await process_frame
	var cores = game.territory_details.get_node("Rights_Cores")
	var claims = game.territory_details.get_node("Rights_Claims")
	check(cores.get_child_count() == 1 and claims.get_child_count() == 1, "MD Singapore cores and claims shown")
	check(cores.get_child(0).tooltip_text == "Singapore" and claims.get_child(0).tooltip_text == "Malaysia", "flag tooltips show country names")
	for flow: Control in [cores,claims]:
		var button: Button = flow.get_child(0)
		check(button.custom_minimum_size == Vector2(34,24) and button.get_child_count() > 0, "small flag textures in rights rows")
	check(game.territory_details.has_node("BuildingWorkers"), "state staffing summary visible")
	var resource_state := ""
	for sid: String in game.state.regions:
		if game.state.regions[sid]["owner"] == "GER" and game.state.regions[sid]["resources"].size() >= 2: resource_state = sid; break
	check(not resource_state.is_empty(), "resource-rich state available")
	game.state.selected_region = int(resource_state)
	game._show_territory()
	await process_frame
	await process_frame
	check(game.territory_details.get_node("StateResources").find_children("Resource_*","HBoxContainer",true,false).size() >= 2, "state resource quantities visible")
	await capture("state-resources-workers")
	root.size = Vector2i(1024,768)
	game._position_panels()
	await process_frame
	await process_frame
	check(game.territory_panel.size.x <= game.get_viewport_rect().size.x, "state inspector fits narrow window")
	await capture("state-small")
	game.queue_free()
	await process_frame
	print("STATE_ECONOMY_UI checks=",checks," failures=",failures)
	quit(0 if failures==0 else 1)
