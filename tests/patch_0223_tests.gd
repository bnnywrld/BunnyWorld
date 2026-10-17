extends SceneTree
const Surface = preload("res://scripts/relief_surface.gd")
var failures:=0
var checks: Array[String]=[]
func _initialize() -> void:run.call_deferred()
func check(ok: bool,label: String) -> void:
 checks.append(("PASS "if ok else"FAIL ")+label);print(checks[-1]);if not ok:failures+=1
func settle(frames: int=3) -> void:
 for i: int in frames:await process_frame
func shot(name: String) -> Image:
 await RenderingServer.frame_post_draw
 var im: Image=root.get_texture().get_image();im.save_png("res://validation_0223/runtime/"+name+".png");return im
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
 DirAccess.make_dir_recursive_absolute("res://validation_0223/runtime")
 root.size=Vector2i(1440,900)
 var main=load("res://main.tscn").instantiate();root.add_child(main)
 while not main.boot_complete:await process_frame
 main._start_selection();main._show_country("JAP",false);main._begin_campaign();main._map_changed(6)
 check(not main.state.countries.has("HLS") and not main.state.regions.has("464") and not main.state.provinces.has("4478"),"Vatican country, State and province removed")
 check(main.spatial_map_layers.prepared_chunks>0 and main.spatial_map_layers.geometry_builds==0,"spatial resources prepared once with no runtime geometry generation")
 check(main.map_rendering.province_texture.get_image().get_format()==Image.FORMAT_RGBA8,"combined live owner and membership lookup")
 check(main.map_rendering.region_textures[0].get_image().get_format()==Image.FORMAT_RG8,"lossless two-channel ID textures reduce GPU memory")
 var vatican_matches: Array=main.places.find_places("Vatican")
 check(main.places.entries.filter(func(r: Dictionary):return r["kind"]=="Country" and r["country"]=="HLS").is_empty(),"Vatican no longer appears as a country in search")
 if not vatican_matches.is_empty():
  main._go_to_place(vatican_matches[0],false);await settle(4)
  check(main._province_at(Vector2(main.world_view.size)*.5)==4934,"former Vatican city picks Rome's existing province")
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
 var owner_uploads: int=main.map_rendering.ownership_uploads
 check(main.state.transfer_region(1813,"JAP"),"State ownership transfer succeeds")
 await settle(5);var taken:=await shot("transfer_after")
 check(difference(original,taken)>3000,"political ownership visibly changes automatically")
 check(main.display_coverage.upload_count==uploads,"ownership transfer loads no geography masks")
 check(main.map_rendering.membership_uploads==membership,"ownership transfer leaves membership geometry unchanged")
 check(main.map_rendering.ownership_uploads==owner_uploads+1,"ownership event updates only the small live lookup")
 var live_record: Color=main.map_rendering.province_texture.get_image().get_pixel(4655%256,int(4655/256))
 check(int(round(live_record.b*255))+int(round(live_record.a*255))*256==int(main.state.countries["JAP"]["index"]),"GPU owner lookup agrees with transferred State")
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
 var before_owner_uploads: int=main.map_rendering.ownership_uploads
 var before_uploads: int=main.display_coverage.upload_count;var before_names: int=main.country_label_layer.geometry_builds
 for d: float in [1.08,1.12,1.2,1.4,1.65]:main.distance=d;await settle(2)
 check(main.display_coverage.upload_count==before_uploads,"camera motion does not decode/upload geography")
 check(main.map_rendering.ownership_uploads==before_owner_uploads and main.spatial_map_layers.geometry_builds==0,"camera motion builds no spatial geometry and uploads no owner lookup")
 check(main.country_label_layer.geometry_builds==before_names,"camera motion does not rebuild country names")
 check(main.country_labels_enabled,"country names remain enabled")
 main._show_sea(72);await settle(4);check(main.display_coverage.last_sea==72,"sea selection retained")
 var cpu_samples: Array=[]
 main.distance=1.07
 for step: int in 64:
  main.planet.rotation.y+=.001
  var started:=Time.get_ticks_usec()
  main._update_camera_pose();main._update_detail_patch()
  cpu_samples.append(float(Time.get_ticks_usec()-started)/1000.0)
 cpu_samples.sort()
 var cpu_file:=FileAccess.open("res://validation_0223/runtime/camera_cpu.json",FileAccess.WRITE)
 cpu_file.store_string(JSON.stringify({"measurement":"CPU camera/spatial-culling/detail-uniform updates only; not FPS","median_ms":cpu_samples[32],"p95_ms":cpu_samples[60],"maximum_ms":cpu_samples[-1],"runtime_geometry_builds":main.spatial_map_layers.geometry_builds},"\t"))
 check(main.spatial_map_layers.geometry_builds==0,"sustained camera rotation generates no geometry")
 await performance_checks(main)
 await additional_checks(main)
 var f:=FileAccess.open("res://validation_0223/runtime/runtime_results.json",FileAccess.WRITE);f.store_string(JSON.stringify({"failures":failures,"checks":checks,"renderer":RenderingServer.get_video_adapter_name(),"native_windows_tested":false},"\t"))
 print("PATCH_0223_COMPLETE failures=",failures);main.queue_free();await process_frame;quit(1 if failures else 0)

