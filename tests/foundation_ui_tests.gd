extends SceneTree
var failures := 0
func check(ok: bool, text: String) -> void:
	print(("PASS " if ok else "FAIL ")+text)
	if not ok: failures += 1
func _initialize() -> void: run.call_deferred()
func run() -> void:
	var main = load("res://main.tscn").instantiate()
	root.add_child(main)
	while not main.boot_complete: await process_frame
	main._start_selection()
	main._show_country("JAP",false)
	main._begin_campaign()
	var ui = main.foundation
	check(ui.toolbar.visible,"country toolbar available")
	check(ui.toolbar.get_child(3).disabled,"Research clearly planned")
	check(ui.indicators["Treasury"]["label"].text == "$528.00B","icon bar Treasury")
	main.state.paused = false
	ui.open_demographics("JAP")
	await process_frame
	check(main.state.paused and ui.demo_dialog.visible,"demographics pauses campaign")
	check(ui.demo_content.get_node("DemographicCharts").get_child_count() == 4,"all four demographic charts together")
	check(ui.demo_content.get_node("DemographicCharts").columns == 2,"two-column demographic grid")
	ui.demo_scope.select(1)
	ui.render_demographics()
	check(ui.demo_content.get_child(0).text != main.state.countries["JAP"]["name"],"State scope selectable")
	ui.demo_dialog.hide(); main._resume_after_dialog()
	check(not main.state.paused,"modal restores previous pause")
	ui.open_ledger()
	check(ui.ledger_rows.size() == main.state.countries.size(),"all countries in Ledger")
	ui.ledger_sort="population";ui.ledger_descending=true;ui.refresh_ledger()
	check(int(ui.ledger_rows[0]["population"]) >= int(ui.ledger_rows[-1]["population"]),"numeric descending population")
	ui.ledger_descending=false;ui.refresh_ledger()
	check(int(ui.ledger_rows[0]["population"]) <= int(ui.ledger_rows[-1]["population"]),"numeric ascending population")
	ui.ledger_search.text="Japan";ui.refresh_ledger()
	check(ui.ledger_rows.size()==1 and ui.ledger_rows[0]["tag"]=="JAP","Ledger country search")
	ui.ledger_dialog.hide();main._resume_after_dialog()
	ui.open_tension()
	check(ui.tension_dialog.visible and main.state.world_tension==0 and main.state.tension_events.is_empty(),"tension baseline and honest empty history")
	ui.tension_dialog.hide();main._resume_after_dialog()
	await process_frame
	main.queue_free()
	await process_frame
	quit(1 if failures else 0)
