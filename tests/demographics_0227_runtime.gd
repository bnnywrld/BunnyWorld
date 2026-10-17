extends SceneTree
const State=preload("res://scripts/world_state.gd")
const Demo=preload("res://scripts/demography.gd")
var checks:=0
var failures:=0
func _initialize() -> void: run.call_deferred()
func check(ok: bool,label: String) -> void:
 checks+=1
 if not ok:failures+=1;printerr("FAIL ",label)
func sum_counts(d: Dictionary) -> int:
 var total:=0
 for v: Variant in d.values():total+=int(v)
 return total
func run() -> void:
 DirAccess.make_dir_recursive_absolute("res://validation_0227")
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
 var path: String="user://tests/demographics_0227_save.json"
 check(state.save_game(path,view),"save workforce rates");state.reset();check(not state.load_game(path).is_empty(),"load same-version save")
 check(is_equal_approx(state.regions["1837"]["workforce"]["unemployment_rate"],.25) and is_equal_approx(state.regions["1837"]["workforce"]["participation_rate"],.65),"workforce save load")
 check(state.regions["1837"]["owner"]=="USA","ownership save load")
 var envelope: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(path));var payload: Dictionary=JSON.parse_string(envelope["payload"]);payload["regions"]["1837"]["workforce"]["unemployment_rate"]=1.1
 var text: String=JSON.stringify(payload);var f:=FileAccess.open("user://tests/demographics_0227_invalid.json",FileAccess.WRITE);f.store_string(JSON.stringify({"format":"BunnyWorldSave","checksum":text.sha256_text(),"payload":text}));f.close()
 check(state.load_game("user://tests/demographics_0227_invalid.json").is_empty(),"invalid rate rejected")
 check(is_equal_approx(state.regions["1837"]["workforce"]["unemployment_rate"],.25),"invalid save transactional")
 print("MODEL_CHECKS_DONE ",checks," failures ",failures)
 root.size=Vector2i(1280,800)
 var main=load("res://main.tscn").instantiate();root.add_child(main)
 while not main.boot_complete:await process_frame
 check(main.build_version=="0.2.0.27","version .27")
 check(main.spatial_map_layers.metadata.get("geography_version")=="0.2.0.27","batch version matches data-only release")
 main._start_selection();main._show_country("SYR",false);main._begin_campaign()
 for sid: int in [1837,913,177]:
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
 var result: Dictionary={"passed":failures==0,"checks":checks,"failures":failures,"mode":"Godot 4.5.1 headless; native Windows visuals not tested"}
 var output:=FileAccess.open("res://validation_0227/runtime_results.json",FileAccess.WRITE);output.store_string(JSON.stringify(result,"  "));output.close()
 print("DEMOGRAPHICS_0227_RUNTIME_RESULT ",checks," checks; ",failures," failures")
 main.queue_free();await process_frame;quit(1 if failures else 0)
