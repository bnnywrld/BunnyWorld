extends SceneTree
var failures := 0
var checks: Array[String] = []
var graphical := false
func _initialize() -> void: run.call_deferred()
func check(ok: bool, label: String) -> void:
 checks.append(("PASS " if ok else "FAIL ") + label)
 print(checks[-1])
 if not ok: failures += 1
func settle(frames: int = 2) -> void:
 for i: int in frames: await process_frame
func shot(name: String) -> void:
 if not graphical: return
 await RenderingServer.frame_post_draw
 root.get_texture().get_image().save_png("res://validation_0224/" + name + ".png")
func run() -> void:
 DirAccess.make_dir_recursive_absolute("res://validation_0224")
 graphical = DisplayServer.get_name() != "headless"
 root.size = Vector2i(1280, 800)
 var main = load("res://main.tscn").instantiate()
 root.add_child(main)
 await process_frame
 check(main.loading_overlay.get_child(0) is TextureRect, "loading screen uses supplied photograph")
 await shot("loading")
 while not main.boot_complete: await process_frame
 check(main.build_version == "0.2.0.24", "application version .24")
 check(main.menu_background.visible and main.menu_screen.visible, "main menu shows photograph")
 check(main.menu_background.texture.resource_path.ends_with("menu_background.jpg"), "menu uses requested source image")
 check(main.menu_background.stretch_mode == TextureRect.STRETCH_KEEP_ASPECT_COVERED, "background preserves proportions")
 await shot("menu")
 main._start_selection()
 check(not main.menu_background.visible, "menu background hides for country selection")
 main._show_country("JAP", false)
 main._begin_campaign()
 main._map_changed(0)
 main._show_country("JAP", false)
 await settle()
 main._position_panels()
 check(is_equal_approx(main.control_panel.size.x, 370.0), "country control panel widened to 370")
 main._show_country("FRA", false)
 main._position_panels()
 check(is_equal_approx(main.control_panel.size.x, 370.0), "diplomacy inspector uses same wider layout")
 for caption: String in main.foundation.feature_buttons:
  var button: Button = main.foundation.feature_buttons[caption]
  check(not button.disabled, "feature button enabled: " + caption)
  button.pressed.emit()
  check(main.control_panel.visible and main.active_feature == caption and main.control_details.get_child_count() == 0, "empty titled feature panel: " + caption)
  check(button.button_pressed, "active feature button: " + caption)
  check(main.control_heading.get_child(0).get_child(0).text == caption, "feature heading: " + caption)
 main._show_feature("Research")
 await settle()
 await shot("research")
 var close: Button = main.control_heading.get_child(0).get_child(1)
 close.pressed.emit()
 check(not main.control_panel.visible and main.active_feature.is_empty(), "feature close button hides panel")
 main._show_feature("Research")
 main._show_feature("Research")
 check(not main.control_panel.visible, "clicking feature twice toggles closed")
 main._open_country_state(1569)
 await settle()
 var crumb: Button = main.territory_heading.find_child("BrowseCountryStates", true, false)
 check(crumb != null and crumb.icon != null and crumb.get_theme_constant("icon_max_width") == 22, "country breadcrumb has small flag")
 var selection: Array = [main.state.selected_country, main.state.selected_region, main.state.selected_province, main.state.selected_sea]
 crumb.pressed.emit()
 check(main.focus_tween != null and main.focus_tween.is_running(), "country breadcrumb starts camera centering")
 check(main.territory_details.find_child("CountryStatesList", true, false) != null, "country breadcrumb opens state browser")
 var list_button: Button = main.territory_details.find_child("State_1574", true, false)
 check(list_button != null, "state browser lists another state")
 list_button.mouse_entered.emit()
 check(main.state_preview == 1574 and int(main.planet_material.get_shader_parameter("selected_region")) == 1574, "state hover updates smooth map highlight")
 check(selection == [main.state.selected_country, main.state.selected_region, main.state.selected_province, main.state.selected_sea], "hover preserves actual selection and country")
 var original_owner: String = main.state.regions["1574"]["owner"]
 check(original_owner == "KOR", "hover leaves ownership unchanged")
 await settle()
 await shot("state_hover")
 list_button.mouse_exited.emit()
 check(main.state_preview == 0 and int(main.planet_material.get_shader_parameter("selected_region")) == main.state.selected_region, "hover exit restores selection")
 list_button.mouse_entered.emit()
 main._toggle_territory()
 check(main.state_preview == 0, "collapsing drawer clears state preview")
 main._toggle_territory()
 list_button.mouse_entered.emit()
 main._hide_panel(main.territory_panel)
 check(main.state_preview == 0, "hiding drawer clears state preview")
 main._show_country_states("MIC")
 check(main.territory_details.find_children("State_*", "Button", true, false).size() == 1, "Micronesia browser contains one state")
 main._open_country_state(675)
 check(main.state.selected_country == "MIC" and main.state.selected_region == 675 and int(main.state.provinces["4773"]["region"]) == 675, "former Palau province is selectable in Micronesia")
 check(not main.state.countries.has("PAU") and not main.state.database["country_registry"].has("PAU"), "Palau removed from active and releasable countries")
 check(not main.state.provinces.has("3024") and not main.state.provinces.has("13050"), "unwanted tiny provinces removed")
 for row: Array in [[12399,1735],[12400,1735],[13026,1707],[13037,1707],[4773,675]]:
  var record: Color = main.map_rendering.province_texture.get_image().get_pixel(row[0] % 256, int(row[0] / 256))
  check(int(round(record.r * 255)) + int(round(record.g * 255)) * 256 == row[1], "GPU membership follows island merge " + str(row[0]))
 main._show_feature("Research")
 main._show_country("MIC", false)
 check(main.active_feature.is_empty() and not main.foundation.feature_buttons["Research"].button_pressed, "country inspection replaces placeholder cleanly")
 # The user tests native smoothness/appearance; this verifies data and UI behavior.
 var result := {"checks": checks.size(), "failures": failures, "graphical": graphical, "native_windows_tested": false, "results": checks}
 var out := FileAccess.open("res://validation_0224/runtime_results.json", FileAccess.WRITE)
 out.store_string(JSON.stringify(result, "  "))
 out.close()
 print("PATCH_0224_RESULTS ", checks.size(), " checks, ", failures, " failures")
 main.queue_free()
 await settle()
 quit(1 if failures else 0)
