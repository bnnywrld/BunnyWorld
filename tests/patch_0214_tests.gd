extends SceneTree
var failures:=0
var checks: Array[String]=[]
func _initialize() -> void:run.call_deferred()
func check(ok: bool,caption: String) -> void:
 checks.append(("PASS " if ok else "FAIL ")+caption);print(checks[-1]);if not ok:failures+=1
func settle() -> void:
 for i: int in 3:await process_frame
func shot(name: String) -> void:
 if DisplayServer.get_name()=="headless":return
 await RenderingServer.frame_post_draw;root.get_texture().get_image().save_png("res://validation_0214/"+name+".png")
func run() -> void:
 var main=load("res://main.tscn").instantiate();root.add_child(main)
 while not main.boot_complete:await process_frame
 check(ProjectSettings.get_setting("application/config/version")=="0.2.0.14","application version")
 check(main.state.regions.size()==1355,"1355 States")
 main._start_selection();main._show_country("JAP",false);main._begin_campaign();await settle()
 check(main.control_panel==main.right_panel,"one shared left country panel")
 check(main.territory_scroll==null,"State panel has no scroll")
 main._map_changed(6);main.distance=1.035;main._update_camera_pose();main._update_detail_patch()
 if main.focus_tween!=null:main.focus_tween.kill()
 main.planet.rotation=Vector3(deg_to_rad(35.687),-deg_to_rad(139.749),0)
 for sid: int in [1494,1541,1563,363,1826,1813,687]:
  main.inspect_region=sid;main.inspect_province=int(main.state.regions[str(sid)]["provinces"][0]);main._show_country(main.state.regions[str(sid)]["owner"],false);await settle()
  check(main.territory_details.has_node("StateCapital") and main.territory_details.has_node("BuildingSlots"),"capital, count and slots "+str(sid))
  var last: Control=main.territory_details.get_child(-1)
  check(last.get_global_rect().end.y<=main.size.y-5,"State contents fit "+str(sid))
 main.inspect_region=1563;main.inspect_province=5144;main._show_country("JAP",false);await settle();await shot("tokyo_state")
 check(main.control_panel.global_position.x<main.size.x*.5 and main.territory_clip.global_position.x>main.size.x*.5,"country left, State right")
 check(bool(main.planet_material.get_shader_parameter("state_coverage_enabled")),"prepared merged State coverage active")
 main._show_sea(90);await settle();check(main.state.selected_sea==90 and main.territory_heading.has_node("SeaTitle"),"sea inspector on right")
 check(bool(main.planet_material.get_shader_parameter("sea_coverage_enabled")),"smooth prepared sea coverage active")
 check(main.territory_heading.get_node("SeaTitle").size.y>=30,"sea heading readable");await shot("tokyo_sea")
 var uploads: int=main.display_coverage.upload_count;var labels: int=main.country_label_layer.geometry_builds
 for zoom: float in [1.05,1.2,1.5,2.0]:
  main.distance=zoom;main._update_camera_pose();await settle()
 check(main.display_coverage.upload_count==uploads,"camera movement never uploads or decodes selection geography")
 check(main.country_label_layer.geometry_builds==labels,"camera movement never rebuilds country labels")
 main.country_labels_enabled=true;main._close_panels();main.distance=2.0;main._update_camera_pose();main.planet.rotation=Vector3(deg_to_rad(35),-deg_to_rad(115),0);await settle();main.country_label_layer.update_view(true);await shot("country_names")
 check(not main.country_label_layer.visible_labels.is_empty(),"country names enabled and visible")
 check(not main.territory_clip.visible,"clearing selection closes State panel")
 root.size=Vector2i(1100,700);await settle();main.distance=1.1;main.inspect_region=1494;main.inspect_province=int(main.state.regions["1494"]["provinces"][0]);main._show_country("FRA",false);await settle();main._position_panels();await settle()
 var bottom: Control=main.territory_details.get_child(-1)
 check(bottom.get_global_rect().end.y<=main.size.y-5,"dense State fits 1100x700 without scroll");await shot("compact_state")
 var zoom_before: float=main.distance;var event:=InputEventMouseButton.new();event.position=main.territory_clip.get_global_rect().get_center();event.global_position=event.position;event.button_index=MOUSE_BUTTON_WHEEL_UP;event.pressed=true;root.push_input(event,true);await settle();check(is_equal_approx(main.distance,zoom_before),"UI wheel does not zoom map")
 var view={"rotation":[0.0,0.0],"distance":1.2,"map_mode":0,"organization":"EU","show_regions":true,"inspection_active":false,"relations_reverse":false}
 check(main.state.save_game("user://tests/patch_0214.json",view),"fresh-version save")
 check(not main.state.load_game("user://tests/patch_0214.json").is_empty(),"fresh-version load")
 var f:=FileAccess.open("res://validation_0214/runtime_results.json",FileAccess.WRITE);f.store_string(JSON.stringify({"checks":checks,"failures":failures,"display":DisplayServer.get_name()},"\t"));print("PATCH_0214_COMPLETE failures=",failures);main.queue_free();await process_frame;quit(1 if failures else 0)
