extends SceneTree
const Rules = preload("res://scripts/government_rules.gd")
const Format = preload("res://scripts/display_format.gd")
const Surface = preload("res://scripts/relief_surface.gd")
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
	game.state.selected_country = "GER"
	game._begin_campaign()
	if game.focus_tween != null: game.focus_tween.kill()
	game._focus_country("GER",false)
	var world = game.state
	var model = world.construction
	var sid := str(int(world.countries["GER"]["capital"]))
	var region: Dictionary = world.regions[sid]
	var stats: Dictionary = world.countries["GER"]["starting_stats"]
	stats["treasury_usd"] = 100e9
	stats["debt_usd"] = 0
	check(model.add(sid,"industrial_complex"), "queue first factory")
	var job: Dictionary = model.queue[0]
	var id: int = job["id"]
	job["progress"] = 123
	check(model.add(sid,"industrial_complex") and model.queue.size() == 1 and job["next_levels"].size() == 1, "same state/building forms one two-level group")
	check(job["progress"] == 123 and model.pending(sid,"industrial_complex") == 2, "adding a level preserves work and reserves both slots")
	check(model.allocations()[id] == 10, "group has one ten-factory allocation")
	var built: int = region["buildings"]["industrial_complex"]
	job["progress"] = float(job["points"])-1
	model.advance_days(1)
	check(region["buildings"]["industrial_complex"] == built+1 and model.queue.size() == 1, "one level completes individually")
	check(job["id"] == id and job["next_levels"].is_empty() and job["progress"] == 0, "next level starts with same group and no excess daily progress")
	check(model.add(sid,"industrial_complex"), "append a third level")
	job["progress"] = float(job["points"])*.5
	var cash: float = stats["treasury_usd"]
	var price: float = model.catalog["industrial_complex"]["money_usd"]
	check(model.cancel(id) and is_equal_approx(stats["treasury_usd"],cash+price*1.5), "cancellation refunds unfinished head and all waiting levels")
	check(model.pending(sid,"industrial_complex") == 0, "group cancellation frees all reservations")
	stats["treasury_usd"] = 0
	check(model.add(sid,"industrial_complex") and model.add(sid,"industrial_complex"), "group can borrow separately for each level")
	var debt: float = stats["debt_usd"]
	job = model.queue[0]
	job["progress"] = float(job["points"])*.5
	check(model.cancel(int(job["id"])) and is_equal_approx(stats["debt_usd"],debt-price*1.5), "group refund reverses unfinished borrowing across levels")
	stats["treasury_usd"] = 100e9
	for property: Dictionary in Rules.PROPERTIES:
		var options: Array = property["options"]
		check("Semi-Presidential" not in options, "removed executive option")
		check(Rules.change_cost(property["key"],options[0],options[1]) == 100, "adjacent law change costs 100 PP")
		if options.size() > 2:
			check(Rules.change_cost(property["key"],options[0],options[2]) == (100 if property["key"] in Rules.UNORDERED else 400), "larger jumps cost quadratically only on ordered scales")
	stats["political_power"] = 1000
	world.government_properties["GER"]["speech_press"] = "Free"
	check(world.change_government_property("GER","speech_press","State-Controlled") and stats["political_power"] == 600, "world charges two-step jump exactly 400 PP")
	world.agenda.advance_days(120)
	check(Format.people(10000000) == "10M" and Format.people(1250000) == "1.25M" and Format.people(900) == "900", "readable population counts")
	check(game.currency_names.size() == 224 and game.currency_names["JAP"]["name"] == "Japanese yen", "national currency names loaded")
	game._show_feature("Government")
	await create_timer(.2).timeout
	var politics: Node = game.control_details.get_node("PoliticalPanel")
	check(politics.property_buttons["speech_press"].text.contains("State-Controlled"), "law tile displays its current choice")
	await capture("government-readable")
	game._show_country("KOR",false)
	await create_timer(.2).timeout
	check(game.control_heading.find_child("HeaderRelations",true,false).get_child_count() == 2, "relations live beside the country title")
	check(game.control_details.get_node("CountrySummary").get_child_count() == 12, "overview includes labor, unemployment, debt, factories and currency")
	check(game.control_details.find_child("NationalWorkforce",true,false) == null, "separate workforce panel removed")
	check(game.control_details.get_node("PoliticalSummary").government_type.text == Rules.government_title(world.government_properties["KOR"]), "dynamic government form above country parliament")
	check(game.diplomacy_actions.visible and not game.diplomacy_actions.collapsed, "diplomatic actions open alongside country")
	game.diplomacy_actions.arrow.pressed.emit()
	check(not game.diplomacy_actions.frame.visible and game.diplomacy_actions.arrow.visible, "actions collapse to an edge arrow")
	game.diplomacy_actions.arrow.pressed.emit()
	await capture("country-readable")
	world.relation_offsets["GER|KOR"] = 5
	check(game.opinion_labels[0].breakdown_bbcode().contains("76d9a1"), "positive opinion modifiers are green")
	world.relation_offsets["GER|KOR"] = -5
	check(game.opinion_labels[0].breakdown_bbcode().contains("ef8585"), "negative opinion modifiers are red")
	game._show_feature("Research")
	await create_timer(.2).timeout
	check(not is_instance_valid(game.diplomacy_actions), "actions removed with owning country tab")
	var research: Node = game.control_details.get_node("ResearchPanel")
	research.open_tree(research.institutions[0])
	await process_frame
	check(research.tech_window.size.x > 1400 and research.tech_window.size.y > 700, "research window fills the screen")
	check(research.tech_buttons.values()[0].size.x <= 170 and research.tech_buttons.values()[0].size.y <= 65, "smaller technology cards")
	await capture("research-compact")
	root.size = Vector2i(1100,768)
	await process_frame
	await process_frame
	check(game.get_viewport_rect().encloses(research.tech_window.get_global_rect()), "large tree shrinks to fit a smaller viewport")
	root.size = Vector2i(1600,900)
	await process_frame
	await process_frame
	game._show_feature("Construction")
	await create_timer(.2).timeout
	game._select_construction_building("industrial_complex")
	for key: String in ["industrial_complex","offices","arms_factory","microchip_plant","agriculture_district"]:
		model.add(sid,key)
		model.add(sid,key)
	game._construction_changed()
	await process_frame
	await process_frame
	var construction: Node = game.control_details.get_node("ConstructionPanel")
	check(construction.queue_rows.get_child(0).size.y < 100, "compact construction queue rows")
	await capture("construction-compact")
	game._select_construction_building("internet_station")
	check(game.legend.text.contains("level 0"), "network selection switches legend to levels")
	if DisplayServer.get_name() != "headless":
		var color: Color = game.palette_texture.get_image().get_pixel(int(sid),0)
		var expected := Color("142f4a").lerp(Color("efd28a"),float(region["buildings"].get("internet_station",0))/10.0)
		check(maxf(absf(color.r-expected.r),maxf(absf(color.g-expected.g),absf(color.b-expected.b))) <= 1.0/255, "network map uses built internet level within texture quantization")
	await capture("construction-network")
	game._map_changed(1)
	var index := -1
	for i: int in game.org_type_picker.item_count:
		if game.org_type_picker.get_item_metadata(i) == "security": index = i
	game._organization_type_changed(index)
	check(game.alliances_overview and game.org_picker.get_item_text(0) == "All alliances", "security filter defaults to all-alliance overview")
	for oid: String in game.org_ids:
		check(oid == "__alliances__" or world.organizations[oid]["type"] == "security", "organization list is filtered")
	if DisplayServer.get_name() != "headless":
		var color: Color = game.palette_texture.get_image().get_pixel(int(sid),0)
		var leader: Array = world.country_color("USA")
		check(color.is_equal_approx(Color(float(leader[0])/255,float(leader[1])/255,float(leader[2])/255)), "NATO members use USA color")
	var alliance_labels := 0
	for entry: Dictionary in game.country_label_layer.entries:
		if entry.get("alliance",false): alliance_labels += 1
		if entry["tag"] == "JAP":
			var center := Vector3.ZERO
			for province: Dictionary in world.provinces.values():
				if world.regions[str(int(province["region"]))]["owner"] == "JAP": center += Surface.unit_point(Vector2(province["map_center"][0],province["map_center"][1])) * float(province["area_km2"])
			check(center.normalized().distance_to(entry["anchor"].normalized()) < .00001, "country name is centered on area-weighted land mass")
	check(alliance_labels == 2, "both scenario alliances have geographic labels")
	game.distance = 2.7
	for entry: Dictionary in game.country_label_layer.entries:
		if entry["tag"] == "NATO":
			var uv := Surface.uv_of(entry["anchor"].normalized())
			game.planet.rotation = Vector3((.5-uv.y)*PI,-(uv.x-.5)*TAU,0)
	game._update_camera_pose()
	game.country_label_layer.update_view(true)
	check(not game.country_label_layer.visible_labels.is_empty(), "alliance label is visible over its centroid")
	await capture("alliances-overview")
	root.size = Vector2i(1100,768)
	await process_frame
	await process_frame
	game._position_panels()
	check(not game.map_box.get_global_rect().intersects(game.top_left_box.get_global_rect()), "organization selectors avoid the toolbar on smaller screens")
	root.size = Vector2i(1600,900)
	await process_frame
	await process_frame
	var directory := OS.get_environment("BUNNYWORLD_QA_DIR")
	if directory.is_empty(): directory = OS.get_environment("TEMP").path_join("bunnyworld-ui-qa")
	var path := directory.path_join("ui-roundtrip.json")
	check(world.save_game(path,game._view_state()), "save grouped construction and alliance view")
	model.queue.clear()
	check(game._load_from(path,false), "load grouped construction and alliance view")
	check(model.queue.size() == 5 and model.queue[0]["next_levels"].size() == 1, "grouped levels survive save/load")
	check(game.alliances_overview and game.organization_type == "security", "organization filter survives save/load")
	var saved_regions := {}
	for state_id: String in world.regions: saved_regions[state_id] = world.regions[state_id]
	var saved: Dictionary = model.export_state()
	saved["queue"][0]["next_levels"][0]["cash"] = -1
	check(not model.valid(saved,saved_regions,"GER"), "invalid future-level payments are rejected")
	saved = model.export_state()
	var duplicate: Dictionary = saved["queue"][0].duplicate(true)
	duplicate["id"] = saved["next_id"]
	saved["next_id"] += 1
	saved["queue"].append(duplicate)
	check(not model.valid(saved,saved_regions,"GER"), "duplicate saved construction groups are rejected")
	for i: int in game.org_type_picker.item_count:
		game._organization_type_changed(i)
		check(game.org_picker.disabled == game.org_ids.is_empty(), "all organization types handle empty lists")
	game.queue_free()
	await process_frame
	print("UI_IMPROVEMENTS checks=",checks," failures=",failures)
	quit(0 if failures == 0 else 1)
