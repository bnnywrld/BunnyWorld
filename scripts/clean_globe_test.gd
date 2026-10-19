extends Node3D
## Clean globe sandbox — single-shader, no detail_patch, no boundary meshes.
## Exposes the same 4 interface hooks that main.gd uses.
## Controls: right-drag to rotate, scroll to zoom, left-click to select, P to toggle physical mode.

# ------------------------------------------------------------------
# Nodes (built at runtime — no .tscn dependencies)
# ------------------------------------------------------------------
var planet: Node3D
var globe_mesh: MeshInstance3D
var camera: Camera3D
var info_label: Label

# ------------------------------------------------------------------
# Material
# ------------------------------------------------------------------
var planet_material: ShaderMaterial
var political_shader: Shader
var physical_shader: Shader

# ------------------------------------------------------------------
# Data helpers (reused from main pipeline, read-only)
# ------------------------------------------------------------------
var map_rendering: RefCounted        # map_rendering.gd
var display_coverage: RefCounted     # display_coverage.gd (loads boundary SDF, coast, sea)
var resident_terrain: RefCounted     # resident_terrain.gd (terrain atlas)
var terrain_shading: RefCounted      # terrain_shading.gd  (far_terrain baked normals)
var relief_surface: ReliefSurface

# ------------------------------------------------------------------
# State data — loaded once, cached here
# ------------------------------------------------------------------
var _state_data: Dictionary

# ------------------------------------------------------------------
# Camera / interaction state
# ------------------------------------------------------------------
var distance: float = 3.65
var dragging: bool = false
var rotation_velocity: Vector2 = Vector2.ZERO
var physical_mode: bool = false
var show_regions: bool = false

# ------------------------------------------------------------------
# Palette state (Hook 2)
# ------------------------------------------------------------------
var palette_texture: ImageTexture
var owners_texture: ImageTexture

# ------------------------------------------------------------------
# Selection state (Hook 3)
# ------------------------------------------------------------------
var selected_country: float = 0.0
var selected_region: float  = 0.0
var selected_province: float = 0.0
var selected_sea: float     = 0.0
var inspection_active: bool = false
var hovered_country: float  = 0.0
var hover_amount: float     = 0.0

# ------------------------------------------------------------------
# Picking cache (Hook 1)
# ------------------------------------------------------------------
var _last_pick_key: Array  = []
var _last_pick_uv: Vector2 = Vector2(-1.0, -1.0)

# ==================================================================
# _ready
# ==================================================================
func _ready() -> void:
	# Planet pivot
	planet      = Node3D.new()
	planet.name = "Planet"
	add_child(planet)

	# Camera
	camera      = Camera3D.new()
	camera.fov  = 45.0
	camera.near = 0.01
	camera.far  = 20.0
	camera.name = "Camera"
	add_child(camera)

	# Relief surface for CPU ray-march picking
	relief_surface = ReliefSurface.new()

	# Load world data once
	_state_data = _load_state_data()

	# Build 384×192 sphere — no detail_patch needed
	globe_mesh              = MeshInstance3D.new()
	globe_mesh.mesh         = _sphere_mesh(384, 192)
	globe_mesh.cast_shadow  = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	globe_mesh.name         = "GlobeMesh"
	planet.add_child(globe_mesh)

	# Shaders
	political_shader       = load("res://scripts/clean_globe.gdshader")
	physical_shader        = load("res://scripts/clean_globe_physical.gdshader")
	planet_material        = ShaderMaterial.new()
	planet_material.shader = political_shader

	# Map rendering — region atlas + province index
	map_rendering = preload("res://scripts/map_rendering.gd").new()
	map_rendering.initialize(_state_data.provinces, _state_data.regions, _state_data.countries)

	planet_material.set_shader_parameter("map_resolution",
		Vector2(map_rendering.region_images[0].get_size()))
	for tile: int in map_rendering.region_textures.size():
		planet_material.set_shader_parameter("region_map_%d" % tile, map_rendering.region_textures[tile])
	planet_material.set_shader_parameter("palette_width",  8192.0)
	planet_material.set_shader_parameter("province_index", map_rendering.province_texture)
	planet_material.set_shader_parameter("relief_data",    load("res://assets/relief_data.png"))
	planet_material.set_shader_parameter("sea_map",        map_rendering.create_sea_mask_texture())
	planet_material.set_shader_parameter("urban_density",  load("res://assets/urban_density.png"))
	planet_material.set_shader_parameter("urban_material", load("res://assets/materials/urban.png"))

	# Terrain atlas (biome materials, terrain_color, terrain_types)
	resident_terrain = preload("res://scripts/resident_terrain.gd").new()
	resident_terrain.initialize(planet_material, false)

	# Far-terrain baked normals
	terrain_shading = preload("res://scripts/terrain_shading.gd").new()
	terrain_shading.initialize(planet_material)

	# Boundary SDF + coast distance + tiny land bits
	display_coverage = preload("res://scripts/display_coverage.gd").new()
	display_coverage.initialize(planet_material)

	globe_mesh.material_override = planet_material

	# Atmosphere rim (reuse existing shader unchanged)
	var atmo        := MeshInstance3D.new()
	var atmo_sphere := SphereMesh.new()
	atmo_sphere.radius          = 1.028
	atmo_sphere.height          = 2.056
	atmo_sphere.radial_segments = 128
	atmo_sphere.rings           = 64
	atmo.mesh                   = atmo_sphere
	var rim_mat    := ShaderMaterial.new()
	rim_mat.shader  = load("res://scripts/atmosphere.gdshader")
	atmo.material_override = rim_mat
	atmo.cast_shadow       = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	atmo.name              = "Atmosphere"
	planet.add_child(atmo)

	# Build initial palette from world data
	_rebuild_palette()

	# HUD
	var canvas    := CanvasLayer.new()
	add_child(canvas)
	info_label    = Label.new()
	info_label.position = Vector2(10, 10)
	info_label.add_theme_color_override("font_color", Color.WHITE)
	info_label.add_theme_font_size_override("font_size", 14)
	canvas.add_child(info_label)

	_update_camera_pose()
	_update_camera_uniforms()

