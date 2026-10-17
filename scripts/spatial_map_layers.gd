extends RefCounted
# Meshes are prepared offline and uploaded at startup. Normal-view rendering
# uses native per-chunk frustum culling; extreme distant views retain the original batch.
var layers: Dictionary={}
var close_view:=false
var prepared_chunks:=0
var geometry_builds:=0
var visibility_switches:=0
var metadata: Dictionary
var previous_camera:=Vector3.INF
var horizon_passes:=0
var maximum_distance:=4.5
func initialize() -> void:
 metadata=JSON.parse_string(FileAccess.get_file_as_string("res://assets/rendering/chunks.json"))
 assert(metadata["schema"]==1 and metadata["province_sha256"]==FileAccess.get_sha256("res://data/provinces.json"),"Render chunks do not match the current geography. Run Prepare_BunnyWorld.bat.")
func register(kind: String, original: MeshInstance3D, parent: Node3D) -> void:
 var group:=Node3D.new();group.name=kind+"_spatial";parent.add_child(group);group.hide()
 var library: MeshLibrary=load("res://"+str(metadata["layers"][kind]["path"]))
 assert(library!=null,"Render chunk resource could not be loaded. Run Prepare_BunnyWorld.bat.")
 var chunks: Array=[]
 for id: int in library.get_item_list():
  var node:=MeshInstance3D.new();node.name="Tile_%d"%id;node.mesh=library.get_item_mesh(id)
  node.material_override=original.material_override
  # Cover the shader's full 0.016 relief displacement plus screen-width ink.
  node.custom_aabb=node.mesh.get_aabb().grow(.025)
  node.cast_shadow=GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
  group.add_child(node);prepared_chunks+=1
  var bounds:=node.custom_aabb;var center:=bounds.get_center().normalized();var minimum:=1.0
  for corner: int in 8:
   var point:=bounds.get_endpoint(corner)
   minimum=minf(minimum,center.dot(point.normalized()))
  chunks.append({"node":node,"center":center,"radius":acos(clampf(minimum,-1,1))+.03})
 layers[kind]={"original":original,"group":group,"enabled":original.visible,"chunks":chunks}
 _apply(kind)
func set_enabled(kind: String, enabled: bool) -> void:
 if not layers.has(kind)or layers[kind]["enabled"]==enabled:return
 layers[kind]["enabled"]=enabled;_apply(kind)
 previous_camera=Vector3.INF
func update_view(distance: float) -> void:
 var near:=distance<maximum_distance
 if near==close_view:return
 close_view=near;visibility_switches+=1
 previous_camera=Vector3.INF
 for kind: String in layers:_apply(kind)
func _apply(kind: String) -> void:
 var row: Dictionary=layers[kind]
 row["original"].visible=row["enabled"] and not close_view
 row["group"].visible=row["enabled"] and close_view
func cull(camera: Camera3D, planet: Node3D) -> void:
 if not close_view:return
 var local_camera: Vector3=planet.global_transform.affine_inverse()*camera.global_position
 if previous_camera.is_equal_approx(local_camera):return
 previous_camera=local_camera;horizon_passes+=1
 # A unit sphere is always present. Permit points as high as radius 1.03,
 # beyond the full 1.016 terrain range and the screen-width line expansion.
 var horizon:=acos(clampf(1.0/maxf(local_camera.length(),1.000001),0,1))+acos(1.0/1.03)
 var direction:=local_camera.normalized()
 for row: Dictionary in layers.values():
  if not row["enabled"]:continue
  for chunk: Dictionary in row["chunks"]:
   var limit: float=cos(minf(PI,horizon+float(chunk["radius"])))
   var visible: bool=direction.dot(chunk["center"])>=limit
   if chunk["node"].visible!=visible:chunk["node"].visible=visible