func performance_checks(main: Control) -> void:
 # Scheduler decisions have no link to the simulation object.
 var policy = load("res://scripts/map_frame_policy.gd").new()
 for i: int in 60: policy.request_frame([0], 1.0/60.0)
 var before: int=policy.requested_frames
 for i: int in 600: policy.request_frame([0], 1.0/60.0)
 var idle_draws: int=policy.requested_frames-before
 check(idle_draws>=80 and idle_draws<=101,"stationary policy requests about 10 map draws per second at 60 application frames")
 check(policy.request_frame([1],0.0),"changed view wakes immediately without waiting for idle heartbeat")
 var moving_before: int=policy.requested_frames
 for i: int in 60:policy.request_frame([i+2],1.0/60.0)
 check(policy.requested_frames-moving_before==60,"moving view renders at every application frame")
 # Exact CPU sea IDs remain available; GPU stores only the same binary test.
 var mask: Image=main.planet_material.get_shader_parameter("sea_map").get_image()
 check(mask.get_format()==Image.FORMAT_R8 and mask.get_width()==8192 and mask.get_height()==4096,"GPU sea mask uses R8 at original resolution")
 var matches:=true
 for y: int in range(0,4096,91):
  for x: int in range(0,8192,113):
   var id: Color=main.sea_image.get_pixel(x,y)
   if (mask.get_pixel(x,y).r>.5)!=(id.r+id.g>.001):matches=false
 check(matches,"GPU sea mask agrees with exact CPU sea IDs")
 # Cache does not approximate the relief ray, even at tilted close zoom.
 var accurate:=true
 for row: Array in [[46.0,7.5,1.025],[2.3,99.2,1.07],[0.0,179.5,1.1],[80.0,-40.0,1.12],[0.0,-140.0,3.5]]:
  main.distance=row[2];main.planet.rotation=Vector3(deg_to_rad(row[0]),-deg_to_rad(row[1]),0);main._update_camera_pose()
  var at:=Vector2(main.world_view.size)*.5
  main.last_pick_key=[]
  var marches: int=main.pick_ray_marches
  var uv: Vector2=main._uv_at(at)
  main._region_at(at);main._province_at(at);main._sea_at(at)
  check(main.pick_ray_marches==marches+1,"region/province/sea reuse one terrain ray at "+str(row))
  var inverse: Transform3D=main.planet.global_transform.affine_inverse()
  var ray: Vector3=main.relief_surface.ray_point(inverse*main.camera.project_ray_origin(at),(inverse.basis*main.camera.project_ray_normal(at)).normalized())
  var expected:=Surface.uv_of(ray) if ray!=Vector3.ZERO else Vector2(-1,-1)
  if uv.distance_to(expected)>.0000001:accurate=false
  var n: int=main.pick_ray_marches
  main._uv_at(at+Vector2(1,0));check(main.pick_ray_marches==n+1,"mouse movement invalidates intersection cache")
 check(accurate,"cached picking agrees with direct relief rays at mountains, poles, dateline and ocean")
 # Freeze drawing, but run the real main loop and compare its clock to the
 # same WorldState.advance sequence. Neither hemisphere gets special status.
 main.set_process(false);main.screen="playing";main.state.paused=false;main.state.speed=30
 main.state.accumulator=0;main.state.hour=0
 main.map_frame_policy.force_continuous=false
 main._process(0.0)
 main.map_frame_policy.settle=0;main.map_frame_policy.elapsed=-100.0
 for i: int in 8: main._process(.25)
 check(main.state.hour==60,"world clock advances normally while map draws are disabled")
 check(main.world_view.render_target_update_mode==SubViewport.UPDATE_DISABLED,"clock test actually keeps the map viewport disabled")
 main.state.paused=true
 # North Sumatra is behind the globe while viewing North America.
 pose(main,1677,0,47.2,-100.5,1.1)
 main._process(0.0)
 var old_owner: String=main.state.regions["1813"]["owner"]
 var uploaded: int=main.map_rendering.ownership_uploads
 var revision: int=main.map_frame_policy.revision
 var transferred: bool=main.state.transfer_region(1813,"JAP")
 check(transferred,"off-screen State ownership changes independently of visibility")
 main._process(0.0)
 var sample: Color=main.map_rendering.province_texture.get_image().get_pixel(4655%256,int(4655/256))
 check(int(round(sample.b*255))+256*int(round(sample.a*255))==int(main.state.countries["JAP"]["index"]),"hidden hemisphere receives current GPU owner lookup before rotating back")
 check(main.map_rendering.ownership_uploads==uploaded+1 and main.map_frame_policy.revision>revision,"off-screen ownership invalidates rendering without rebuilding geography")
 check(main.world_view.render_target_update_mode==SubViewport.UPDATE_ONCE,"ownership change immediately wakes map rendering")
 pose(main,1813,0,2.3,99.2,1.07);main._process(0.0)
 check(main.state.regions["1813"]["owner"]=="JAP","rotating back uses current off-screen ownership")
 main.state.transfer_region(1813,old_owner);main._process(0.0)
 var membership: int=main.map_frame_policy.revision
 main.map_rendering.update_membership(main.state.provinces)
 check(main.map_frame_policy.revision>membership,"direct membership lookup updates invalidate an idle viewport")
 # Explicit quality switches replace arrays, with no repeated upload on a
 # camera change or on Balanced -> High (same terrain texture quality).
 var settings_path:="user://interface_settings.json"
 var had_settings:=FileAccess.file_exists(settings_path)
 var settings:=FileAccess.get_file_as_bytes(settings_path) if had_settings else PackedByteArray()
 main._graphics_changed(1)
 check(main.resident_terrain.light_active and main.resident_terrain.texture.get_width()==2048,"Light texture quality applies immediately")
 var quality_uploads: int=main.resident_terrain.quality_uploads
 main.planet.rotation.y+=.001;main._process(.01)
 check(main.resident_terrain.quality_uploads==quality_uploads,"camera motion uploads no terrain arrays")
 main._graphics_changed(0)
 check(not main.resident_terrain.light_active and main.resident_terrain.texture.get_width()==4096,"Balanced restores high-resolution terrain immediately")
 quality_uploads=main.resident_terrain.quality_uploads
 main._graphics_changed(2)
 check(main.resident_terrain.quality_uploads==quality_uploads,"Balanced to High only changes MSAA without a redundant terrain upload")
 main._graphics_changed(0)
 if had_settings:
  var settings_file:=FileAccess.open(settings_path,FileAccess.WRITE);settings_file.store_buffer(settings)
 else:DirAccess.remove_absolute(settings_path)
 main.map_diagnostics.start(120)
 var diagnostic_path:=""
 for i: int in 120:diagnostic_path=main.map_diagnostics.capture(main,false)
 check(not diagnostic_path.is_empty() and FileAccess.file_exists(main.map_diagnostics.last_path),"bounded native timing capture writes a report")
 var report: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(main.map_diagnostics.last_path))
 check(report["samples"].size()==120 and report["summary"]["map_draws"]==0,"timing report records map redraws separately from application frames")
 main.state.paused=true;main.set_process(true)