# ==================================================================
# State data loader — reads world.json + provinces.json, called once
# ==================================================================
func _load_state_data() -> Dictionary:
	var world: Dictionary = JSON.parse_string(
		FileAccess.get_file_as_string("res://data/world.json"))
	var provinces_raw: Dictionary = JSON.parse_string(
		FileAccess.get_file_as_string("res://data/provinces.json"))
	return {
		"provinces": provinces_raw,
		"regions":   world.get("regions",   {}),
		"countries": world.get("countries", {}),
	}

# ==================================================================
# Hook 1 — UV / Province / Sea picking
# ==================================================================
func uv_at(screen_pos: Vector2) -> Vector2:
	var key: Array = [screen_pos, camera.global_transform, planet.global_transform]
	if key == _last_pick_key:
		return _last_pick_uv
	_last_pick_key    = key
	var inverse       := planet.global_transform.affine_inverse()
	var origin        : Vector3 = inverse * camera.project_ray_origin(screen_pos)
	var direction     : Vector3 = inverse.basis * camera.project_ray_normal(screen_pos)
	var point         : Vector3 = relief_surface.ray_point(origin, direction.normalized())
	_last_pick_uv = ReliefSurface.uv_of(point) if point != Vector3.ZERO else Vector2(-1.0, -1.0)
	return _last_pick_uv

func _map_pixel_at(screen_pos: Vector2) -> Color:
	var uv := uv_at(screen_pos)
	if uv.x < 0.0: return Color.BLACK
	return map_rendering.pixel_at_uv(uv)

func region_at(screen_pos: Vector2) -> int:
	var pixel := _map_pixel_at(screen_pos)
	var pid := int(round(pixel.r * 255.0)) + int(round(pixel.g * 255.0)) * 256
	return int(_state_data.provinces.get(str(pid), {}).get("region", 0))

func province_at_screen(screen_pos: Vector2) -> int:
	var pixel := _map_pixel_at(screen_pos)
	var pid := int(round(pixel.r * 255.0)) + int(round(pixel.g * 255.0)) * 256
	return pid if _state_data.provinces.has(str(pid)) else 0

# ==================================================================
# Hook 2 — Palette / Owner texture updates
# ==================================================================
func update_palette(colors_tex: ImageTexture, owners_tex: ImageTexture) -> void:
	palette_texture = colors_tex
	owners_texture  = owners_tex
	planet_material.set_shader_parameter("colors", palette_texture)
	planet_material.set_shader_parameter("owners", owners_texture)

