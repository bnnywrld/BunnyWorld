class_name UrbanScenery
extends Node3D
signal preparation_progress(completed: int,total: int)

# Only visible nearby clusters own meshes. Repeated buildings are batched;
# landmark parts are baked into a single mesh per monument. No physics,
# collision, individual shadows, annual regeneration, or building simulation.
const EARTH_METERS := 6371000.0
const SIZE_MULTIPLIER := 2.1
const DISPLAY_SCALE := 12.0 * SIZE_MULTIPLIER
const AREA_SCALE := 0.9
const BUILDING_CAP := 1600
const CLUSTER_CAP := 76
const Surface = preload("res://scripts/relief_surface.gd")
var relief: RefCounted
var clusters: Array = []
var landmarks: Array = []
var active: Dictionary = {}
var active_landmarks: Dictionary = {}
var cached_clusters: Dictionary = {}
var cached_landmarks: Dictionary = {}
var material: ShaderMaterial
var landmark_material: ShaderMaterial
var building_mesh: ArrayMesh
var timer := 0.0
var visible_buildings := 0
var peak_visible_buildings := 0
var visibility_alpha := 0.0
var mesh_builds := 0
var visibility_passes := 0
var candidate_tests := 0
var last_candidate_count := 0
var view_key: Array = []
var point_index := preload("res://scripts/map_point_index.gd").new()
var last_visibility_alpha := -1.0

func initialize(surface: RefCounted) -> void:
	relief = surface
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/urban_scenery.json"))
	clusters = data["clusters"]
	landmarks = data["landmarks"]
	for record: Dictionary in clusters:
		record["point"] = _unit(float(record["longitude"]), float(record["latitude"]))
		record["surface"] = relief.point_at(Surface.uv_of(record["point"]))
	_build_spatial_buckets()
	for record: Dictionary in landmarks:
		record["point"] = _unit(float(record["longitude"]), float(record["latitude"]))
		record["surface"] = relief.point_at(Surface.uv_of(record["point"]))
	material = ShaderMaterial.new()
	material.shader = load("res://scripts/urban_scenery.gdshader")
	landmark_material = material.duplicate()
	landmark_material.set_shader_parameter("windows_enabled", false)
	var tool := SurfaceTool.new()
	tool.begin(Mesh.PRIMITIVE_TRIANGLES)
	var box := BoxMesh.new()
	box.size = Vector3.ONE
	_piece(tool, box, Vector3.ZERO, Vector3.ONE, Color.WHITE)
	building_mesh = tool.commit()
	var prepared := 0
	for record: Dictionary in clusters:
		cached_clusters[int(record["id"])] = _cluster(record)
		mesh_builds += 1
		prepared += 1
		if prepared % 100 == 0:
			preparation_progress.emit(prepared,clusters.size())
			await get_tree().process_frame
	for record: Dictionary in landmarks:
		var node := MeshInstance3D.new()
		node.name = str(record["id"])
		node.mesh = _landmark_mesh(record)
		node.material_override = landmark_material
		node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		var height: float = maxf(100.0,float(record["height_m"])) / EARTH_METERS * 18.0 * SIZE_MULTIPLIER
		node.transform = _surface_transform(float(record["longitude"]),float(record["latitude"]),Vector3(height*float(record.get("horizontal_scale", 1.0)),height,height*float(record.get("horizontal_scale", 1.0))),0.0)
		cached_landmarks[record["id"]] = node
	print("SCENERY_PREPARED clusters=",cached_clusters.size()," landmarks=",cached_landmarks.size()," size_multiplier=",SIZE_MULTIPLIER)
	hide()

static func _unit(lon: float, lat: float) -> Vector3:
	return Surface.unit_point(Vector2((lon + 180.0) / 360.0, (90.0 - lat) / 180.0))

