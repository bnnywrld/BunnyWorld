extends Control
const Surface = preload("res://scripts/relief_surface.gd")
# Fixed world-space glyphs: one mesh/atlas, no font fitting or glyph drawing in play.
var host: Control
var entries: Array[Dictionary] = []
var visible_labels: Array[Dictionary] = []
var preparation_runs := 0
var preparation_reads := 0
var geometry_builds := 0
var visibility_passes := 0
var last_view := ""
var label_mesh: MeshInstance3D
var label_material: ShaderMaterial
var visibility_image: Image
var visibility_texture: ImageTexture
var next_visibility_ms := 0
var previous_pose := Transform3D()
var previous_camera := Transform3D()
var previous_size := Vector2.ZERO
var previous_panels: Array[Rect2] = []
var previous_mask := PackedByteArray()
var last_distance := -1.0
var ownership_key: Array = []
const PATHS := {"JAP":[Vector2(132.1,34.4),Vector2(135.5,35.4),Vector2(138.7,37.1),Vector2(140.5,39.2)],"IND":[Vector2(104,-3.8),Vector2(112,-3.5),Vector2(120,-3)],"NRY":[Vector2(6.8,60.7),Vector2(11.1,64.2),Vector2(17.3,67.7)],"ENG":[Vector2(-1.3,51),Vector2(-2.7,54),Vector2(-4.3,57.5)]}
func configure(main: Control) -> void:
 host=main;mouse_filter=Control.MOUSE_FILTER_IGNORE;clip_contents=true;preparation_runs+=1
 entries.clear()
 ownership_key = _ownership_snapshot()
 var graph: Dictionary={}
 var owned: Dictionary={}
 for key: String in host.state.regions:
  graph[int(key)]=[]
  var owner: String=host.state.regions[key]["owner"]
  if not owned.has(owner):owned[owner]=[]
  owned[owner].append(int(key))
 for p: Dictionary in host.state.provinces.values():
  var sid:=int(p["region"])
  for neighbor: int in p["neighbors"]:
   var other:=int(host.state.provinces[str(neighbor)]["region"])
   if sid!=other and host.state.regions[str(sid)]["owner"]==host.state.regions[str(other)]["owner"] and other not in graph[sid]:graph[sid].append(other)
 for tag: String in host.state.countries:
  var country: Dictionary=host.state.countries[tag];var remaining: Array[int]=[]
  for value: Variant in owned.get(tag,[]):remaining.append(int(value))
  var best: Array=[];var area:=0.0
  while not remaining.is_empty():
   var component: Array=[remaining.pop_back()];var cursor:=0;var total:=0.0
   while cursor<component.size():
    var sid:=int(component[cursor]);cursor+=1;total+=float(host.state.regions[str(sid)].get("area_km2",0))
    for other: int in graph[sid]:
     if other in remaining:remaining.erase(other);component.append(other)
   if total>area:area=total;best=component
  if area<1200 or best.is_empty():continue
  var center:=Vector3.ZERO
  for sid: int in best:
   var r: Dictionary=host.state.regions[str(sid)];center+=Surface.unit_point(Vector2(r["map_center"][0],r["map_center"][1]))*float(r["area_km2"])
  center=center.normalized()
  if owner_at(Surface.uv_of(center))!=tag:
   var closest:=Vector3.ZERO;var distance:=INF
   for sid: int in best:
    var r: Dictionary=host.state.regions[str(sid)];var p:=Surface.unit_point(Vector2(r["map_center"][0],r["map_center"][1]))
    if p.distance_squared_to(center)<distance:distance=p.distance_squared_to(center);closest=p
   center=closest
  var east:=Vector3(center.z,0,-center.x).normalized();var north:=center.cross(east).normalized();var xx:=0.0;var yy:=0.0;var xy:=0.0
  for sid: int in best:
   var r: Dictionary=host.state.regions[str(sid)];var d:=Surface.unit_point(Vector2(r["map_center"][0],r["map_center"][1]))-center;var weight:=float(r["area_km2"])
   xx+=pow(d.dot(east),2)*weight;yy+=pow(d.dot(north),2)*weight;xy+=d.dot(east)*d.dot(north)*weight
  var angle:=clampf(.5*atan2(2*xy,xx-yy),-1.1,1.1) if best.size()>1 else 0.0
  var direction: Vector3=(east*cos(angle)+north*sin(angle)).normalized();var span:=clampf(sqrt(area)/6371*.90,.02,.8)
  var path:=PackedVector3Array()
  for i: int in 49:
   var uv: Vector2
   if PATHS.has(tag):
    var nodes: Array=PATHS[tag];var t: float=float(i)/48*(nodes.size()-1);var j:=mini(int(t),nodes.size()-2);var ll: Vector2=nodes[j].lerp(nodes[j+1],t-j);uv=Vector2((ll.x+180)/360,(90-ll.y)/180)
   else:
    var t: float=(float(i)/48-.5)*span;uv=Surface.uv_of((center*cos(t)+direction*sin(t)).normalized())
   path.append(host.relief_surface.point_at(uv)+Surface.unit_point(uv)*.00006)
  entries.append({"tag":tag,"text":str(country["name"]).to_upper(),"area":area,"path":path,"anchor":path[24]})
 entries.sort_custom(func(a:Dictionary,b:Dictionary):return a["area"]>b["area"])
 _build_geometry()