func _rebuild_palette() -> void:
	var color_image := Image.create(8192, 1, false, Image.FORMAT_RGBA8)
	var owner_image := Image.create(8192, 1, false, Image.FORMAT_RGBA8)
	color_image.fill(Color(0.02, 0.08, 0.14))  # ocean default
	owner_image.fill(Color(0, 0, 0, 1))
	for sid: String in _state_data.regions:
		var region: Dictionary = _state_data.regions[sid]
		var tag: String        = region.get("owner", "")
		var rgb := Color("556b78")
		var index: int = 0
		if _state_data.countries.has(tag):
			var c: Dictionary  = _state_data.countries[tag]
			index              = int(c.get("index", 0))
			var cols: Array    = c.get("color", [85, 107, 120])
			rgb = Color(float(cols[0]) / 255.0, float(cols[1]) / 255.0, float(cols[2]) / 255.0)
		color_image.set_pixel(int(sid), 0, rgb)
		owner_image.set_pixel(int(sid), 0, Color(float(index & 255) / 255.0, float(index >> 8) / 255.0, 0, 1))
	if palette_texture == null:
		palette_texture = ImageTexture.create_from_image(color_image)
		owners_texture  = ImageTexture.create_from_image(owner_image)
	else:
		palette_texture.update(color_image)
		owners_texture.update(owner_image)
	planet_material.set_shader_parameter("colors", palette_texture)
	planet_material.set_shader_parameter("owners", owners_texture)

# ==================================================================
# Hook 3 — Selection / Hover IDs
# ==================================================================
func update_selection(country_idx: float, region_id: float, province_id: float,
		sea_id: float, active: bool) -> void:
	selected_country  = country_idx
	selected_region   = region_id
	selected_province = province_id
	selected_sea      = sea_id
	inspection_active = active
	planet_material.set_shader_parameter("selected_country",  country_idx)
	planet_material.set_shader_parameter("inspection_active", active)
	planet_material.set_shader_parameter("selected_region",   region_id)
	planet_material.set_shader_parameter("selected_province", province_id)
	planet_material.set_shader_parameter("selected_sea",      sea_id)
	# Sea coverage tile upload (same as main.gd L942)
	if display_coverage != null:
		display_coverage.select(
			int(region_id)   if active else 0,
			int(province_id) if active else 0,
			int(sea_id))

func update_hover(country_idx: float, amount: float) -> void:
	hovered_country = country_idx
	hover_amount    = amount
	planet_material.set_shader_parameter("hovered_country", country_idx)
	planet_material.set_shader_parameter("hover_amount",    amount)

# ==================================================================
# Hook 4 — Camera distance / Rotation
# ==================================================================
func _update_camera_pose() -> void:
	if camera == null: return
	var front  := planet.global_transform.basis.inverse() * Vector3.BACK
	var uv     := ReliefSurface.uv_of(front)
	var radius : float = 1.0 + relief_surface.height_at(uv)
	var amount := smoothstep(0.0, 1.0, clampf((1.18 - distance) / .165, 0.0, 1.0))
	var tilt   := deg_to_rad(38.0 * amount)
	var anchor := Vector3(0.0, 0.0, radius)
	camera.position = anchor + Vector3(0.0, -sin(tilt), cos(tilt)) * maxf(.015, distance - 1.0)
	camera.look_at(anchor, Vector3.UP)

func _update_camera_uniforms() -> void:
	if planet_material == null: return
	var vis_regions := distance <= 1.65
	if show_regions != vis_regions:
		show_regions = vis_regions
		planet_material.set_shader_parameter("show_regions", show_regions)
	planet_material.set_shader_parameter("region_opacity",   clampf((1.65 - distance) / 0.15, 0.0, 1.0))
	planet_material.set_shader_parameter("camera_distance",  distance)
	planet_material.set_shader_parameter("province_opacity", clampf((1.2  - distance) / 0.08,  0.0, 1.0))
	planet_material.set_shader_parameter("city_detail",      clampf((1.50 - distance) / .25,    0.0, 1.0))
	planet_material.set_shader_parameter("far_filter",       clampf((distance - 2.4)  / 1.0,    0.0, 1.0))
	planet_material.set_shader_parameter("border_strength",  clampf((4.1 - distance)  / 1.3,    0.0, 1.0))
	planet_material.set_shader_parameter("coast_strength",   clampf((3.2 - distance)  / 1.0,    0.0, 1.0))
	planet_material.set_shader_parameter("terrain_mix",
		clampf((1.5 - distance) / 0.25, 0.0, 1.0) if physical_mode else 0.0)
	planet_material.set_shader_parameter("physical_mode", physical_mode)

