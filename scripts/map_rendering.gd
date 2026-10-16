extends RefCounted
# Runtime map resources come from the authoritative source, not stale imported
# categorical textures. Shared by picking, fills, labels and border materials.
var region_textures: Array[Texture2D] = []
var region_images: Array[Image] = []
var province_texture: ImageTexture
var contract: Dictionary
var membership_uploads := 0
func initialize(provinces: Dictionary) -> void:
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
  region_images.append(image);region_textures.append(ImageTexture.create_from_image(image))
 update_membership(provinces)
func update_membership(provinces: Dictionary) -> void:
 var bytes:=PackedByteArray();bytes.resize(256*256*3);bytes.fill(0)
 for p: Dictionary in provinces.values():
  var id:=int(p["id"])*3;var sid:=int(p["region"])
  bytes[id]=sid&255;bytes[id+1]=(sid>>8)&255;bytes[id+2]=int(p.get("local_index",0))&255
 bytes[65535*3]=255;bytes[65535*3+1]=31
 var image:=Image.create_from_data(256,256,false,Image.FORMAT_RGB8,bytes)
 if province_texture==null:province_texture=ImageTexture.create_from_image(image)
 else:province_texture.update(image)
 membership_uploads+=1
