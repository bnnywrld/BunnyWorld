extends SceneTree
func _initialize() -> void:
	var f := FileAccess.open("res://tools/cartography/waterways_0201.bin",FileAccess.READ)
	var count := f.get_32()
	var indices_count := f.get_32()
	var raw := f.get_buffer(count*12).to_float32_array()
	var positions := PackedVector3Array()
	positions.resize(count)
	for i: int in count: positions[i]=Vector3(raw[i*3],raw[i*3+1],raw[i*3+2])
	var tangents := f.get_buffer(count*16).to_float32_array()
	var uv_raw := f.get_buffer(count*8).to_float32_array()
	var type_raw := f.get_buffer(count*8).to_float32_array()
	var uvs := PackedVector2Array()
	var types := PackedVector2Array()
	uvs.resize(count);types.resize(count)
	for i: int in count:
		uvs[i]=Vector2(uv_raw[i*2],uv_raw[i*2+1])
		types[i]=Vector2(type_raw[i*2],type_raw[i*2+1])
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX]=positions
	arrays[Mesh.ARRAY_TANGENT]=tangents
	arrays[Mesh.ARRAY_TEX_UV]=uvs
	arrays[Mesh.ARRAY_TEX_UV2]=types
	arrays[Mesh.ARRAY_INDEX]=f.get_buffer(indices_count*4).to_int32_array()
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
	var result := ResourceSaver.save(mesh,"res://assets/waterways.res",ResourceSaver.FLAG_COMPRESS)
	print("WATERWAYS_COMPILED vertices=",count)
	quit(0 if result==OK else 1)
