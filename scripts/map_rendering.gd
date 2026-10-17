extends RefCounted
signal visual_changed
# Runtime map resources come from the authoritative source, not stale imported
# categorical textures. Shared by picking, fills, labels and border materials.
var region_textures: Array[Texture2D] = []
var region_images: Array[Image] = []
var province_texture: ImageTexture
var contract: Dictionary
var membership_uploads := 0
var ownership_uploads := 0
var owner_by_state: Dictionary = {}
var owner_snapshot: Array = []
var membership_bytes := PackedByteArray()
func initialize(provinces: Dictionary, regions: Dictionary = {}, countries: Dictionary = {}) -> void:
 contract=JSON.parse_string(FileAccess.get_file_as_string("res://assets/display/map_contract.json"))
 assert(contract.get("schema",0)==1,"Map build contract missing. Run tools/build_map.py.")
 assert(int(contract["province_count"])==provinces.size(),"Province topology changed. Rebuild the map.")
 for row: Array in contract["membership"]:
  assert(provinces.has(str(int(row[0])))and int(provinces[str(int(row[0]))]["region"])==int(row[1]),"Map membership changed. Run tools/build_map.py.")
 for tile: int in 4:
  var path: String="res://assets/region_ids_%d.png"%tile
  var image: Image
  # Source projects: read the exact PNG bytes, bypassing editor import caches.
  # Exported projects: use the imported texture, checked against decoded bytes.
  if FileAccess.file_exists(path):
   image=Image.new()
   var decoded: Error=image.load_png_from_buffer(FileAccess.get_file_as_bytes(path))
   assert(decoded==OK,"Province map tile could not be decoded: "+path)
  else:image=load(path).get_image()
  assert(image!=null,"Province map tile could not be read: "+path)
  if image.is_compressed():image.decompress()
  image.convert(Image.FORMAT_RGB8)
  var hash:=HashingContext.new();hash.start(HashingContext.HASH_SHA256);hash.update(image.get_data())
  assert(hash.finish().hex_encode()==str(contract["decoded_tiles"][tile]),"Province texture differs from the map build: "+path)
  region_images.append(image)
  # IDs occupy only R/G. Keep verified RGB bytes for picking, but upload the
  # same two ID channels as RG8 instead of reserving an unused blue channel.
  var gpu_image: Image=image.duplicate();gpu_image.convert(Image.FORMAT_RG8)
  region_textures.append(ImageTexture.create_from_image(gpu_image))
 if regions.is_empty() or countries.is_empty():
  var world: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json"))
  regions=world["regions"];countries=world["countries"]
 update_ownership(provinces,regions,countries)
 update_membership(provinces)
func update_membership(provinces: Dictionary) -> void:
 # RG identifies the State; BA holds its current owner. All shader boundary
 # samples resolve both from one fetch, with no ownership-dependent geometry.
 membership_bytes.resize(256*256*4);membership_bytes.fill(0)
 for p: Dictionary in provinces.values():
  var id:=int(p["id"])*4;var sid:=int(p["region"]);var owner:=int(owner_by_state.get(sid,0))
  membership_bytes[id]=sid&255;membership_bytes[id+1]=(sid>>8)&255
  membership_bytes[id+2]=owner&255;membership_bytes[id+3]=(owner>>8)&255
 membership_bytes[65535*4]=255;membership_bytes[65535*4+1]=31
 var image:=Image.create_from_data(256,256,false,Image.FORMAT_RGBA8,membership_bytes)
 if province_texture==null:province_texture=ImageTexture.create_from_image(image)
 else:province_texture.update(image)
 membership_uploads+=1
 visual_changed.emit()
func update_ownership(provinces: Dictionary, regions: Dictionary, countries: Dictionary) -> void:
 var snapshot: Array=[]
 for key: String in regions:snapshot.append_array([int(key),int(countries[regions[key]["owner"]]["index"])])
 if snapshot==owner_snapshot:return
 owner_snapshot=snapshot;owner_by_state.clear()
 for i: int in range(0,snapshot.size(),2):owner_by_state[snapshot[i]]=snapshot[i+1]
 if province_texture==null:return
 for p: Dictionary in provinces.values():
  var at:=int(p["id"])*4;var owner:=int(owner_by_state.get(int(p["region"]),0))
  membership_bytes[at+2]=owner&255;membership_bytes[at+3]=(owner>>8)&255
 province_texture.update(Image.create_from_data(256,256,false,Image.FORMAT_RGBA8,membership_bytes))
 ownership_uploads+=1
 visual_changed.emit()

func create_sea_mask_texture() -> ImageTexture:
 var file := FileAccess.open("res://assets/display/sea_mask.bwd", FileAccess.READ)
 assert(file != null, "Sea coverage mask is missing. Run Prepare_BunnyWorld.bat.")
 var width := file.get_32()
 var height := file.get_32()
 var raw := file.get_buffer(file.get_length()-8).decompress(width*height, FileAccess.COMPRESSION_DEFLATE)
 assert(raw.size() == width*height, "Invalid sea coverage mask")
 return ImageTexture.create_from_image(Image.create_from_data(width,height,false,Image.FORMAT_R8,raw))