func update_view(camera: Camera3D, distance: float, enabled: bool, delta: float) -> void:
	visibility_alpha = smoothstep(0.0, 1.0, clampf((1.18 - distance) / .10, 0, 1)) if enabled else 0.0
	if last_visibility_alpha != visibility_alpha:
		material.set_shader_parameter("visibility_alpha", visibility_alpha)
		landmark_material.set_shader_parameter("visibility_alpha", visibility_alpha)
		last_visibility_alpha = visibility_alpha
	visible = visibility_alpha > .001
	if not visible:
		visible_buildings = 0
		view_key.clear()
		timer = .25
		if not active.is_empty() or not active_landmarks.is_empty(): _clear_active()
		return
	var key: Array = [global_transform,camera.global_transform,camera.get_viewport().size,camera.fov,camera.projection,camera.size,camera.keep_aspect,camera.frustum_offset,camera.h_offset,camera.v_offset]
	if key == view_key: return
	timer += delta
	if timer < .25: return
	timer = 0.0
	view_key = key
	visibility_passes += 1
	var candidates := _candidate_indices(camera)
	last_candidate_count = candidates.size()
	var nearby: Array[Dictionary] = []
	for index: int in candidates:
		var record: Dictionary = clusters[index]
		candidate_tests += 1
		if _in_view(record, camera):
			nearby.append({"record": record, "distance": (global_transform * record["point"]).distance_squared_to(camera.global_position)})
	nearby.sort_custom(func(a: Dictionary, b: Dictionary): return a["distance"] < b["distance"])
	var wanted: Dictionary = {}
	var budget := 0
	for entry: Dictionary in nearby:
		var record: Dictionary = entry["record"]
		var count: int = record["instances"].size()
		if wanted.size() >= CLUSTER_CAP: break
		if budget + count > BUILDING_CAP: continue
		wanted[int(record["id"])] = record
		budget += count
	for id: Variant in active.keys():
		if not wanted.has(id):
			active[id].hide()
			active.erase(id)
	# Resources already exist; view updates only select/show cached nodes.
	for id: Variant in wanted:
		if active.has(id): continue
		var node: MultiMeshInstance3D = cached_clusters[id]
		if node.get_parent() == null: add_child(node)
		node.show()
		active[id] = node
	visible_buildings = 0
	for node: MultiMeshInstance3D in active.values(): visible_buildings += node.multimesh.instance_count
	peak_visible_buildings = maxi(peak_visible_buildings, visible_buildings)
	var wanted_landmarks: Dictionary = {}
	for record: Dictionary in landmarks:
		if _in_view(record, camera): wanted_landmarks[record["id"]] = record
	for id: Variant in active_landmarks.keys():
		if not wanted_landmarks.has(id):
			active_landmarks[id].hide()
			active_landmarks.erase(id)
	for id: Variant in wanted_landmarks:
		if active_landmarks.has(id): continue
		var node: MeshInstance3D = cached_landmarks[id]
		if node.get_parent() == null: add_child(node)
		node.show()
		active_landmarks[id] = node

func _in_view(record: Dictionary, camera: Camera3D) -> bool:
	var point: Vector3 = record["point"]
	var local: Vector3 = record["surface"]
	var world: Vector3 = global_transform * local
	if world.dot(camera.global_position - world) <= 0 or camera.is_position_behind(world): return false
	var p := camera.unproject_position(world)
	return Rect2(Vector2.ZERO, Vector2(camera.get_viewport().size)).grow(160.0).has_point(p)

func _surface_transform(lon: float, lat: float, scale: Vector3, angle: float) -> Transform3D:
	var uv := Vector2((lon + 180.0) / 360.0, (90.0 - lat) / 180.0)
	var up := Surface.unit_point(uv)
	var east := Vector3(cos(deg_to_rad(lon)), 0, -sin(deg_to_rad(lon)))
	var south := east.cross(up).normalized()
	var basis := Basis(east, up, south) * Basis(Vector3.UP, angle)
	var anchor: Vector3 = relief.point_at(uv) + up * .000006
	return Transform3D(basis.scaled_local(scale), anchor)

