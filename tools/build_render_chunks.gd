extends SceneTree
# Repartition exact existing triangles; no resampling, simplification or new
# borders. Each resource item has a bounded AABB for native frustum culling.
const COLS := 8
const ROWS := 4
const LAYERS := {"sphere":"", "land":"res://assets/land_boundaries.res", "province":"res://assets/province_boundaries.res", "sea":"res://assets/sea_boundaries.res", "water":"res://assets/waterways.res"}
func _initialize() -> void:
 DirAccess.make_dir_recursive_absolute("res://assets/rendering")
 var main=load("res://scripts/main.gd").new()
 var report: Dictionary={"schema":1,"geography_version":JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json"))["version"],"province_sha256":FileAccess.get_sha256("res://data/provinces.json"),"grid":[COLS,ROWS],"shape_changed":false,"layers":{}}
 for kind: String in LAYERS:
  var source: ArrayMesh=main._sphere_mesh(512,256) if kind=="sphere" else load(LAYERS[kind])
  assert(source.get_surface_count()==1)
  var arrays:=source.surface_get_arrays(0)
  var vertices: PackedVector3Array=arrays[Mesh.ARRAY_VERTEX]
  var indices: PackedInt32Array=arrays[Mesh.ARRAY_INDEX]
  var bins: Dictionary={}
  for at: int in range(0,indices.size(),3):
   var p: Vector3=(vertices[indices[at]]+vertices[indices[at+1]]+vertices[indices[at+2]]).normalized()
   var x:=clampi(int((atan2(p.x,p.z)/TAU+.5)*COLS),0,COLS-1)
   var y:=clampi(int(acos(clampf(p.y,-1,1))/PI*ROWS),0,ROWS-1)
   var key:=y*COLS+x
   if not bins.has(key):bins[key]=PackedInt32Array()
   bins[key].append_array(PackedInt32Array([indices[at],indices[at+1],indices[at+2]]))
  var library:=MeshLibrary.new();var total:=0
  for key: int in bins:
   var input: PackedInt32Array=bins[key];var mapping: Dictionary={};var selected:=PackedInt32Array();var output:=PackedInt32Array()
   for old: int in input:
    if not mapping.has(old):mapping[old]=selected.size();selected.append(old)
    output.append(mapping[old])
   var part: Array=[];part.resize(Mesh.ARRAY_MAX)
   for slot: int in Mesh.ARRAY_INDEX:
    if arrays[slot]==null:continue
    var source_array: Variant=arrays[slot]
    var target: Variant=source_array.slice(0,0)
    if slot==Mesh.ARRAY_TANGENT:
     target.resize(selected.size()*4)
     for j: int in selected.size():
      for c: int in 4:target[j*4+c]=source_array[selected[j]*4+c]
    else:
     target.resize(selected.size())
     for j: int in selected.size():target[j]=source_array[selected[j]]
    part[slot]=target
   part[Mesh.ARRAY_INDEX]=output
   var mesh:=ArrayMesh.new();mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,part)
   library.create_item(key);library.set_item_name(key,"%s_%d"%[kind,key]);library.set_item_mesh(key,mesh)
   total+=output.size()
  assert(total==indices.size(),"All original triangles must occur exactly once")
  var path: String="res://assets/rendering/%s_chunks.res"%kind
  # Save atomically and load the on-disk resource back. The repository packs
  # these lossless bytes separately, so no nested resource compression is needed.
  var temporary: String=path.replace(".res",".prepare-tmp.res")
  assert(ResourceSaver.save(library,temporary)==OK)
  var verified: MeshLibrary=ResourceLoader.load(temporary,"MeshLibrary",ResourceLoader.CACHE_MODE_IGNORE)
  assert(verified!=null and verified.get_item_list().size()==bins.size(),"Chunk resource round-trip failed")
  assert(DirAccess.rename_absolute(temporary,path)==OK)
  report["layers"][kind]={"path":path.trim_prefix("res://"),"chunks":bins.size(),"triangles":total/3,"source_sha256":FileAccess.get_sha256(LAYERS[kind])if kind!="sphere" else "sphere_512_256","sha256":FileAccess.get_sha256(path)}
  print("RENDER_CHUNKS ",kind," triangles=",total/3," chunks=",bins.size())
 main.free()
 var file:=FileAccess.open("res://assets/rendering/chunks.json",FileAccess.WRITE);file.store_string(JSON.stringify(report,"\t"));quit()
