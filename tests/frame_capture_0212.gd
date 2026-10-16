extends RefCounted
var main
var tree: SceneTree
var folder: String
func settle() -> void:
 for i: int in 4:await tree.process_frame
func view(tag: String, zoom: float, mode: int, own: bool=true) -> void:
 main._close_panels();main.inspect_region=0;main.inspect_province=0;main.national_profile_expanded=false
 if own:main.state.player_country=tag;main._update_country_bar()
 main._map_changed(mode);main._focus_country(tag,false)
 if main.focus_tween!=null:main.focus_tween.kill()
 main.rotation_velocity=Vector2.ZERO;main.distance=zoom;main._update_camera_pose();main._update_detail_patch();main.country_label_layer.update_view(true);await settle()
func shot(name: String) -> void:
 await settle();await RenderingServer.frame_post_draw
 tree.root.get_texture().get_image().save_png(folder.path_join(name+".png"));print("FINAL_CAPTURE ",name)
func metrics(values: Array) -> Dictionary:
 values.sort();var total:=0.0
 for v: float in values:total+=v
 return {"median_ms":values[values.size()/2],"p95_ms":values[int(values.size()*.95)],"maximum_ms":values[-1],"mean_ms":total/values.size()}
func run(host, directory: String) -> bool:
 main=host;tree=host.get_tree();folder=directory
 await view("USA",2.4,0);await shot("north_america_names")
 var on: Image=tree.root.get_texture().get_image()
 main.country_labels_enabled=false;main.country_label_layer.update_view(true);await settle();await RenderingServer.frame_post_draw
 var off: Image=tree.root.get_texture().get_image();var changed:=0
 for y: int in range(120,800,3):
  for x: int in range(150,1250,3):
   var a: Color=on.get_pixel(x,y);var b: Color=off.get_pixel(x,y)
   if absf(a.r-b.r)+absf(a.g-b.g)+absf(a.b-b.b)>.2:changed+=1
 main.country_labels_enabled=true;main.country_label_layer.update_view(true)
 var file:=FileAccess.open(folder.path_join("render_results.json"),FileAccess.WRITE);file.store_string(JSON.stringify({"name_pixels_changed_sampled":changed,"labels_visible":changed>150}))
 await view("GER",2.0,0);await shot("europe_names")
 await view("JAP",1.5,0);main._show_country("JAP",false);await shot("japan_command_bar")
 await view("JAP",1.035,6)
 main.planet.rotation=Vector3(deg_to_rad(34.75),-deg_to_rad(138.4),0);main._update_camera_pose();main._update_detail_patch()
 main.inspect_region=1564;main.inspect_province=int(main.state.regions["1564"]["provinces"][8]);main._show_country("JAP",false)
 await tree.create_timer(.3).timeout;await shot("tokai_province_9")
 main.get_window().size=Vector2i(1100,700);main.get_window().content_scale_size=Vector2i(1100,700);await settle();await shot("minimum_1100")
 main.get_window().size=Vector2i(1440,900);main.get_window().content_scale_size=Vector2i(1440,900);await settle()
 if OS.get_environment("BUNNY_SKIP_FRAME_BENCH")=="1":return changed>150
 await view("GER",2.0,0);main.state.paused=true;Engine.max_fps=0
 var base_rotation: Vector3=main.planet.rotation
 var result: Dictionary={"platform":OS.get_name(),"renderer":RenderingServer.get_video_adapter_name(),"resolution":[tree.root.size.x,tree.root.size.y],"frames_per_pass":15,"measurement":"wall frame intervals during identical camera paths; Linux software rendering, not a Windows GPU benchmark"}
 for pass_index: int in 4:
  var enabled: bool=pass_index%2==1
  main.country_labels_enabled=enabled;main.planet.rotation=base_rotation;main.country_label_layer.update_view(true)
  for i: int in 4:main.planet.rotation.y+=.002;await tree.process_frame
  var values: Array=[]
  for i: int in 15:
   main.planet.rotation.y+=.002
   var start:=Time.get_ticks_usec();await tree.process_frame
   values.append(float(Time.get_ticks_usec()-start)/1000.0)
  var key:=str(pass_index)+("_names_on" if enabled else "_names_off")
  result[key]=metrics(values);print("LABEL_FRAME ",key," ",result[key])
 file=FileAccess.open(folder.path_join("frame_results.json"),FileAccess.WRITE);file.store_string(JSON.stringify(result,"\t"))
 return changed>150