func owner_at(uv: Vector2) -> String:
 preparation_reads+=1
 var tx:=mini(int(uv.x*2),1);var ty:=mini(int(uv.y*2),1);var im: Image=host.region_images[ty*2+tx]
 var c:=im.get_pixel(clampi(int((uv.x*2-tx)*im.get_width()),0,im.get_width()-1),clampi(int((uv.y*2-ty)*im.get_height()),0,im.get_height()-1));var pid:=int(round(c.r*255))+256*int(round(c.g*255));var sid:=int(host.state.provinces.get(str(pid),{}).get("region",0))
 return str(host.state.regions.get(str(sid),{}).get("owner",""))

func _point_at(entry: Dictionary, offset: float, up: float = 0.0) -> Vector3:
 var path: PackedVector3Array = entry["path"]
 var lengths: PackedFloat32Array = entry["lengths"]
 var i := 1
 while i < lengths.size()-1 and lengths[i] < offset: i += 1
 var t := clampf((offset-lengths[i-1])/maxf(.000001,lengths[i]-lengths[i-1]),0,1)
 var point := path[i-1].lerp(path[i],t).normalized()
 var tangent := (path[i]-path[i-1]).normalized()
 point = (point+point.cross(tangent).normalized()*up).normalized()
 return host.relief_surface.point_at(Surface.uv_of(point))+point*.00015

func _build_geometry() -> void:
 geometry_builds += 1
 var atlas: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/display/country_glyphs.json"))
 var glyphs: Dictionary = atlas["glyphs"]
 var vertices := PackedVector3Array()
 var uvs := PackedVector2Array()
 var identifiers := PackedVector2Array()
 var indices := PackedInt32Array()
 for index: int in entries.size():
  var entry: Dictionary = entries[index]
  var path: PackedVector3Array = entry["path"]
  var lengths := PackedFloat32Array([0.0])
  for i: int in range(1,path.size()): lengths.append(lengths[-1]+path[i].distance_to(path[i-1]))
  entry["lengths"] = lengths
  var total := 0.0
  for letter: String in entry["text"]: total += float(glyphs[letter]["advance"])+float(atlas["tracking"])
  total -= float(atlas["tracking"])
  var scale: float = minf(lengths[-1]*.9/maxf(total,1.0),sqrt(float(entry["area"]))/6371.0*.22/64.0)
  entry["world_height"] = 64.0*scale
  entry["index"] = index
  var entry_start:=vertices.size()
  var cursor: float = (lengths[-1]-total*scale)*.5
  for letter: String in entry["text"]:
   var glyph: Dictionary = glyphs[letter]
   if letter != " ":
    var box: Array = glyph["box"]
    var uv: Array = glyph["uv"]
    var base := vertices.size()
    for corner: Vector2 in [Vector2(0,0),Vector2(1,0),Vector2(0,1),Vector2(1,1)]:
     vertices.append(_point_at(entry,cursor+(float(box[0])+corner.x*float(box[2]))*scale,(-float(box[1])-corner.y*float(box[3])-23.0)*scale))
     uvs.append(Vector2(float(uv[0])+corner.x*float(uv[2]),float(uv[1])+corner.y*float(uv[3])))
     identifiers.append(Vector2((float(index)+.5)/256.0,64.0*scale))
    for offset: int in [0,2,1,1,2,3]: indices.append(base+offset)
   cursor += (float(glyph["advance"])+float(atlas["tracking"]))*scale
  # Collision checks use the baked text footprint, not the much longer
  # geographic fitting path. No font measurement is needed while moving.
  var footprint:=PackedVector3Array()
  var quads: int=(vertices.size()-entry_start)/4
  for fraction: float in [0.0,.25,.5,.75,1.0]:
   var quad:=mini(quads-1,int(fraction*quads))
   if quad>=0:
    for corner: int in 4:footprint.append(vertices[entry_start+quad*4+corner])
  entry["footprint"]=footprint
 var arrays := []
 arrays.resize(Mesh.ARRAY_MAX)
 arrays[Mesh.ARRAY_VERTEX] = vertices
 arrays[Mesh.ARRAY_TEX_UV] = uvs
 arrays[Mesh.ARRAY_TEX_UV2] = identifiers
 arrays[Mesh.ARRAY_INDEX] = indices
 var mesh := ArrayMesh.new()
 mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
 if label_mesh != null: label_mesh.hide(); label_mesh.queue_free()
 label_mesh = MeshInstance3D.new()
 label_mesh.name = "CountryNamesBatch"
 label_mesh.mesh = mesh
 label_mesh.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
 visibility_image = Image.create(256,1,false,Image.FORMAT_R8)
 visibility_texture = ImageTexture.create_from_image(visibility_image)
 label_material = ShaderMaterial.new()
 label_material.shader = preload("res://scripts/country_labels.gdshader")
 # Upload explicit coverage channels once; never depend on an editor's imported
 # PNG alpha/cache or on an installed system font.
 var source:=FileAccess.open("res://assets/display/country_glyph_mask.bwd",FileAccess.READ)
 if source==null:
  push_error("Country label coverage is missing; run Prepare_BunnyWorld.bat.")
  return
 var width:=source.get_32();var height:=source.get_32()
 var raw:=source.get_buffer(source.get_length()-8).decompress(width*height*3,FileAccess.COMPRESSION_DEFLATE)
 if raw.size()!=width*height*3:
  push_error("Country label coverage is damaged.")
  return
 var image:=Image.create_from_data(width,height,false,Image.FORMAT_RGB8,raw)
 image.generate_mipmaps()
 label_material.set_shader_parameter("glyph_atlas",ImageTexture.create_from_image(image))
 label_material.set_shader_parameter("label_visibility",visibility_texture)
 label_material.render_priority = 30
 label_mesh.material_override = label_material
 host.planet.add_child(label_mesh)
 label_mesh.hide()
 previous_mask = PackedByteArray()
 last_distance = -1.0
 next_visibility_ms = 0
 last_view = ""

