extends SceneTree
var checks := 0
var failures := 0
func check(ok: bool,message: String) -> void:
	checks+=1
	if not ok: failures+=1;push_error(message)
func _initialize() -> void: run.call_deferred()
func settle() -> void:
	await create_timer(.3).timeout
	await process_frame
func capture(label: String) -> void:
	var directory:=OS.get_environment("BUNNYWORLD_QA_DIR")
	if directory.is_empty() or DisplayServer.get_name()=="headless": return
	await RenderingServer.frame_post_draw
	root.get_texture().get_image().save_png(directory.path_join(label+".png"))
func run() -> void:
	root.size=Vector2i(1600,900)
	var game=load("res://main.tscn").instantiate();root.add_child(game)
	while not game.boot_complete: await process_frame
	game._start_selection();game.state.selected_country="JAP";game._begin_campaign();game.set_process(false)
	if game.focus_tween!=null: game.focus_tween.kill()
	var world=game.state
	game._show_feature("Economy");await settle()
	var panel=game.control_details.get_node("EconomyPanel")
	check(panel.tabs.get_child_count()==4 and panel.selected=="Overview","four economy subtabs")
	check(game.control_panel.size.x>=590,"economy uses wide shared panel")
	await capture("economy-overview")
	panel.tabs.get_node("Budget").pressed.emit();await process_frame
	check(panel.controls.size()==9,"two taxes and seven spending categories")
	var current: float=world.economy.nations["JAP"]["budget"]["education"]
	panel.controls["education"].value=0
	panel.controls["healthcare"].value=0
	panel.body.get_node("ApplyBudget").pressed.emit()
	check(world.economy.nations["JAP"]["budget"]["education"]==current and world.economy.nations["JAP"]["pending"]["education"]==0,"budget edits queue next month")
	check(world.agenda.queue.is_empty(),"budget adjustments do not create law reforms")
	await settle();await capture("economy-budget")
	panel.tabs.get_node("Energy").pressed.emit();await process_frame
	check(world.economy.nations["JAP"]["electricity"]["generation"]==null,"energy framework stays inactive")
	await capture("electricity-framework")
	game._show_feature("Research");await settle()
	var research=game.control_details.get_node("ResearchPanel")
	check("Education quality" in research.education_quality.text and "Research speed" in research.education_quality.text,"research displays quality and speed")
	await capture("research-quality")
	var quality: float=world.economy.nations["JAP"]["education_quality"]
	world.hour=743;world.accumulator=1;world.paused=false;world.advance(0);world.paused=true
	check(world.economy.nations["JAP"]["education_quality"]<quality and "−" not in research.education_quality.text,"funding cut updates live quality display")
	game._show_feature("Construction");await settle()
	var construction=game.control_details.get_node("ConstructionPanel")
	check(construction.manufactured_box.get_parent().name=="ManufacturedGoods","dedicated visible manufactured goods box")
	check(construction.manufactured_box.get_parent().get_index()<construction.queue_rows.get_parent().get_index(),"manufacturing box above construction queue")
	check(str(world.construction.manufactured_factories()) in construction.manufactured_box.text,"manufacturing assignment count displayed")
	await capture("construction-manufacturing")
	game._show_feature("Trade");await settle()
	var trade=game.control_details.get_node("TradePanel")
	check(trade.resource_buttons.size()==10,"ten clickable goods")
	trade.resource_buttons["food"].pressed.emit()
	check(trade.resource=="food" and trade.resource_buttons["food"].button_pressed,"food market selected")
	check(trade.capacity_labels["food"].text.ends_with(" MU"),"production uses market-flow units")
	await capture("food-trade")
	game._show_country("JAP",false);await settle()
	var population: Node=game.control_details.get_node("CountrySummary").get_child(0)
	var tooltip: String=population.breakdown_bbcode()
	check("Monthly change" in tooltip and "Healthcare quality" in tooltip and "[color=#76d9a1]" in tooltip,"population tooltip includes green growth and modifiers")
	world.economy.nations["JAP"]["food_stress"]=1
	tooltip=population.breakdown_bbcode()
	check("[color=#ef8585]" in tooltip and "Sustained food shortage" in tooltip,"negative growth/modifiers shown red")
	var tip: Control=population._make_custom_tooltip("Population")
	game.game_ui.add_child(tip);tip.position=Vector2(650,200)
	await settle();await capture("population-growth-tooltip")
	tip.queue_free()
	world.economy.nations["JAP"]["food_stress"]=0
	game._show_feature("Society");await settle()
	var society=game.control_details.get_node("SocietyPanel")
	check(not society.page.find_children("*","Label",true,false).filter(func(item: Label): return "Healthcare quality" in item.text).is_empty(),"healthcare quality displayed in Society")
	await capture("society-healthcare")
	root.size=Vector2i(1024,768)
	game._show_feature("Economy");await settle();game._position_panels()
	panel=game.control_details.get_node("EconomyPanel")
	panel.tabs.get_node("Budget").pressed.emit();await process_frame
	for input: SpinBox in panel.controls.values(): check(input.get_global_rect().end.x<=1024,"budget controls fit smaller screen")
	await capture("budget-smaller")
	game.queue_free();await process_frame
	print("ECONOMY_UI checks=",checks," failures=",failures)
	quit(0 if failures==0 else 1)
