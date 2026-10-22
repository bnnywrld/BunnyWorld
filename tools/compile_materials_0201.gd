extends SceneTree
func _initialize() -> void:
	for size: int in [2048, 4096]:
		var path := "res://assets/materials/terrain_materials.bwm" if size == 2048 else "res://assets/materials/terrain_materials_high.bwm"
		var file := FileAccess.open(path, FileAccess.WRITE)
		file.store_32(8)
		for i: int in 8:
			var image := Image.load_from_file("res://assets/materials/resident_%d.png" % i)
			if size == 4096: image.resize(4096, 4096, Image.INTERPOLATE_LANCZOS)
			image.convert(Image.FORMAT_RGB8)
			image.generate_mipmaps()
			var result := image.compress(Image.COMPRESS_S3TC)
			if result != OK:
				printerr("Material compression failed: ", result)
				quit(1)
				return
			var bytes := image.get_data()
			file.store_32(size)
			file.store_32(size)
			file.store_32(image.get_format())
			file.store_32(bytes.size())
			file.store_buffer(bytes)
			print("MATERIAL_LAYER ", size, " ", i, " bytes=", bytes.size())
		file.flush()
	print("RESIDENT_MATERIALS_COMPILED layers=8 offline_compression=true mipmaps=true")
	quit()
