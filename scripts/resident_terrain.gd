extends RefCounted
# Fixed, immutable material IDs; no tile replacement, decoding or uploads in play.
var layer_count := 8
var initialized := false
var light_active := false
var quality_uploads := 0
var texture: Texture2DArray
func initialize(material: ShaderMaterial, light: bool = false) -> void:
	var file := FileAccess.open("res://assets/materials/terrain_materials.bwm" if light else "res://assets/materials/terrain_materials_high.bwm",FileAccess.READ)
	light_active = light
	quality_uploads += 1
	layer_count = file.get_32()
	var images: Array[Image] = []
	for i: int in layer_count:
		var width := file.get_32()
		var height := file.get_32()
		var format := file.get_32()
		var length := file.get_32()
		images.append(Image.create_from_data(width,height,true,format,file.get_buffer(length)))
	texture = Texture2DArray.new()
	var result := texture.create_from_images(images)
	if result!=OK: push_error("Resident terrain materials could not be prepared")
	material.set_shader_parameter("terrain_materials", texture)
	material.set_shader_parameter("terrain_types", load("res://assets/terrain_types.png"))
	material.set_shader_parameter("terrain_color", load("res://assets/terrain_color.png"))
	initialized = true

func set_light(material: ShaderMaterial, light: bool) -> void:
	if initialized and light == light_active: return
	# One explicit settings action; never load or upload on camera movement.
	# The old array loses its final references when the material is replaced.
	initialize(material, light)
