extends SceneTree
var failures := 0
var report: Array[String] = []
var out := OS.get_environment("BUNNY_VALIDATION_DIR")
func _initialize() -> void: run.call_deferred()
func check(ok: bool, description: String) -> void:
	var line := ("PASS " if ok else "FAIL ") + description
	report.append(line);print(line)
	if not ok: failures += 1
func settle() -> void:
	for i: int in 5: await process_frame
	await create_timer(.24).timeout
func capture(main, name: String) -> void:
	if DisplayServer.get_name()=="headless":
		await settle();return
	await settle();await RenderingServer.frame_post_draw
	main.get_viewport().get_texture().get_image().save_png(out.path_join(name+".png"))
func save_report() -> void:
	var file := FileAccess.open(out.path_join("ui_results.json"), FileAccess.WRITE)
	file.store_string(JSON.stringify({"failures":failures,"checks":report},"\t"))
func run() -> void:
	var main = load("res://main.tscn").instantiate()
	root.add_child(main)
	while not main.boot_complete: await process_frame
	check(str(ProjectSettings.get_setting("application/config/version"))=="0.2.0.6","application version")
	check(str(ProjectSettings.get_setting("display/window/stretch/aspect"))=="expand","aspect expands without side bars")
	main._start_selection();main._show_country("POL", false);main._begin_campaign();await settle()
	check(main.view_container.position.is_equal_approx(Vector2.ZERO) and main.view_container.size.is_equal_approx(main.size),"globe fills entire window behind top boxes")
	check(main.clock_box.position.y==0 and main.top_left_box.position.y==0,"stats and clock attached to same top edge")
	check(main.top_left_box.size.x+main.clock_box.size.x+16<=main.size.x,"top groups do not overlap")
	check(main.map_picker.get_parent().get_child(main.map_picker.get_parent().get_child_count()-1).name=="FindPlace","map picker beside search")
	check(not main.title_label.visible and not main.status.visible,"country header and footer stay removed")
	check("M" in main.foundation.indicators["Population"]["label"].text and "38,635,969" in main.foundation.indicators["Population"]["cell"].tooltip_text,"short population with exact hover value")
	check("K" in main.foundation.indicators["GDP per capita"]["label"].text and "Exact:" in main.foundation.indicators["GDP per capita"]["cell"].tooltip_text,"short per-capita number with exact hover value")
	var captions := PackedStringArray()
	for button: Button in main.foundation.toolbar.get_children():
		captions.append(button.tooltip_text)
		check(not button.disabled if button.name=="NationalDemographicsShortcut" else button.disabled,"national section availability: "+button.tooltip_text)
	for caption: String in ["Economy", "Construction", "Production", "Diplomacy", "Trade", "Military", "Intelligence", "Space Exploration"]:
		check((caption+" · Planned") in captions,"toolbar section: "+caption)
	await capture(main,"campaign_1440")
	main.foundation.toolbar.get_node("NationalDemographicsShortcut").pressed.emit();await settle()
	check(main.control_panel.visible,"demographics shortcut opens inline national profile")
	var national = main.control_details.get_node("NationalDemographics")
	check(national.get_meta("scope")=="national" and int(national.get_meta("population"))==main.state.country_metrics("POL")["population"],"country chart uses national population")
	for key: String in ["age","religion","education","activity"]:
		national.selectors.get_node(key).pressed.emit()
		check(national.selected==key and national.page.get_child(1).get_child_count()==2,"single national chart switches: "+key)
	check(national.get_index()>2 and main.control_details.get_child(national.get_index()-1) is Label and main.control_details.get_child(national.get_index()-1).text==main.state.countries["POL"]["outlook"],"outlook above national demographics")
	main._close_panels()
	if main.focus_tween!=null:main.focus_tween.kill()
	main.planet.rotation=Vector3(deg_to_rad(35.686963),-deg_to_rad(139.749462),0)
	main.distance=1.025;main._update_camera_pose();main._update_detail_patch();main.show_regions=true
	await settle()
	var center := Vector2(main.world_view.size)*.5
	main.inspect_region=main._region_at(center);main.inspect_province=main._province_at(center);main._show_country("JAP",false);await settle()
	check(main.territory_clip.visible and main.territory_handle.visible,"territory and attached arrow appear")
	check(main.territory_clip.position.x+main.territory_clip.size.x<=main.right_panel.position.x+1,"foreign drawer is left of diplomacy")
	check(main.territory_clip.position.y>=main.size.y*.5-1 and main.territory_panel.size.y<=main.size.y*.5,"drawer occupies lower half")
	check(is_equal_approx(main.territory_panel.size.x,300),"wider 300-pixel territory drawer")
	var state_chart = main.territory_details.get_node("StateDemographics")
	check(int(state_chart.get_meta("population"))==int(main.state.regions[str(main.state.selected_region)]["population"]) and state_chart.get_meta("scope")=="state","territory chart uses selected State only")
	for key: String in ["age","religion","education","activity"]:
		state_chart.selectors.get_node(key).pressed.emit();check(state_chart.selected==key,"State chart switches: "+key)
	await capture(main,"foreign_expanded")
	var old_arrow: String=main.territory_handle.text
	main.territory_handle.pressed.emit();await settle()
	check(main.territory_collapsed and main.territory_handle.visible and main.territory_handle.text!=old_arrow,"collapse leaves handle and reverses arrow")
	check(is_equal_approx(main.territory_panel.position.x,300),"foreign drawer slides behind diplomacy")
	await capture(main,"foreign_collapsed")
	main.territory_handle.pressed.emit();await settle()
	check(not main.territory_collapsed and is_zero_approx(main.territory_panel.position.x),"arrow reopens same territory")
	main.state.player_country="JAP";main._update_country_bar();main._show_country("JAP",false);await settle()
	check(main.territory_clip.position.x>=main.control_panel.position.x+main.control_panel.size.x-1,"own drawer remains right of country control")
	main.territory_handle.pressed.emit();await settle()
	check(is_equal_approx(main.territory_panel.position.x,-300) and main.territory_handle.text=="›","own drawer collapses left behind country control")
	main.territory_handle.pressed.emit();await settle()
	await capture(main,"own_expanded")
	main.get_window().size=Vector2i(1920,1080);main.get_window().content_scale_size=Vector2i(1440,900);await settle()
	check(main.view_container.size.is_equal_approx(main.size) and main.size.x/main.size.y>1.7,"16:9 maximized-shaped viewport fills sides")
	await capture(main,"wide_1920")
	main.get_window().size=Vector2i(2560,1080);await settle()
	check(main.view_container.size.is_equal_approx(main.size) and main.size.x/main.size.y>2.2,"ultrawide viewport fills sides")
	check(main.clock_box.position.x+main.clock_box.size.x<=main.size.x,"clock stays on right edge after resize")
	main.get_window().size=Vector2i(1100,700);main.get_window().content_scale_size=Vector2i(1100,700);await settle()
	check(main.top_left_box.size.x+main.clock_box.size.x+16<=main.size.x,"minimum-size top boxes fit")
	check(main.territory_clip.position.x+main.territory_clip.size.x<=main.view_container.size.x,"minimum-size drawer stays inside viewport")
	await capture(main,"minimum_1100")
	main._show_organization();await settle();check(not main.territory_handle.visible,"organization hides stale territorial handle")
	main._open_place_search();check(main.place_dialog.visible,"search still opens");main.place_dialog.hide();main._resume_after_dialog()
	main._enter_menu();main._start_selection();await settle()
	check(main.selection_box.visible and not main.stats_row.visible and not main.foundation.toolbar.visible,"selection screen controls remain usable")
	await capture(main,"selection")
	save_report()
	if failures==0 and OS.get_environment("BUNNY_RUN_SMOKE")=="1":
		main.get_window().size=Vector2i(1440,900);main.get_window().content_scale_size=Vector2i(1440,900)
		main._enter_menu();await main._run_smoke_test();return
	main.queue_free();await process_frame
	quit(0 if failures==0 else 1)
