extends SceneTree
const State=preload("res://scripts/world_state.gd")
const Demo=preload("res://scripts/demography.gd")
var checks:=0
var failures:=0
func _initialize() -> void: run.call_deferred()
func check(ok: bool,label: String) -> void:
 checks+=1
 if not ok:failures+=1;printerr("FAIL ",label)
func counts_equal(a: Dictionary,b: Dictionary) -> bool:
 if a.size()!=b.size():return false
 for key: String in a:
  if not b.has(key)or int(a[key])!=int(b[key]):return false
 return true
func sum_counts(d: Dictionary) -> int:
 var total:=0
 for v: Variant in d.values():total+=int(v)
 return total
func run() -> void:
 DirAccess.make_dir_recursive_absolute("res://validation_0228")
 var db: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json"))
 var state:=State.new();state.initialize(db);var demo:=Demo.new()
 for k: String in state.regions:
  var e:=demo.state_metrics(state,int(k));var metrics: Dictionary=e["metrics"]
  check(metrics.size()==3 and not metrics.has("activity"),"three metrics "+k)
  for key: String in metrics:check(sum_counts(metrics[key]["counts"])==int(metrics[key]["denominator"]),"exact counts "+k+key)
  check(int(metrics["age"]["denominator"])==int(state.regions[k]["population"]),"resident denominator "+k)
  var f: Dictionary=e["workforce"]
  check(int(f["employed"])+int(f["unemployed"])==int(f["labour_force"]),"labour force identity "+k)
  check(int(f["labour_force"])+int(f["outside_labour_force"])==int(f["working_age"]),"working age identity "+k)
  check(is_equal_approx(float(f["unemployment_rate"]),float(f["unemployed"])/int(f["labour_force"]) if int(f["labour_force"])>0 else 0.),"unemployment denominator "+k)
 for tag: String in state.countries:
  var e:=demo.country_metrics(state,tag)
  check(int(e["population"])==int(state.countries[tag]["population"]),"national population "+tag)
  for key: String in e["metrics"]:check(sum_counts(e["metrics"][key]["counts"])==int(e["metrics"][key]["denominator"]),"national counts "+tag+key)
 var before:=demo.state_metrics(state,1837);state.transfer_region(1837,"USA");var transferred:=demo.state_metrics(state,1837)
 check(before["metrics"]["religion"]["counts"]==transferred["metrics"]["religion"]["counts"],"transfer retains religion")
 check(before["metrics"]["education"]["counts"]==transferred["metrics"]["education"]["counts"],"transfer retains education")
 state.countries["USA"]["starting_stats"]["retirement_age"]=60
 var retirement:=demo.state_metrics(state,1837)
 check(int(retirement["metrics"]["age"]["counts"]["Retired"])>int(before["metrics"]["age"]["counts"]["Retired"]),"retirement law changes age grouping")
 check(retirement["metrics"]["education"]["counts"]==before["metrics"]["education"]["counts"],"education denominator unaffected by retirement law")
 state.regions["1837"]["workforce"]["participation_rate"]=.65;state.regions["1837"]["workforce"]["unemployment_rate"]=.25
 var view: Dictionary={"rotation":[.3,-1.1],"distance":1.06,"map_mode":6,"organization":"ASEAN","show_regions":true,"inspection_active":true,"relations_reverse":false}
 var path: String="user://tests/demographics_0228_save.json"
 check(state.save_game(path,view),"save workforce rates");state.reset();check(not state.load_game(path).is_empty(),"load same-version save")
 check(is_equal_approx(state.regions["1837"]["workforce"]["unemployment_rate"],.25) and is_equal_approx(state.regions["1837"]["workforce"]["participation_rate"],.65),"workforce save load")
 check(state.regions["1837"]["owner"]=="USA","ownership save load")
 var envelope: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(path));var payload: Dictionary=JSON.parse_string(envelope["payload"]);payload["regions"]["1837"]["workforce"]["unemployment_rate"]=1.1
 var text: String=JSON.stringify(payload);var f:=FileAccess.open("user://tests/demographics_0228_invalid.json",FileAccess.WRITE);f.store_string(JSON.stringify({"format":"BunnyWorldSave","checksum":text.sha256_text(),"payload":text}));f.close()
 check(state.load_game("user://tests/demographics_0228_invalid.json").is_empty(),"invalid rate rejected")
 check(is_equal_approx(state.regions["1837"]["workforce"]["unemployment_rate"],.25),"invalid save transactional")
 var baseline: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://tools/cartography/baseline_0227/runtime_demographics.json"))
 state.reset()
 for tag: String in state.countries:
  var now:=demo.country_metrics(state,tag)
  for key: String in ["age","religion","education"]:
   check(counts_equal(now["metrics"][key]["counts"],baseline["countries"][tag]["metrics"][key]["counts"]),"exact merged national counts "+tag+key)
  for key: String in ["working_age","labour_force","employed","unemployed","outside_labour_force"]:
   check(int(now["workforce"][key])==int(baseline["countries"][tag]["workforce"][key]),"exact workforce total "+tag+key)
 check(not state.regions.has("622")and not state.regions.has("623")and not state.regions.has("1758"),"old merged states absent")
 check(state.countries["LEB"]["regions"].size()==1 and int(state.countries["LEB"]["regions"][0])==624 and state.regions["461"]["owner"]=="HEZ","Lebanon and Hezbollah scope")
 print("MODEL_CHECKS_DONE ",checks," failures ",failures)
 if OS.get_cmdline_user_args().has("model-only"):quit(1 if failures else 0);return
 root.size=Vector2i(1280,800)
 var main=load("res://main.tscn").instantiate();root.add_child(main)
 while not main.boot_complete:await process_frame
 check(main.build_version=="0.2.0.28","version .28")
 check(main.spatial_map_layers.metadata.get("geography_version")=="0.2.0.28","batch version matches province release")
 main._start_selection();main._show_country("SYR",false);main._begin_campaign()
 for sid: int in [624,1750,1837,913,177]:
  main._open_country_state(sid)
  var chart: Control=main.territory_details.find_child("StateDemographics",true,false)
  check(chart!=null and chart.selectors.get_child_count()==3,"three state selectors")
  check(chart.selectors.find_child("activity",true,false)==null,"no activity selector")
  check(main.territory_details.find_child("StateWorkforce",true,false)!=null,"separate workforce figures")
  for metric: String in ["age","religion","education"]:chart.selectors.get_node(metric).pressed.emit();check(chart.selected==metric,"selector works "+metric)
 main._show_country("SYR",false)
 check(main.control_details.find_child("NationalWorkforce",true,false)!=null,"national workforce figures")
 main.foundation.open_demographics("SYR",1837)
 var grid: Control=main.foundation.demo_content.find_child("DemographicCharts",true,false)
 check(grid!=null and grid.get_child_count()==4,"three modal charts and workforce box")
 check(grid.find_child("activity",true,false)==null and grid.find_child("WorkforceFigures",true,false)!=null,"modal activity replaced")
 main.foundation.demo_dialog.hide()
 var membership: PackedByteArray=main.map_rendering.membership_bytes
 for k: String in main.state.provinces:
  var province: Dictionary=main.state.provinces[k];var pid:=int(k);var sid:=int(province["region"])
  check(int(membership[pid*4])+int(membership[pid*4+1])*256==sid,"live province membership "+k)
  var uv: Array=province["map_center"];var tx:=mini(int(float(uv[0])*2),1);var ty:=mini(int(float(uv[1])*2),1)
  var image: Image=main.region_images[ty*2+tx]
  var col:=image.get_pixel(clampi(int((float(uv[0])*2-tx)*image.get_width()),0,image.get_width()-1),clampi(int((float(uv[1])*2-ty)*image.get_height()),0,image.get_height()-1))
  check(int(round(col.r*255))+int(round(col.g*255))*256==pid,"runtime picking image anchor "+k)
 for sid: int in [624,1750,1831,1843,1857]:
  main._show_country_states(main.state.regions[str(sid)]["owner"])
  var button: Button=main.territory_details.find_child("State_"+str(sid),true,false)
  check(button!=null,"browser button "+str(sid))
  if button!=null:
   button.mouse_entered.emit();check(main.state_preview==sid and int(main.planet_material.get_shader_parameter("selected_region"))==sid,"highlight reaches shader "+str(sid));button.mouse_exited.emit()
 if main.focus_tween!=null:main.focus_tween.kill()
 main._focus_country("CHI",false)
 var old_owner: String=main.state.regions["1857"]["owner"]
 var uploads:=int(main.map_rendering.membership_uploads);var owner_uploads:=int(main.map_rendering.ownership_uploads)
 check(main.state.transfer_region(1857,"CHI"),"offscreen transfer")
 await process_frame
 await process_frame
 for pid: int in main.state.regions["1857"]["provinces"]:
  check(main.state.province_owner(pid)=="CHI","offscreen province owner")
  var bytes: PackedByteArray=main.map_rendering.membership_bytes
  check(int(bytes[pid*4+2])+int(bytes[pid*4+3])*256==int(main.state.countries["CHI"]["index"]),"offscreen owner upload buffer")
 check(main.map_rendering.membership_uploads==uploads and main.map_rendering.ownership_uploads>owner_uploads,"transfer reuses geometry")
 check(main.state.transfer_region(1857,old_owner),"restore owner")
 await process_frame
 for mode: int in [0,1,2,4,5]:main._map_changed(mode);await process_frame

 var result: Dictionary={"passed":failures==0,"checks":checks,"failures":failures,"mode":"Godot 4.5.1 headless; native Windows visuals not tested"}
 var output:=FileAccess.open("res://validation_0228/runtime_results.json",FileAccess.WRITE);output.store_string(JSON.stringify(result,"  "));output.close()
 print("DEMOGRAPHICS_0228_RUNTIME_RESULT ",checks," checks; ",failures," failures")
 main.queue_free();await process_frame;quit(1 if failures else 0)
