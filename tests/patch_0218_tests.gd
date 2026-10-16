extends SceneTree
var failures:=0
var checks: Array[String]=[]
func _initialize() -> void:run.call_deferred()
func check(ok: bool,label: String) -> void:
 checks.append(("PASS "if ok else"FAIL ")+label);print(checks[-1]);if not ok:failures+=1
func settle(frames: int=3) -> void:
 for i: int in frames:await process_frame
func shot(name: String) -> Image:
 await RenderingServer.frame_post_draw
 var im: Image=root.get_texture().get_image();im.save_png("res://validation_0218/"+name+".png");return im
func pose(main,sid: int,pid: int,lat: float,lon: float,dist: float) -> void:
 if main.focus_tween!=null:main.focus_tween.kill()
 main.rotation_velocity=Vector2.ZERO;main.distance=dist;main._update_camera_pose()
 main.planet.rotation=Vector3(deg_to_rad(lat),-deg_to_rad(lon),0)
 main.inspect_region=sid;main.inspect_province=pid;main._show_country(main.state.regions[str(sid)]["owner"],false)
 main.control_panel.hide();main.territory_clip.hide()
func difference(a: Image,b: Image) -> int:
 var smalla: Image=a.duplicate();var smallb: Image=b.duplicate();smalla.resize(360,225);smallb.resize(360,225)
 var ba:=smalla.get_data();var bb:=smallb.get_data();var changed:=0
 for i: int in ba.size():if abs(int(ba[i])-int(bb[i]))>4:changed+=1
 return changed
func run() -> void:
 DirAccess.make_dir_recursive_absolute("res://validation_0218")
 root.size=Vector2i(1440,900)
 var main=load("res://main.tscn").instantiate();root.add_child(main)
 while not main.boot_complete:await process_frame
 main._start_selection();main._show_country("JAP",false);main._begin_campaign();main._map_changed(6)
 check(main.map_rendering.contract["ownership_baked"]==false,"no ownership-dependent prepared masks")
 check(main.map_rendering.contract["land_selection_masks"]==false,"no pre-State/province highlight masks")
 check(main.display_coverage.pack.get_path().ends_with("sea_coverage.bwd"),"old 204MB land selection pack retired")
 check(main.map_rendering.region_images.size()==4,"verified raw categorical textures shared with picking")
 for row: Array in [[1813,4655,2.3,99.2,1.07,"sumatra"],[253,3093,35.08,33.24,1.022,"cyprus"],[1569,5469,38.05,127.15,1.035,"korea"]]:
  pose(main,row[0],row[1],row[2],row[3],row[4]);await settle(5)
  check(main.state.selected_region==row[0],"actual State selected "+row[5])
  check(main.display_coverage.last_state==row[0],"selection uses live mapping "+row[5])
  await shot(row[5])
 # State ownership transfer: new colour and national edges appear without
 # geometry building, disk mask loading or any explicit palette refresh.
 main._map_changed(0);pose(main,1813,0,2.3,99.2,1.11);await settle(5)
 main.inspection_active=false;main._update_selection_shader();await settle()
 var original:=await shot("transfer_before")
 var uploads: int=main.display_coverage.upload_count;var membership: int=main.map_rendering.membership_uploads
 var meshes: int=main.detail_mesh_builds
 check(main.state.transfer_region(1813,"JAP"),"State ownership transfer succeeds")
 await settle(5);var taken:=await shot("transfer_after")
 check(difference(original,taken)>3000,"political ownership visibly changes automatically")
 check(main.display_coverage.upload_count==uploads,"ownership transfer loads no geography masks")
 check(main.map_rendering.membership_uploads==membership,"ownership transfer leaves membership geometry unchanged")
 check(main.detail_mesh_builds==meshes,"ownership transfer builds no terrain meshes")
 check(main.state.transfer_region(1813,"IND"),"State ownership can transfer back")
 await settle(5);var returned:=await shot("transfer_returned")
 check(difference(original,returned)<1000,"political colour returns after ownership restored")
 # Physical edge shading must react too, including a new internal border.
 main._map_changed(6);pose(main,1813,0,2.3,99.2,1.07);main.inspection_active=false;main._update_selection_shader();await settle(5)
 var physical_before:=await shot("physical_before")
 main.state.transfer_region(1813,"JAP");await settle(5);var physical_after:=await shot("physical_after")
 check(difference(physical_before,physical_after)>300,"physical national edge shading responds to new ownership")
 main.state.transfer_region(1813,"IND");await settle(5)
 # Merge simulation in the small current membership lookup: state 486 into
 # 1813. Highlight includes its provinces with no generated State texture.
 pose(main,1813,0,1.5,100.0,1.14);await settle(5)
 var merged:=[]
 for p: Dictionary in main.state.provinces.values():
  if int(p["region"])==486:merged.append(int(p["id"]));p["region"]=1813
 main.map_rendering.update_membership(main.state.provinces);await settle(5);await shot("membership_merge")
 check(merged.size()>0 and main.map_rendering.membership_uploads==membership+1,"State merge only updates small membership lookup")
 for id: int in merged:main.state.provinces[str(id)]["region"]=486
 main.map_rendering.update_membership(main.state.provinces);await settle(5)
 var before_uploads: int=main.display_coverage.upload_count;var before_names: int=main.country_label_layer.geometry_builds
 for d: float in [1.08,1.12,1.2,1.4,1.65]:main.distance=d;await settle(2)
 check(main.display_coverage.upload_count==before_uploads,"camera motion does not decode/upload geography")
 check(main.country_label_layer.geometry_builds==before_names,"camera motion does not rebuild country names")
 check(main.country_labels_enabled,"country names remain enabled")
 main._show_sea(72);await settle(4);check(main.display_coverage.last_sea==72,"sea selection retained")
 var f:=FileAccess.open("res://validation_0218/runtime_results.json",FileAccess.WRITE);f.store_string(JSON.stringify({"failures":failures,"checks":checks,"renderer":RenderingServer.get_video_adapter_name(),"native_windows_tested":false},"\t"))
 print("PATCH_0218_COMPLETE failures=",failures);main.queue_free();await process_frame;quit(1 if failures else 0)
