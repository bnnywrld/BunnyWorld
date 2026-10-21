extends RefCounted
# Sea/coast coverage only. Land selection resolves live membership in shader.
var material: ShaderMaterial
var index: Dictionary
var pack: FileAccess
var cache: Dictionary = {}
var upload_count := 0
var last_state := -1
var last_province := -1
var last_sea := -1
var coast_index: Dictionary
var coast_pack: FileAccess
var coast_key := ""
func initialize(target: ShaderMaterial, legacy_fields: bool = true) -> void:
 material=target
 # The clean shader resolves land borders from IDs; legacy fields stay offline.
 if legacy_fields:
  var hint:=FileAccess.open("res://assets/display/boundary_hint.bwd",FileAccess.READ)
  var hw:=hint.get_32();var hh:=hint.get_32()
  var hb:=hint.get_buffer(hint.get_length()-8).decompress(hw*hh,FileAccess.COMPRESSION_DEFLATE)
  assert(hb.size()==hw*hh,"Invalid boundary acceleration field")
  material.set_shader_parameter("boundary_hint",ImageTexture.create_from_image(Image.create_from_data(hw,hh,false,Image.FORMAT_R8,hb)))
  for record: Array in [["boundary_pairs",Image.FORMAT_RGBA8,4],["boundary_distance",Image.FORMAT_RH,2]]:
   var field:=FileAccess.open("res://assets/display/"+record[0]+".bwd",FileAccess.READ)
   var width:=field.get_32();var height:=field.get_32()
   var raw:=field.get_buffer(field.get_length()-8).decompress(width*height*int(record[2]),FileAccess.COMPRESSION_DEFLATE)
   assert(raw.size()==width*height*int(record[2]),"Invalid universal boundary field")
   material.set_shader_parameter(record[0],ImageTexture.create_from_image(Image.create_from_data(width,height,false,record[1],raw)))
  coast_index=JSON.parse_string(FileAccess.get_file_as_string("res://assets/display/local_coasts.json"))
  coast_pack=FileAccess.open("res://assets/display/local_coasts.bwd",FileAccess.READ)
 index=JSON.parse_string(FileAccess.get_file_as_string("res://assets/display/sea_coverage.json"))
 pack=FileAccess.open("res://assets/display/"+str(index["data_file"]),FileAccess.READ)
 var coast:=FileAccess.open("res://assets/display/coast_distance_0217.bwd",FileAccess.READ)
 var width:=coast.get_32();var height:=coast.get_32()
 var bytes:=coast.get_buffer(coast.get_length()-8).decompress(width*height*2,FileAccess.COMPRESSION_DEFLATE)
 assert(bytes.size()==width*height*2,"Invalid current coast field")
 material.set_shader_parameter("coast_distance",ImageTexture.create_from_image(Image.create_from_data(width,height,false,Image.FORMAT_RH,bytes)))
 var tiny:=FileAccess.open("res://assets/display/tiny_land_bits.bwd",FileAccess.READ)
 var tw:=tiny.get_32();var th:=tiny.get_32()
 var tb:=tiny.get_buffer(tiny.get_length()-8).decompress(tw*th,FileAccess.COMPRESSION_DEFLATE)
 material.set_shader_parameter("tiny_land_bits",ImageTexture.create_from_image(Image.create_from_data(tw,th,false,Image.FORMAT_R8,tb)))
func select(state: int, province: int, sea: int=0) -> void:
 if state!=last_state:
  last_state=state
 if province!=last_province:
  last_province=province
 if sea!=last_sea:
  _set_tile("sea",sea,"seas");last_sea=sea
 if coast_pack != null and (state>0 or province>0):_set_local_coast(state,province)
func _set_tile(prefix: String, id: int, scope: String) -> void:
 var key:=scope+":"+str(id)
 if id<=0 or not index[scope].has(str(id)):
  material.set_shader_parameter(prefix+"_coverage_enabled",false)
  return
 if not cache.has(key):
  var record: Array=index[scope][str(id)]
  pack.seek(int(record[4]))
  var bytes:=pack.get_buffer(int(record[5])).decompress(int(record[6])*int(record[7])*2,FileAccess.COMPRESSION_DEFLATE)
  assert(bytes.size()==int(record[6])*int(record[7])*2,"Invalid selection field "+key)
  var texture:=ImageTexture.create_from_image(Image.create_from_data(int(record[6]),int(record[7]),false,Image.FORMAT_RH,bytes))
  # Keep bounded memory while switching between provinces; no camera uploads.
  if cache.size()>=12:cache.erase(cache.keys()[0])
  cache[key]={"texture":texture,"rect":Vector4(record[0],record[1],record[2],record[3])}
 material.set_shader_parameter(prefix+"_coverage",cache[key]["texture"])
 material.set_shader_parameter(prefix+"_coverage_rect",cache[key]["rect"])
 material.set_shader_parameter(prefix+"_coverage_enabled",true)
 upload_count+=1

func _set_local_coast(state: int, province: int) -> void:
 var scope: String="provinces" if province>0 and coast_index["provinces"].has(str(province)) else "states"
 if coast_index["states"].has(str(state)):
  var state_window: Array=coast_index["states"][str(state)]
  if float(state_window[2])*16384.0/float(state_window[6])<=.5:scope="states"
 var id: int=province if scope=="provinces" else state
 var key: String="coast:"+scope+":"+str(id)
 if key==coast_key:return
 coast_key=key
 if id<=0 or not coast_index[scope].has(str(id)):
  material.set_shader_parameter("local_coast_enabled",false);return
 if not cache.has(key):
  var record: Array=coast_index[scope][str(id)]
  coast_pack.seek(int(record[4]))
  var raw:=coast_pack.get_buffer(int(record[5])).decompress(int(record[6])*int(record[7])*2,FileAccess.COMPRESSION_DEFLATE)
  assert(raw.size()==int(record[6])*int(record[7])*2,"Invalid coast field "+key)
  if cache.size()>=12:cache.erase(cache.keys()[0])
  cache[key]={"texture":ImageTexture.create_from_image(Image.create_from_data(int(record[6]),int(record[7]),false,Image.FORMAT_RH,raw)),"rect":Vector4(record[0],record[1],record[2],record[3])}
 material.set_shader_parameter("local_coast",cache[key]["texture"])
 material.set_shader_parameter("local_coast_rect",cache[key]["rect"])
 material.set_shader_parameter("local_coast_enabled",true)
 upload_count+=1
