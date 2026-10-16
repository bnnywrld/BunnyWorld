extends SceneTree
var main
func _initialize() -> void:run.call_deferred()
func stats(values: Array) -> Dictionary:
 values.sort();return {"median_us":values[values.size()/2],"p95_us":values[int(values.size()*.95)],"maximum_us":values[-1]}
func run() -> void:
 main=load("res://main.tscn").instantiate();root.add_child(main)
 while not main.boot_complete:await process_frame
 main._start_selection();main._show_country("GER",false);main._begin_campaign();main._close_panels();main._focus_country("GER",false)
 if main.focus_tween!=null:main.focus_tween.kill()
 main.distance=2.0;main._update_camera_pose();main.set_process(false)
 var result: Dictionary={"platform":OS.get_name(),"rendering":DisplayServer.get_name(),"measurement":"label update CPU time; camera-path replay, no GPU timing claim"}
 var base_rotation: Vector3=main.planet.rotation
 var legacy=load("res://tests/fixtures/labels_0211.gd").new();main.view_container.add_child(legacy);legacy.size=main.view_container.size;legacy.configure(main)
 for kind: String in ["legacy_0211","current","current_forced_visibility"]:
  var layer=legacy if kind=="legacy_0211" else main.country_label_layer
  main.planet.rotation=base_rotation
  var times: Array=[]
  for i: int in 220:
   main.planet.rotation.y+=.004;main.country_labels_enabled=true
   var start:=Time.get_ticks_usec();if kind=="current_forced_visibility":layer.update_view(true)
   else:layer.update_view()
   times.append(Time.get_ticks_usec()-start)
   if i%20==0:await process_frame
  result[kind]=stats(times)
  print("LABEL_CPU ",kind," ",result[kind])
 legacy.queue_free();main.queue_free();await process_frame
 var out:=OS.get_environment("BUNNY_PERFORMANCE_RESULT")
 if not out.is_empty():var f:=FileAccess.open(out,FileAccess.WRITE);f.store_string(JSON.stringify(result,"\t"))
 quit()
