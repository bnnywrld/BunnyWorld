extends Control
const Surface = preload("res://scripts/relief_surface.gd")
# Paths are prepared once; moving the camera only projects cached points.
var host: Control
var entries: Array[Dictionary] = []
var visible_labels: Array[Dictionary] = []
var preparation_runs := 0
var preparation_reads := 0
var last_view := ""
var font: Font = ThemeDB.fallback_font
const PATHS := {"JAP":[Vector2(132.1,34.4),Vector2(135.5,35.4),Vector2(138.7,37.1),Vector2(140.5,39.2)],"IND":[Vector2(104,-3.8),Vector2(112,-3.5),Vector2(120,-3)],"NRY":[Vector2(6.8,60.7),Vector2(11.1,64.2),Vector2(17.3,67.7)]}
func configure(main: Control) -> void:
 host=main;mouse_filter=Control.MOUSE_FILTER_IGNORE;clip_contents=true;preparation_runs+=1
 var graph: Dictionary={}
 for key: String in host.state.regions:graph[int(key)]=[]
 for p: Dictionary in host.state.provinces.values():
  var sid:=int(p["region"])
  for neighbor: int in p["neighbors"]:
   var other:=int(host.state.provinces[str(neighbor)]["region"])
   if sid!=other and host.state.regions[str(sid)]["owner"]==host.state.regions[str(other)]["owner"] and other not in graph[sid]:graph[sid].append(other)
 for tag: String in host.state.countries:
  var country: Dictionary=host.state.countries[tag];var remaining: Array[int]=[]
  for value: Variant in country["regions"]:remaining.append(int(value))
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
func owner_at(uv: Vector2) -> String:
 preparation_reads+=1
 var tx:=mini(int(uv.x*2),1);var ty:=mini(int(uv.y*2),1);var im: Image=host.region_images[ty*2+tx]
 var c:=im.get_pixel(clampi(int((uv.x*2-tx)*im.get_width()),0,im.get_width()-1),clampi(int((uv.y*2-ty)*im.get_height()),0,im.get_height()-1));var pid:=int(round(c.r*255))+256*int(round(c.g*255));var sid:=int(host.state.provinces.get(str(pid),{}).get("region",0))
 return str(host.state.regions.get(str(sid),{}).get("owner",""))
func path_at(points: PackedVector2Array, distance: float) -> Dictionary:
 for i: int in range(1,points.size()):
  var length: float=points[i].distance_to(points[i-1])
  if distance<=length or i==points.size()-1:return {"point":points[i-1].lerp(points[i],clampf(distance/maxf(length,.001),0,1)),"angle":(points[i]-points[i-1]).angle()}
  distance-=length
 return {"point":points[-1],"angle":0.0}
func text_width(text: String, font_size: int, tracking: float) -> float:
 var width:=0.0
 for letter: String in text:width+=font.get_string_size(letter,HORIZONTAL_ALIGNMENT_LEFT,-1,font_size).x+tracking
 return maxf(0,width-tracking)
func update_view() -> void:
 if host==null:return
 var key: String=str(host.planet.global_transform)+str(host.camera.global_transform)+str(host.view_container.size)+str(host.screen)+str(host.country_labels_enabled)+str(host.control_panel.get_global_rect())+str(host.control_panel.visible)+str(host.right_panel.get_global_rect())+str(host.right_panel.visible)+str(host.territory_clip.get_global_rect())+str(host.territory_clip.visible)+str(host.territory_collapsed)
 if key==last_view:return
 last_view=key;visible_labels.clear()
 if not host.country_labels_enabled or host.screen=="menu" or host.distance<1.22:queue_redraw();return
 var occupied: Array[Rect2]=[]
 for entry: Dictionary in entries:
  var anchor: Vector3=host.planet.global_transform*entry["anchor"]
  if host.camera.is_position_behind(anchor) or anchor.normalized().dot((host.camera.global_position-anchor).normalized())<.25:continue
  var points:=PackedVector2Array();var valid:=true;var path: PackedVector3Array=entry["path"]
  for i: int in range(0,49,4):
   var p: Vector3=host.planet.global_transform*path[i]
   if host.camera.is_position_behind(p) or p.normalized().dot((host.camera.global_position-p).normalized())<.08:valid=false;break
   points.append(host.camera.unproject_position(p)*host.view_container.size/Vector2(host.world_view.size))
  if not valid:continue
  if points[-1].x<points[0].x:points.reverse()
  var width:=0.0
  for i: int in range(1,points.size()):width+=points[i].distance_to(points[i-1])
  var text: String=entry["text"];var font_size:=27;var tracking:=1.7
  while font_size>10 and text_width(text,font_size,tracking)>width*.92:font_size-=1;tracking=clampf(font_size*.065,.6,1.7)
  var tw:=text_width(text,font_size,tracking)
  if tw>width*1.1 or tw>size.x*.75:continue
  var rect:=Rect2(path_at(points,(width-tw)*.5)["point"],Vector2.ZERO)
  for i: int in 9:rect=rect.expand(path_at(points,(width-tw)*.5+tw*float(i)/8)["point"])
  rect=rect.grow(font_size*.7+2)
  if not Rect2(Vector2(8,100),size-Vector2(16,108)).encloses(rect):continue
  var blocked:=false
  for previous: Rect2 in occupied:
   if previous.intersects(rect):blocked=true;break
  for panel: Control in [host.control_panel,host.right_panel,host.territory_clip,host.top_left_box,host.clock_box,host.map_box]:
   if panel.is_visible_in_tree() and not (panel==host.territory_clip and host.territory_collapsed) and panel.get_global_rect().intersects(Rect2(rect.position+global_position,rect.size)):blocked=true;break
  if blocked:continue
  occupied.append(rect);visible_labels.append({"tag":entry["tag"],"text":text,"points":points,"width":width,"text_width":tw,"font_size":font_size,"tracking":tracking,"alpha":smoothstep(1.22,1.48,host.distance)*.88})
 queue_redraw()
func _draw() -> void:
 for entry: Dictionary in visible_labels:
  var offset: float=(entry["width"]-entry["text_width"])*.5
  for letter: String in entry["text"]:
   var advance:=font.get_string_size(letter,HORIZONTAL_ALIGNMENT_LEFT,-1,entry["font_size"]).x;var at:=path_at(entry["points"],offset+advance*.5);draw_set_transform(at["point"],at["angle"])
   var baseline:=Vector2(-advance*.5,entry["font_size"]*.33);draw_string_outline(font,baseline,letter,HORIZONTAL_ALIGNMENT_LEFT,-1,entry["font_size"],3,Color(.025,.05,.06,entry["alpha"]*.9));draw_string(font,baseline,letter,HORIZONTAL_ALIGNMENT_LEFT,-1,entry["font_size"],Color(.93,.91,.84,entry["alpha"]));offset+=advance+entry["tracking"]
 draw_set_transform(Vector2.ZERO)