func _cluster(record: Dictionary) -> MultiMeshInstance3D:
	var multimesh := MultiMesh.new()
	multimesh.transform_format = MultiMesh.TRANSFORM_3D
	multimesh.use_colors = true
	multimesh.mesh = building_mesh
	multimesh.instance_count = maxi(1, int(round(record["instances"].size() * 0.8))) if not record["instances"].is_empty() else 0
	var colors := [Color("d4c9b4"), Color("b8b4a6"), Color("c7b49c"), Color("a8b8c2"), Color("b6c5cb")]
	for i: int in multimesh.instance_count:
		var item: Array = record["instances"][i]
		var width := float(item[2]) / EARTH_METERS * DISPLAY_SCALE * 1.4
		var height := float(item[3]) / EARTH_METERS * DISPLAY_SCALE
		var longitude := float(record["longitude"]) + wrapf(float(item[0])-float(record["longitude"]),-180,180) * AREA_SCALE
		var latitude := lerpf(float(record["latitude"]),float(item[1]),AREA_SCALE)
		var transform := _surface_transform(longitude, latitude, Vector3(width, height, width), float(item[4]))
		transform.origin += transform.basis.y * .5
		multimesh.set_instance_transform(i, transform)
		multimesh.set_instance_color(i, colors[(i + int(record["id"])) % colors.size()])
	var node := MultiMeshInstance3D.new()
	node.name = "Urban_%d" % int(record["id"])
	node.multimesh = multimesh
	node.material_override = material
	node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return node

func _clear_active() -> void:
	for node: Node3D in active.values(): node.hide()
	for node: Node3D in active_landmarks.values(): node.hide()
	active.clear()
	active_landmarks.clear()

func _piece(tool: SurfaceTool, mesh: Mesh, at: Vector3, scale: Vector3, color: Color, rotation: Basis = Basis.IDENTITY) -> void:
	var arrays := mesh.surface_get_arrays(0)
	var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
	var normals: PackedVector3Array = arrays[Mesh.ARRAY_NORMAL]
	var uvs: PackedVector2Array = arrays[Mesh.ARRAY_TEX_UV]
	var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
	var transform := Transform3D(rotation.scaled_local(scale), at)
	var normal_basis := transform.basis.inverse().transposed()
	for index: int in indices:
		tool.set_color(color)
		tool.set_normal((normal_basis * normals[index]).normalized())
		tool.set_uv(uvs[index] if index < uvs.size() else Vector2.ZERO)
		tool.add_vertex(transform * vertices[index])

func _box(tool: SurfaceTool, at: Vector3, size: Vector3, color: Color) -> void:
	var mesh := BoxMesh.new()
	mesh.size = Vector3.ONE
	_piece(tool, mesh, at, size, color)

func _cone(tool: SurfaceTool, at: Vector3, radius: float, height: float, color: Color, sides: int = 8, top: float = 0.0) -> void:
	var mesh := CylinderMesh.new()
	mesh.bottom_radius = radius
	mesh.top_radius = top
	mesh.height = height
	mesh.radial_segments = sides
	mesh.rings = 1
	_piece(tool, mesh, at, Vector3.ONE, color)

func _beam(tool: SurfaceTool, a: Vector3, b: Vector3, width: float, color: Color) -> void:
	var direction := b - a
	var up := direction.normalized()
	var east := up.cross(Vector3.FORWARD).normalized()
	if east.length_squared() < .1: east = Vector3.RIGHT
	var basis := Basis(east, up, east.cross(up))
	var mesh := BoxMesh.new()
	mesh.size = Vector3.ONE
	_piece(tool, mesh, (a + b) * .5, Vector3(width, direction.length(), width), color, basis)

