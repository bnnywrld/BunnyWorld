extends SceneTree
var failures := 0
var checks := 0
func _initialize() -> void: run.call_deferred()
func check(ok: bool, label: String) -> void:
 checks += 1
 if not ok: failures += 1
 print(("PASS " if ok else "FAIL ") + label)
func run() -> void:
 root.size = Vector2i(1280,800)
 var main = load("res://main.tscn").instantiate()
 root.add_child(main)
 while not main.boot_complete: await process_frame
 check(main.build_version == "0.2.0.26", "new application version")
 check(main.state.regions.size() == 1264, "all states initialize")
 main._start_selection()
 main._show_country("CHI",false)
 main._begin_campaign()
 main._map_changed(0)
 var report: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/geography_0226_report.json"))
 var image: Image = main.map_rendering.province_texture.get_image()
 for s: Dictionary in report["new_states"]:
  for pid: int in s["provinces"]:
   var col: Color = image.get_pixel(pid%256,int(pid/256))
   check(int(round(col.r*255))+int(round(col.g*255))*256 == int(s["id"]), "live membership %d -> %d"%[pid,int(s["id"])])
 # One representative new state from each country; browser hover and inline info.
 for sid: int in [1831,1841,1843,1851,1849,1857]:
  var s: Dictionary = main.state.regions[str(sid)]
  main._show_country_states(s["owner"])
  var button: Button = main.territory_details.find_child("State_"+str(sid),true,false)
  check(button != null,"new state browser button "+str(sid))
  var selected: int = main.state.selected_region
  if button != null: button.mouse_entered.emit()
  check(main.state_preview == sid and int(main.planet_material.get_shader_parameter("selected_region"))==sid,"hover reaches shared highlight "+str(sid))
  check(main.state.selected_region==selected,"hover preserves selection "+str(sid))
  if button != null: button.mouse_exited.emit()
  main._open_country_state(sid)
  check(main.state.selected_region==sid and main.inspection_active,"new state opens "+str(sid))
  check(main.territory_details.find_child("StateDemographics",true,false)!=null,"inline demographic chart "+str(sid))
  check(s["capital_province"] in s["provinces"],"capital stays inside "+str(sid))
 # Change ownership in South America while the camera is centred on China.
 if main.focus_tween != null: main.focus_tween.kill()
 main._focus_country("CHI",false)
 var old_owner: String = main.state.regions["1857"]["owner"]
 var count: int = main.map_rendering.membership_uploads
 var owner_uploads: int = main.map_rendering.ownership_uploads
 check(main.state.transfer_region(1857,"CHI"),"offscreen state transfer succeeds")
 await process_frame
 await process_frame
 image=main.map_rendering.province_texture.get_image()
 for pid: int in main.state.regions["1857"]["provinces"]:
  check(main.state.province_owner(pid)=="CHI","offscreen province owner "+str(pid))
  var data: PackedByteArray=main.map_rendering.membership_bytes
  check(int(data[pid*4+2])+int(data[pid*4+3])*256==int(main.state.countries["CHI"]["index"]),"live owner texture upload buffer "+str(pid))
 check(main.map_rendering.ownership_uploads>owner_uploads,"ownership changes trigger texture upload")
 check(main.map_rendering.membership_uploads==count,"owner transfer reuses province geometry")
 check(main.state.transfer_region(1857,old_owner),"restore ownership after test")
 await process_frame
 check(main.state.countries["TAI"]["regions"].size()==6 and main.state.countries["AFG"]["regions"].size()==2,"Taiwan and Afghanistan retained")
 var file := FileAccess.open("res://validation_0226/runtime_results.json",FileAccess.WRITE)
 file.store_string(JSON.stringify({"checks":checks,"failures":failures,"passed":failures==0,"mode":"Godot 4.5.1 headless; checks texture upload bytes, not hardware GPU readback; no native Windows graphics test"},"  "))
 print("STATES_0226_RUNTIME_RESULT ",checks," checks; ",failures," failures")
 main.queue_free()
 await process_frame
 quit(1 if failures else 0)