# ==================================================================
# Sphere mesh builder — clean UV, no UV2 / no patch_surface flag
# ==================================================================
func _sphere_mesh(segments: int, rings: int) -> ArrayMesh:
	var vertices := PackedVector3Array()
	var normals  := PackedVector3Array()
	var uvs      := PackedVector2Array()
	var indices  := PackedInt32Array()
	for y: int in range(rings + 1):
		var v        := float(y) / rings
		var latitude := PI / 2.0 - v * PI
		for x: int in range(segments + 1):
			var u         := float(x) / segments
			var longitude := (u - 0.5) * TAU
			var p := Vector3(cos(latitude)*sin(longitude), sin(latitude), cos(latitude)*cos(longitude))
			vertices.append(p)
			normals.append(p)
			uvs.append(Vector2(u, v))
	for y: int in range(rings):
		for x: int in range(segments):
			var a := y * (segments + 1) + x
			var b := a + segments + 1
			indices.append_array(PackedInt32Array([a, a+1, b, a+1, b+1, b]))
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_TEX_UV] = uvs
	arrays[Mesh.ARRAY_INDEX]  = indices
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	return mesh

# ==================================================================
# Input — right-drag orbit, scroll zoom, left-click pick, P = toggle
# ==================================================================
func _input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		match mb.button_index:
			MOUSE_BUTTON_RIGHT:
				dragging = mb.pressed
				if mb.pressed: rotation_velocity = Vector2.ZERO
			MOUSE_BUTTON_WHEEL_UP:
				distance = maxf(1.02, distance * 0.92)
			MOUSE_BUTTON_WHEEL_DOWN:
				distance = minf(6.0,  distance * 1.08)
			MOUSE_BUTTON_LEFT:
				if mb.pressed: _handle_click(mb.position)
	elif event is InputEventMouseMotion and dragging:
		var mm := event as InputEventMouseMotion
		var d  := mm.relative * 0.003
		planet.rotation.y += d.x
		planet.rotation.x  = clampf(planet.rotation.x - d.y, -1.5, 1.5)
		rotation_velocity  = d / maxf(get_process_delta_time(), 0.001)
	elif event is InputEventKey and event.pressed:
		var ke := event as InputEventKey
		if ke.keycode == KEY_P:
			physical_mode          = not physical_mode
			planet_material.shader = physical_shader if physical_mode else political_shader
			_update_camera_uniforms()

func _handle_click(position: Vector2) -> void:
	var uv := uv_at(position)
	if uv.x < 0.0:
		update_selection(0.0, 0.0, 0.0, 0.0, false)
		info_label.text = "Clicked: ocean"
		return
	var pixel: Color = map_rendering.pixel_at_uv(uv)
	var pid   := int(round(pixel.r * 255.0)) + int(round(pixel.g * 255.0)) * 256
	var rid   := int(_state_data.provinces.get(str(pid), {}).get("region", 0))
	var tag   : String = _state_data.regions.get(str(rid), {}).get("owner", "")
	var idx   : float  = float(_state_data.countries.get(tag, {}).get("index", 0))
	if rid > 0:
		update_selection(idx, float(rid), float(pid), 0.0, true)
		info_label.text = "Province %d  |  State %d  |  Owner: %s" % [pid, rid, tag]
	else:
		update_selection(0.0, 0.0, 0.0, 0.0, false)
		info_label.text = "Clicked: unowned land"

# ==================================================================
# Process loop
# ==================================================================
func _process(delta: float) -> void:
	if not dragging:
		planet.rotation.y += rotation_velocity.x * delta
		planet.rotation.x  = clampf(planet.rotation.x + rotation_velocity.y * delta, -1.5, 1.5)
		rotation_velocity  *= exp(-10.0 * delta)
		if rotation_velocity.length() < 0.0001:
			rotation_velocity = Vector2.ZERO
	_update_camera_pose()
	_update_camera_uniforms()
	# HUD
	var fps  := Engine.get_frames_per_second()
	var uv   := uv_at(get_viewport().get_mouse_position())
	var mode := "Physical" if physical_mode else "Political"
	info_label.text = "%s  |  %d FPS  |  dist=%.2f  |  UV=(%.3f, %.3f)  |  [P] toggle  [RMB] orbit  [LMB] select" \
		% [mode, fps, distance, uv.x, uv.y]
