extends Control
# A small, fixed set of markers. No text meshes, province decoding or geometry
# generation during camera travel. Enlarged selection affects these dots only.
var host: Control
var entries: Array[Dictionary]=[]
var projected: Array[Dictionary]=[]
var last_pose:=Transform3D()
var last_camera:=Transform3D()
var last_distance: float=-1.0
var last_size:=Vector2.ZERO
var last_panels: Array=[]
func configure(main: Control) -> void:
 host=main;mouse_filter=Control.MOUSE_FILTER_IGNORE;set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
 for s: Dictionary in host.state.regions.values():
  if float(s["area_km2"])>150 and int(s["id"])!=223:continue
  var uv:=Vector2(s["map_center"][0],s["map_center"][1])
  entries.append({"state":int(s["id"]),"province":int(s["capital_province"]),"point":host.relief_surface.point_at(uv),"owner":s["owner"]})
func update_view() -> void:
 var active: bool=host.screen!="menu" and host.distance<2.1
 if visible!=active:visible=active
 if not active:return
 var panels: Array=[]
 for panel: Control in [host.control_panel,host.territory_clip,host.clock_box,host.map_box,host.top_left_box]:
  panels.append(panel.get_global_rect()if panel.is_visible_in_tree()else Rect2())
 if last_panels==panels and last_pose==host.planet.global_transform and last_camera==host.camera.global_transform and is_equal_approx(last_distance,host.distance)and last_size==host.view_container.size:return
 last_panels=panels;last_pose=host.planet.global_transform;last_camera=host.camera.global_transform;last_distance=host.distance;last_size=host.view_container.size;projected.clear()
 for entry: Dictionary in entries:
  var p: Vector3=host.planet.global_transform*entry["point"]
  if host.camera.is_position_behind(p):continue
  var n: Vector3=(p-host.planet.global_position).normalized()
  if n.dot((host.camera.global_position-p).normalized())<.12:continue
  var pixel: Vector2=host.camera.unproject_position(p)
  if not Rect2(Vector2.ZERO,host.view_container.size).has_point(pixel)or host._ui_blocks_globe(pixel):continue
  projected.append({"position":pixel,"state":entry["state"],"province":entry["province"],"owner":entry["owner"]})
 queue_redraw()
func province_at(point: Vector2) -> int:
 if not visible:return 0
 var best: int=0;var radius: float=9.0*9.0
 for entry: Dictionary in projected:
  var d: float=point.distance_squared_to(entry["position"])
  if d<radius:radius=d;best=int(entry["province"])
 return best
func _draw() -> void:
 for entry: Dictionary in projected:
  var p: Vector2=entry["position"];var points:=PackedVector2Array([p+Vector2(0,-4),p+Vector2(4,0),p+Vector2(0,4),p+Vector2(-4,0)])
  draw_colored_polygon(points,Color("12242e"))
  var color: Color=Color("82b9b1") if host.state.selected_region!=entry["state"]else Color("ede0ad")
  draw_polyline(PackedVector2Array([points[0],points[1],points[2],points[3],points[0]]),color,1.3,true)