func update_view(force: bool = false) -> void:
 if host == null or label_mesh == null: return
 var enabled: bool = host.country_labels_enabled and host.screen != "menu" and host.distance >= 1.22
 label_mesh.visible = enabled
 if not enabled:
  visible_labels.clear()
  last_view = ""
  return
 if not is_equal_approx(last_distance,host.distance):
  label_material.set_shader_parameter("camera_distance",host.distance)
  last_distance = host.distance
 var now := Time.get_ticks_msec()
 if not force and not last_view.is_empty() and now < next_visibility_ms: return
 next_visibility_ms = now+100
 var panels: Array[Rect2] = []
 for panel: Control in [host.control_panel,host.right_panel,host.territory_clip,host.top_left_box,host.clock_box,host.map_box]:
  if panel.is_visible_in_tree() and not (panel==host.territory_clip and host.territory_collapsed): panels.append(panel.get_global_rect())
 if not force and not last_view.is_empty() and previous_pose.is_equal_approx(host.planet.global_transform) and previous_camera.is_equal_approx(host.camera.global_transform) and previous_size==host.view_container.size and panels==previous_panels: return
 previous_pose = host.planet.global_transform
 previous_camera = host.camera.global_transform
 previous_size = host.view_container.size
 previous_panels = panels
 last_view = "cached"
 visibility_passes += 1
 visible_labels.clear()
 var occupied: Array[Rect2] = []
 var mask := PackedByteArray()
 mask.resize(256)
 var ratio: Vector2 = host.view_container.size/Vector2(host.world_view.size)
 for entry: Dictionary in entries:
  var anchor: Vector3 = host.planet.global_transform*entry["anchor"]
  if host.camera.is_position_behind(anchor) or anchor.normalized().dot((host.camera.global_position-anchor).normalized()) < .25: continue
  var screen_height: float = entry["world_height"]*host.view_container.size.y/(2.0*tan(deg_to_rad(host.camera.fov)*.5)*maxf(.01,host.camera.global_position.distance_to(anchor)))
  if screen_height < 7.0: continue
  var rect := Rect2(host.camera.unproject_position(anchor)*ratio,Vector2.ZERO)
  var valid := true
  for local: Vector3 in entry["footprint"]:
   var point: Vector3 = host.planet.global_transform*local
   if host.camera.is_position_behind(point) or point.normalized().dot((host.camera.global_position-point).normalized()) < .12: valid=false;break
   rect=rect.expand(host.camera.unproject_position(point)*ratio)
  if not valid: continue
  rect=rect.grow(3.0)
  if not Rect2(Vector2(6,0),size-Vector2(12,6)).encloses(rect): continue
  var blocked := false
  for previous: Rect2 in occupied:
   if previous.intersects(rect): blocked=true;break
  if not blocked:
   for panel: Rect2 in panels:
    if panel.intersects(Rect2(rect.position+global_position,rect.size)): blocked=true;break
  if blocked: continue
  occupied.append(rect)
  mask[entry["index"]] = 255
  visible_labels.append(entry)
 if mask != previous_mask:
  visibility_image.set_data(256,1,false,Image.FORMAT_R8,mask)
  visibility_texture.update(visibility_image)
  previous_mask = mask

func _ownership_snapshot() -> Array:
 var signature: Array=[]
 for key: String in host.state.regions:signature.append(host.state.regions[key]["owner"])
 for tag: String in host.state.countries:signature.append(host.state.countries[tag]["name"])
 return signature

func refresh_if_changed() -> void:
 if host!=null and _ownership_snapshot()!=ownership_key:configure(host)
