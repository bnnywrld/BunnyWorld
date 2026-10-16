extends SceneTree
var failures:=0
var checks: Array[String]=[]
func _initialize() -> void:run.call_deferred()
func check(ok: bool,label: String) -> void:
 checks.append(("PASS "if ok else"FAIL ")+label);print(checks[-1]);if not ok:failures+=1
func settle() -> void:
 for i: int in 3:await process_frame
func shot(name: String) -> void:
 await RenderingServer.frame_post_draw;root.get_texture().get_image().save_png("res://validation_0217/"+name+".png")
func run() -> void:
 root.size=Vector2i(1440,900)
 var main=load("res://main.tscn").instantiate();root.add_child(main)
 while not main.boot_complete:await process_frame
 check(ProjectSettings.get_setting("application/config/version")=="0.2.0.17","version 0.2.0.17")
 check(main.state.regions.size()==1305 and main.state.countries.size()==227,"current States and controllers")
 main._start_selection();main._show_country("JAP",false);main._begin_campaign();main._map_changed(6);await settle()
 check(main.display_coverage.index["format"]=="RH" and main.display_coverage.coast_index["format"]=="RH","precise current coverage fields")
 for t: Array in [[1813,4686,3.25,99.5,"sumatra_close"],[1569,5469,38.05,127.15,"korea_close"],[253,3096,35.05,33.3,"cyprus_close"],[1811,4656,.85,104.1,"riau_close"]]:
  if main.focus_tween!=null:main.focus_tween.kill()
  main.distance=1.035;main._update_camera_pose();main.planet.rotation=Vector3(deg_to_rad(t[2]),-deg_to_rad(t[3]),0);main.inspect_region=int(t[0]);main.inspect_province=int(t[1]);main._show_country(main.state.regions[str(t[0])]["owner"],false);await settle()
  check(bool(main.planet_material.get_shader_parameter("state_coverage_enabled"))and bool(main.planet_material.get_shader_parameter("province_coverage_enabled")),"State and province coverage "+t[4])
  var tex: ImageTexture=main.planet_material.get_shader_parameter("state_coverage")
  check(tex.get_image().get_format()==Image.FORMAT_RH,"half-float coverage texture "+t[4])
  await shot(t[4])
 main._show_sea(72);await settle();check(bool(main.planet_material.get_shader_parameter("sea_coverage_enabled")),"sea coverage active");await shot("riau_sea")
 main.inspect_region=1813;main.inspect_province=0;main._show_country("IND",false);await settle()
 for tag: String in ["MNC","NAU","PAU","TIM"]:
  main._show_country(tag,false);await settle();check(main.state.selected_country==tag,"country overview "+tag)
 main.inspect_region=1813;main.inspect_province=0;main._show_country("IND",false);await settle()
 var left: int=main.diplomatic_details.get_child_count();var left_visible: bool=main.control_panel.visible
 main.territory_heading.get_node("SelectionBreadcrumb").get_child(0).pressed.emit();await settle()
 check(main.territory_details.has_node("CountryStatesList"),"country breadcrumb opens State list")
 var rows: VBoxContainer=main.territory_details.get_node("CountryStatesList").get_child(0)
 check(rows.get_child_count()==main.state.countries["IND"]["regions"].size(),"all currently owned States listed")
 var before: Vector3=main.planet.rotation;rows.get_node("State_1813").pressed.emit()
 await create_timer(.7).timeout;await settle()
 check(main.state.selected_region==1813 and main.territory_details.has_node("StateCapital"),"State button opens overview")
 check(main.planet.rotation.distance_to(before)>.01,"State button moves camera")
 check(main.control_panel.visible==left_visible and main.diplomatic_details.get_child_count()==left,"camera navigation preserves left panel")
 check(main.territory_scroll==null and not main.territory_details.has_node("CountryStatesList"),"State overview has no scroll")
 await shot("state_navigation")
 main._open_country_state(223);await create_timer(.7).timeout;await settle();check(main.state.selected_country=="CHI" and main.state.regions["223"]["provinces"].size()==1,"one Paracel State and province");await shot("paracels")
 main._open_country_state(1489);await create_timer(.7).timeout;await settle();main.tiny_state_markers.update_view()
 check(main.tiny_state_markers.entries.size()>20,"tiny strategic territory markers prepared")
 var found: bool=false
 for entry: Dictionary in main.tiny_state_markers.projected:
  if entry["state"]==1489:
   var pos: Vector2=entry["position"]+Vector2(6,0);found=main._region_at(pos)==1489
 check(found,"Gibraltar enlarged marker is selectable")
 var uploads: int=main.display_coverage.upload_count;var builds: int=main.country_label_layer.geometry_builds
 for distance: float in [1.06,1.12,1.25,1.5]:main.distance=distance;main._update_camera_pose();await settle()
 check(main.display_coverage.upload_count==uploads,"camera travel does not decode/upload geography")
 check(main.country_label_layer.geometry_builds==builds,"country names stay enabled without geometry rebuilds")
 check(main.country_labels_enabled,"country names enabled")
 var zoom: float=main.distance;var wheel:=InputEventMouseButton.new();wheel.position=main.territory_clip.get_global_rect().get_center();wheel.global_position=wheel.position;wheel.button_index=MOUSE_BUTTON_WHEEL_UP;wheel.pressed=true;root.push_input(wheel,true);await settle();check(is_equal_approx(main.distance,zoom),"UI wheel does not zoom map")
 var view={"rotation":[0.,0.],"distance":1.2,"map_mode":6,"organization":"EU","show_regions":true,"inspection_active":false,"relations_reverse":false}
 check(main.state.save_game("user://tests/patch_0217.json",view),"new campaign save");check(not main.state.load_game("user://tests/patch_0217.json").is_empty(),"new campaign load")
 var f:=FileAccess.open("res://validation_0217/runtime_results.json",FileAccess.WRITE);f.store_string(JSON.stringify({"failures":failures,"checks":checks,"display":DisplayServer.get_name()},"\t"));print("PATCH_0217_COMPLETE failures=",failures);main.queue_free();await process_frame;quit(1 if failures else 0)