func expected_clusters(urban: Node3D, camera: Camera3D) -> Array:
 var nearby: Array=[]
 for record: Dictionary in urban.clusters:
  if urban._in_view(record,camera):nearby.append({"record":record,"distance":(urban.global_transform*record["point"]).distance_squared_to(camera.global_position)})
 nearby.sort_custom(func(a:Dictionary,b:Dictionary):return a["distance"]<b["distance"])
 var result: Array=[];var budget:=0
 for entry: Dictionary in nearby:
  var record: Dictionary=entry["record"];var count: int=record["instances"].size()
  if result.size()>=96:break
  if budget+count>2048:continue
  result.append(int(record["id"]));budget+=count
 result.sort();return result

func additional_checks(main: Control) -> void:
 main.set_process(false);main.state.paused=true
 var report: Dictionary={"city_views":[],"scenery_views":[]}
 var reference=load("res://validation_0223/reference_main_0222.gd").new()
 reference.planet=main.planet;reference.camera=main.camera;reference.view_container=main.view_container
 reference.world_view=main.world_view;reference.cities=main.cities;reference.screen="playing"
 reference.city_layer=load("res://scripts/city_overlay.gd").new()
 # The index must produce the exact old decorations, including label collisions
 # and the cluster budget. These views include dense cities, poles/dateline.
 for row: Array in [[1813,2.3,99.2],[1499,46.0,7.5],[1569,38.05,127.15],[534,41.9,12.45],[1813,0.0,179.8],[1813,80.0,-40.0]]:
  pose(main,row[0],0,row[1],row[2],1.07);main._update_camera_pose();main._update_detail_patch()
  reference.distance=main.distance;reference.last_city_view=[]
  var start:=Time.get_ticks_usec();reference._update_cities();var old_us:=Time.get_ticks_usec()-start
  main.last_city_view=[];var n: int=main.city_projection_tests
  start=Time.get_ticks_usec();main._update_cities();var new_us:=Time.get_ticks_usec()-start
  var actual: Array=main.city_layer.markers;var expected: Array=reference.city_layer.markers
  var equal:=actual.size()==expected.size()
  for i: int in mini(actual.size(),expected.size()):
   if actual[i]["name"]!=expected[i]["name"] or actual[i]["point"].distance_to(expected[i]["point"])>.001:equal=false
  check(equal,"indexed city labels match complete scan at "+str(row))
  report["city_views"].append({"pose":row,"old_cpu_us":old_us,"new_cpu_us":new_us,"projection_candidates":main.city_projection_tests-n,"total_city_records":main.cities.size()})
  main.urban_scenery.view_key.clear()
  var full:=expected_clusters(main.urban_scenery,main.camera)
  start=Time.get_ticks_usec();main.urban_scenery.update_view(main.camera,main.distance,true,.3);var query_us:=Time.get_ticks_usec()-start
  var ids: Array=main.urban_scenery.active.keys();ids.sort()
  check(ids==full,"indexed scenery matches complete scan/budget at "+str(row))
  report["scenery_views"].append({"pose":row,"candidate_records":main.urban_scenery.last_candidate_count,"total_records":main.urban_scenery.clusters.size(),"query_cpu_us":query_us})
  var passes: int=main.urban_scenery.visibility_passes
  for i: int in 20:main.urban_scenery.update_view(main.camera,main.distance,true,.3)
  check(main.urban_scenery.visibility_passes==passes,"stationary scenery does not repeat visibility scans")
 reference.city_layer.free();reference.free()
 for kind: String in ["land","province","sea","water"]:
  check(main.spatial_map_layers.layers[kind]["original"].mesh==null,"no duplicate full-world mesh resident: "+kind)
 var array: Array=main.spatial_map_layers.layers["sphere"]["original"].mesh.surface_get_arrays(0)
 check(array[Mesh.ARRAY_INDEX].size()/3==65536,"far sphere has 65,536 triangles instead of 262,144")
 var uploads: int=main.terrain_shading.uploads
 for distance: float in [1.025,2.0,2.2,2.4,4.49,4.51,6.0,1.07]:
  main.distance=distance;main._update_camera_pose();main._update_detail_patch()
  check(main.spatial_map_layers.layers["sphere"]["group"].visible==(distance<4.5),"sphere detail switch is correct at "+str(distance))
 check(main.terrain_shading.uploads==uploads and uploads==1,"camera motion uploads no far-terrain cache")
 var image: Image=main.terrain_shading.texture.get_image()
 check(image.get_width()==4096 and image.has_mipmaps(),"far terrain cache has prepared resolution and filtered mip levels")
 var membership: int=main.map_rendering.membership_uploads
 for mode: int in [0,6,1,2,3,4,5,7,6,0]:
  main._map_changed(mode)
  check(main.planet_material.shader==(main.physical_shader if mode==6 else main.political_shader),"correct compiled shader for map mode "+str(mode))
  check(main.planet_material.get_shader_parameter("province_index")==main.map_rendering.province_texture,"live province lookup survives shader switching")
 check(main.map_rendering.membership_uploads==membership and main.terrain_shading.uploads==uploads,"map-mode changes upload no geometry membership or terrain cache")
 # High-frequency mouse input is reduced to its latest position per frame.
 main.screen="playing";main.dragging=false;main.console.hide();main.game_menu.hide()
 main.control_panel.hide();main.right_panel.hide();main.territory_clip.hide()
 pose(main,1813,0,2.3,99.2,1.07);main._update_camera_pose()
 var position:=Vector2(main.world_view.size)*.5
 main.pending_hover=false
 var queries: int=main.hover_queries
 for i: int in 40:
  var event:=InputEventMouseMotion.new();event.position=position+Vector2(i*.1,0)
  main._globe_input(event)
 check(main.hover_queries==queries and main.pending_hover,"mouse burst queues hover without forty terrain queries")
 main._flush_map_hover()
 check(main.hover_queries==queries+1 and not main.pending_hover,"one hover query resolves the latest mouse position")
 check(main.last_pick_key[0]==position+Vector2(3.9,0),"coalesced hover uses the final mouse position")
 main._queue_map_hover(position);main.dragging=true;main._flush_map_hover()
 check(main.hover_queries==queries+1,"dragging suppresses queued hover work")
 main.dragging=false
 var file:=FileAccess.open("res://validation_0223/runtime/decoration_cpu.json",FileAccess.WRITE)
 file.store_string(JSON.stringify(report,"\t"))
 main.set_process(true)
