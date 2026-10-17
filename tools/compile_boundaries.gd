extends SceneTree

func _initialize() -> void:
	for kind: String in ["land", "sea", "province"]:
		if not OS.get_cmdline_user_args().is_empty() and kind != OS.get_cmdline_user_args()[0]:
			continue
		# Geography edits rebuild land and province lines. The unchanged sea
		# mesh is restored from the repository; its authoring binary is optional.
		if kind == "sea" and not FileAccess.file_exists("res://tools/cartography/sea_boundaries_021.bin"):
			assert(ResourceLoader.exists("res://assets/sea_boundaries.res"))
			continue
		var file := FileAccess.open("res://tools/cartography/%s_boundaries_021.bin" % kind, FileAccess.READ)
		var vertices_count := file.get_32()
		var indices_count := file.get_32()
		var position_values := file.get_buffer(vertices_count * 12).to_float32_array()
		var tangent_values := file.get_buffer(vertices_count * 16).to_float32_array()
		var color_values := file.get_buffer(vertices_count * 16).to_float32_array()
		var uv_values := file.get_buffer(vertices_count * 8).to_float32_array()
		var indices := file.get_buffer(indices_count * 4).to_int32_array()
		var positions := PackedVector3Array()
		var normals := PackedVector3Array()
		var colors := PackedColorArray()
		var uvs := PackedVector2Array()
		var identifiers := PackedVector2Array()
		positions.resize(vertices_count); normals.resize(vertices_count); colors.resize(vertices_count); uvs.resize(vertices_count); identifiers.resize(vertices_count)
		for i: int in vertices_count:
			positions[i] = Vector3(position_values[i*3], position_values[i*3+1], position_values[i*3+2])
			normals[i] = positions[i].normalized()
			colors[i] = Color(tangent_values[i*4] * .5 + .5, tangent_values[i*4+1] * .5 + .5, tangent_values[i*4+2] * .5 + .5, 1.0)
			identifiers[i] = Vector2(roundf(color_values[i*4]*255.0) + roundf(color_values[i*4+1]*255.0)*256.0, roundf(color_values[i*4+2]*255.0) + roundf(color_values[i*4+3]*255.0)*256.0)
			uvs[i] = Vector2(uv_values[i*2], uv_values[i*2+1])
		var arrays := []
		arrays.resize(Mesh.ARRAY_MAX)
		arrays[Mesh.ARRAY_VERTEX] = positions
		arrays[Mesh.ARRAY_NORMAL] = normals
		arrays[Mesh.ARRAY_TANGENT] = tangent_values
		arrays[Mesh.ARRAY_COLOR] = colors
		arrays[Mesh.ARRAY_TEX_UV] = uvs
		arrays[Mesh.ARRAY_TEX_UV2] = identifiers
		arrays[Mesh.ARRAY_INDEX] = indices
		var mesh := ArrayMesh.new()
		mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
		var world: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json"))
		mesh.set_meta("geography_version",world["version"])
		mesh.set_meta("province_sha256",FileAccess.get_sha256("res://data/provinces.json"))
		var result := ResourceSaver.save(mesh, "res://assets/%s_boundaries.res" % kind, ResourceSaver.FLAG_COMPRESS)
		if result != OK:
			printerr("Boundary mesh could not be saved: ", kind, " ", result)
			quit(1); return
		print("COMPILED_BOUNDARIES ", kind, " vertices=", vertices_count)
	quit()
