extends SceneTree
const Rules = preload("res://scripts/organization_rules.gd")
var checks := 0
var failures := 0
func check(value: bool, message: String) -> void:
	checks += 1
	if not value:
		failures += 1
		push_error(message)
func _initialize() -> void: run.call_deferred()
func click(button: Button) -> void:
	var position := button.get_global_rect().get_center()
	var motion := InputEventMouseMotion.new()
	motion.position = position
	root.push_input(motion, true)
	for pressed: bool in [true, false]:
		var event := InputEventMouseButton.new()
		event.position = position
		event.button_index = MOUSE_BUTTON_LEFT
		event.pressed = pressed
		root.push_input(event, true)
	await process_frame
func run() -> void:
	root.size = Vector2i(1440, 900)
	var game = load("res://main.tscn").instantiate()
	root.add_child(game)
	while not game.boot_complete: await process_frame
	game._start_selection()
	game.state.selected_country = "GER"
	game._begin_campaign()
	var world = game.state
	check(world.organizations.size() == 19, "preserve existing active organizations")
	check(Rules.definitions().size() == 44, "all eight types represented in directory")
	for oid: String in world.organizations:
		check(world.organizations[oid]["members"] == world.database["organizations"][oid]["members"], "no silently imported membership: " + oid)
		check(Rules.full_members(world.organizations[oid]).size() == world.organizations[oid]["members"].size(), "existing status seeded as full: " + oid)
	check(Rules.valid_state(world.organizations, world.countries), "scenario alliance exclusivity")
	check(world.trade_integration_level("GER") == 3, "EU scenario integration level")
	var test_orgs: Dictionary = world.organizations.duplicate(true)
	test_orgs["EU"]["opt_out_levels"]["GER"] = 1
	world.organizations = test_orgs
	check(world.trade_integration_level("GER") == 1, "per-country integration opt-out")
	world.organizations["EU"]["statuses"]["GER"] = "suspended"
	check(world.trade_integration_level("GER") == 0, "suspended country receives no trade integration")
	check(world.memberships("GER").has("EU") and not world.full_memberships("GER").has("EU"), "suspension remains visible")
	world.organizations = world.database["organizations"].duplicate(true)
	Rules.seed(world.organizations)
	var invalid: Dictionary = world.organizations.duplicate(true)
	invalid["CSTO"]["members"].append("USA")
	invalid["CSTO"]["statuses"]["USA"] = "full"
	check(not Rules.valid_state(invalid, world.countries), "two exclusive factions rejected")
	invalid["CSTO"]["statuses"]["USA"] = "partner"
	check(Rules.valid_state(invalid, world.countries), "partner does not consume faction slot")
	invalid["CSTO"]["statuses"]["USA"] = "made_up"
	check(not Rules.valid_state(invalid, world.countries), "invalid membership status rejected")
	check(Rules.display_name(world.organizations["OAU"], {"year":2000,"month":1,"day":1}) == "Organization of African Unity", "OAU at scenario start")
	check(Rules.display_name(world.organizations["OAU"], {"year":2002,"month":7,"day":9}) == "African Union", "dated AU name")
	check(Rules.display_name(world.organizations["CSTO"], {"year":2000,"month":1,"day":1}) == "Collective Security Treaty", "pre-CSTO treaty label")
	world.organizations["EU"]["statuses"]["GER"] = "associate"
	world.organizations["EU"]["opt_out_levels"]["GER"] = 1
	var saved: Dictionary = world.organizations.duplicate(true)
	var path := "user://organization_test.json"
	check(world.save_game(path, game._view_state()), "save organization statuses and opt-outs")
	world.organizations["EU"]["statuses"]["GER"] = "full"
	check(not world.load_game(path).is_empty(), "load new organization save")
	for oid: String in saved:
		check(world.organizations[oid]["members"] == saved[oid]["members"] and world.organizations[oid]["statuses"] == saved[oid]["statuses"], "membership and statuses round-trip: " + oid)
		check(int(world.organizations[oid]["integration_level"]) == int(saved[oid]["integration_level"]) and world.organizations[oid]["opt_out_levels"].keys() == saved[oid]["opt_out_levels"].keys(), "integration level and opt-outs round-trip: " + oid)
		for tag: String in saved[oid]["opt_out_levels"]:
			check(int(world.organizations[oid]["opt_out_levels"][tag]) == int(saved[oid]["opt_out_levels"][tag]), "opt-out value survives JSON numeric conversion")
		check(world.organizations[oid]["hq"] == saved[oid]["hq"], "headquarters metadata round-trip: " + oid)
	DirAccess.remove_absolute(path)
	DirAccess.remove_absolute(path + ".bak")
	world.organizations["EU"]["statuses"]["GER"] = "full"
	world.organizations["EU"]["opt_out_levels"].clear()
	var pp: float = world.political_power("GER")
	var opinion: float = world.opinion("GER", "FRA")
	game._show_feature("Organizations")
	await create_timer(.25).timeout
	var ui = game.control_details.get_node("OrganizationsPanel")
	check(game.foundation.feature_buttons.has("Organizations"), "dedicated navigation button")
	check(ui.card_buttons.size() == world.memberships("GER").size(), "cards only for player memberships")
	check(not ui.card_buttons.has("ASEAN"), "not selected-country or global list by default")
	# Sorted EU card is within the scrolled viewport for Germany.
	await click(ui.card_buttons["EU"])
	await process_frame
	check(ui.selected_organization == "EU", "pointer click opens organization card")
	check(ui.member_buttons.size() == 15, "member detail contains all EU members")
	check(ui.detail_tabs.get_tab_count() == 2, "members and features tabs")
	check(ui.detail_tabs.get_tab_title(0) == "Members", "members shown first")
	check(ui.detail_tabs.get_tab_title(1) == "Features", "features tab available")
	ui.directory = true
	ui.show_list()
	check(ui.card_buttons.size() == 44, "directory includes inactive definitions")
	ui.open_organization("UN")
	check(ui.member_buttons.is_empty() and not world.organizations.has("UN"), "pending UN does not invent members")
	check(world.political_power("GER") == pp and world.opinion("GER", "FRA") == opinion, "browsing has no PP or opinion side effects")
	ui.directory = false
	ui.show_list()
	await process_frame
	# Country panels can be hidden by map inspector, but switching to HQ must not hide Organizations.
	game._open_organization("EU")
	await create_timer(.25).timeout
	check(game.control_panel.visible and game.active_feature == "Organizations", "map inspector preserves own organizations tab")
	var hq: Dictionary = game.organization_hq_places["EU"]
	check(not hq.is_empty() and hq["country"] == "BEL", "EU headquarters linked to Belgium place catalog")
	var uv: Vector2 = hq["uv"]
	game.planet.rotation = Vector3((.5-uv.y)*PI, -(uv.x-.5)*TAU, 0)
	game.distance = 2.2
	game._update_camera_pose()
	game._update_cities()
	check(game.city_layer.markers.size() == 1, "HQ visible at world zoom")
	for marker: Dictionary in game.city_layer.markers:
		check(marker["capital"] and marker.get("organization") == "EU", "only HQ star; no member capital")
	game._open_organization("G7")
	game._update_cities()
	check(game.city_layer.markers.is_empty(), "rotating chair has no fake headquarters")
	game._open_organization("OPEC")
	check(game.organization_hq_places["OPEC"]["country"] == "AUS", "HQ may be in a nonmember host country")
	game._map_changed(0)
	game.distance = 1.2
	game._update_camera_pose()
	game._update_cities()
	check(game.city_layer.markers.any(func(m: Dictionary): return not m.has("organization")), "ordinary city markers restored outside organization mode")
	var projections: int = game.city_projection_tests
	game._open_organization("EU")
	game._update_cities()
	for i: int in 20: game._update_cities()
	check(game.city_projection_tests == projections, "HQ mode does not scan national cities")
	game._show_feature("Research")
	await process_frame
	check(not is_instance_valid(ui), "organizations panel freed on tab switch")
	game._show_feature("Organizations")
	await process_frame
	await create_timer(.2).timeout
	ui = game.control_details.get_node("OrganizationsPanel")
	root.size = Vector2i(1024, 768)
	await process_frame
	await process_frame
	check(game.get_viewport_rect().encloses(game.control_panel.get_global_rect()), "organizations panel fits smaller viewport")
	var qa_dir := OS.get_environment("BUNNYWORLD_QA_DIR")
	if DisplayServer.get_name() != "headless" and not qa_dir.is_empty():
		await process_frame
		await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png(qa_dir.path_join("organizations.png"))
		ui.open_organization("EU")
		ui.detail_tabs.current_tab = 1
		await process_frame
		await process_frame
		await RenderingServer.frame_post_draw
		root.get_texture().get_image().save_png(qa_dir.path_join("organization_features.png"))
	game.queue_free()
	await process_frame
	print("ORGANIZATIONS_RESULT checks=", checks, " failures=", failures)
	quit(0 if failures == 0 else 1)
