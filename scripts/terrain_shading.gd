extends RefCounted
# A single immutable cache, prepared from relief. It stores no light direction,
# owner or camera data; rotating the globe still changes sunlight correctly.
var texture: ImageTexture
var uploads := 0
func initialize(material: ShaderMaterial) -> void:
	var file := FileAccess.open("res://assets/display/terrain_cache.bwd",FileAccess.READ)
	assert(file != null,"Distant terrain shading is missing. Run Prepare_BunnyWorld.bat.")
	var width := file.get_32()
	var height := file.get_32()
	var bytes := file.get_buffer(file.get_length()-8).decompress(width*height*4,FileAccess.COMPRESSION_DEFLATE)
	assert(bytes.size()==width*height*4,"Distant terrain shading is damaged")
	var image := Image.create_from_data(width,height,false,Image.FORMAT_RGBA8,bytes)
	image.generate_mipmaps()
	texture = ImageTexture.create_from_image(image)
	material.set_shader_parameter("far_terrain",texture)
	uploads += 1
