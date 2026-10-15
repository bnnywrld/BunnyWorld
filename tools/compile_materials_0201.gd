extends SceneTree
func _initialize() -> void:
	var file := FileAccess.open("res://assets/materials/terrain_materials.bwm",FileAccess.WRITE)
	file.store_32(8)
	for i: int in 8:
		var image := Image.load_from_file("res://assets/materials/resident_%d.png" % i)
		image.convert(Image.FORMAT_RGB8)
		image.generate_mipmaps()
		var result := image.compress(Image.COMPRESS_S3TC)
		if result!=OK:
			printerr("Material compression failed: ",result)
			quit(1)
			return
		var bytes := image.get_data()
		file.store_32(image.get_width())
		file.store_32(image.get_height())
		file.store_32(image.get_format())
		file.store_32(bytes.size())
		file.store_buffer(bytes)
		print("MATERIAL_LAYER ",i," format=",image.get_format()," bytes=",bytes.size())
	print("RESIDENT_MATERIALS_COMPILED layers=8 offline_compression=true mipmaps=true")
	quit()