func _landmark_mesh(record: Dictionary) -> ArrayMesh:
	var tool := SurfaceTool.new()
	tool.begin(Mesh.PRIMITIVE_TRIANGLES)
	var color := Color(str(record["color"]))
	var dark := color.darkened(.24)
	var model: String = record["model"]
	if model == "lattice":
		var levels := [[0.0,.22],[.3,.11],[.55,.065],[.89,.012]]
		for level: int in 3:
			var low: Array = levels[level]; var high: Array = levels[level + 1]
			for x: float in [-1.0,1.0]:
				for z: float in [-1.0,1.0]:
					var a := Vector3(x*float(low[1]), float(low[0]), z*float(low[1]))
					var b := Vector3(x*float(high[1]), float(high[0]), z*float(high[1]))
					_beam(tool, a, b, .018 if level == 0 else .011, color)
					_beam(tool, a, Vector3(-x*float(high[1]),float(high[0]),z*float(high[1])), .006, dark)
			_box(tool, Vector3(0,float(high[0]),0), Vector3(float(high[1])*2.8,.018,float(high[1])*2.8), color.lightened(.13))
		_beam(tool,Vector3(0,.89,0),Vector3(0,1,0),.009,color)
	elif model == "liberty":
		_box(tool,Vector3(0,.18,0),Vector3(.34,.36,.3),Color("c7b28e"))
		_cone(tool,Vector3(0,.6,0),.14,.45,color,8,.07)
		_cone(tool,Vector3(0,.85,0),.066,.1,color,8,.065)
		_beam(tool,Vector3(.06,.73,0),Vector3(.17,.96,0),.045,color)
		_cone(tool,Vector3(.17,.985,0),.036,.06,Color("eac073"),6)
		_box(tool,Vector3(-.11,.7,.045),Vector3(.06,.13,.045),dark)
		for i: int in 7:
			var a := float(i) / 7.0 * TAU
			_beam(tool,Vector3(cos(a)*.05,.9,sin(a)*.05),Vector3(cos(a)*.1,.94,sin(a)*.1),.012,color)
	elif model == "clock":
		_box(tool,Vector3(0,.36,0),Vector3(.24,.72,.24),color)
		_box(tool,Vector3(0,.76,0),Vector3(.27,.15,.27),color.lightened(.1))
		for x: float in [-1.0,1.0]:
			_box(tool,Vector3(x*.137,.77,0),Vector3(.004,.105,.105),Color("f2ead6"))
			_box(tool,Vector3(0,.77,x*.137),Vector3(.105,.105,.004),Color("f2ead6"))
			_box(tool,Vector3(x*.14,.786,0),Vector3(.006,.038,.008),dark)
			_box(tool,Vector3(0,.786,x*.14),Vector3(.008,.038,.006),dark)
		_cone(tool,Vector3(0,.925,0),.18,.19,dark,4)
	elif model == "pyramids":
		for i: int in 3:
			_cone(tool,Vector3((i-1)*1.3,.5,0),.60,1.0 if i == 1 else .78,color,4)
	elif model == "colosseum":
		for i: int in 24:
			var a := float(i) / 24.0 * TAU
			_box(tool,Vector3(cos(a)*.8,.31,sin(a)*.58),Vector3(.12,.62,.1),color)
			_beam(tool,Vector3(cos(a)*.8,.61,sin(a)*.58),Vector3(cos(a+TAU/24)*.8,.61,sin(a+TAU/24)*.58),.11,color)
			_beam(tool,Vector3(cos(a)*.8,.33,sin(a)*.58),Vector3(cos(a+TAU/24)*.8,.33,sin(a+TAU/24)*.58),.055,dark)
	elif model == "opera":
		_box(tool,Vector3(0,.08,0),Vector3(1.6,.16,.8),Color("b4a38d"))
		for i: int in 5:
			var mesh := PrismMesh.new()
			mesh.size = Vector3(.48,.55 + i*.035,.62)
			_piece(tool,mesh,Vector3((i-2)*.24,.44,0),Vector3.ONE,color,Basis(Vector3.UP,.1))
	elif model == "christ":
		_box(tool,Vector3(0,.12,0),Vector3(.28,.24,.25),dark)
		_cone(tool,Vector3(0,.58,0),.11,.62,color,8,.065)
		_cone(tool,Vector3(0,.94,0),.055,.1,color,8,.05)
		_beam(tool,Vector3(-.38,.79,0),Vector3(.38,.79,0),.065,color)
	return tool.commit()

func _exit_tree() -> void:
	for cache: Dictionary in [cached_clusters,cached_landmarks]:
		for node: Node3D in cache.values():
			if is_instance_valid(node) and node.get_parent() == null: node.free()

func _build_spatial_buckets() -> void:
	var points := PackedVector3Array()
	for record: Dictionary in clusters: points.append(record["point"])
	point_index.build(points)

func _candidate_indices(camera: Camera3D) -> Array[int]:
	return point_index.candidates(global_transform.affine_inverse()*camera.global_position)
