extends SceneTree
# Render the actual country-label shader, then check the hole and strokes of O.
# Merely detecting changed pixels would also pass for a solid white rectangle.
func _initialize() -> void: run.call_deferred()
func run() -> void:
	var viewport:=SubViewport.new()
	viewport.size=Vector2i(256,256)
	viewport.own_world_3d=true
	viewport.transparent_bg=true
	viewport.render_target_update_mode=SubViewport.UPDATE_ALWAYS
	root.add_child(viewport)
	var camera:=Camera3D.new()
	camera.position=Vector3(0,0,3)
	viewport.add_child(camera)
	camera.current=true
	var source:=FileAccess.open("res://assets/display/country_glyph_mask.bwd",FileAccess.READ)
	var w:=source.get_32();var h:=source.get_32()
	var image:=Image.create_from_data(w,h,false,Image.FORMAT_RGB8,source.get_buffer(source.get_length()-8).decompress(w*h*3,FileAccess.COMPRESSION_DEFLATE))
	image.generate_mipmaps()
	var mask:=Image.create(256,1,false,Image.FORMAT_R8)
	mask.fill(Color.WHITE)
	var material:=ShaderMaterial.new()
	material.shader=load("res://scripts/country_labels.gdshader")
	material.set_shader_parameter("glyph_atlas",ImageTexture.create_from_image(image))
	material.set_shader_parameter("label_visibility",ImageTexture.create_from_image(mask))
	var metadata: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://assets/display/country_glyphs.json"))
	var uv: Array=metadata["glyphs"]["O"]["uv"]
	var vertices:=PackedVector3Array();var uvs:=PackedVector2Array();var ids:=PackedVector2Array()
	for corner: Vector2 in [Vector2(0,0),Vector2(1,0),Vector2(0,1),Vector2(1,1)]:
		vertices.append(Vector3((corner.x-.5)*1.5,(.5-corner.y)*1.5,1))
		uvs.append(Vector2(uv[0]+corner.x*uv[2],uv[1]+corner.y*uv[3]))
		ids.append(Vector2(.5/256.0,1.5))
	var arrays:=[];arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX]=vertices;arrays[Mesh.ARRAY_TEX_UV]=uvs;arrays[Mesh.ARRAY_TEX_UV2]=ids
	arrays[Mesh.ARRAY_INDEX]=PackedInt32Array([0,2,1,1,2,3])
	var mesh:=ArrayMesh.new();mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES,arrays)
	var instance:=MeshInstance3D.new();instance.mesh=mesh;instance.material_override=material
	viewport.add_child(instance)
	for i: int in 8:await process_frame
	await RenderingServer.frame_post_draw
	var result:=viewport.get_texture().get_image()
	var hole: float=result.get_pixel(128,128).a
	var strokes:=0;var clear:=0
	for y: int in range(68,188):
		for x: int in range(68,188):
			if result.get_pixel(x,y).a>.3:strokes+=1
			if result.get_pixel(x,y).a<.01:clear+=1
	var success:=hole<.01 and strokes>1000 and clear>2000
	print("GLYPH_SHAPE_RESULT ",JSON.stringify({"success":success,"hole_alpha":hole,"stroke_pixels":strokes,"clear_pixels":clear,"renderer":RenderingServer.get_video_adapter_name()}))
	var folder:=OS.get_environment("BUNNY_VALIDATION_DIR")
	if not folder.is_empty():result.save_png(folder.path_join("glyph_O.png"))
	viewport.queue_free();await process_frame
	quit(0 if success else 1)
