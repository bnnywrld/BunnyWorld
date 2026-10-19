extends Node3D
## Clean globe sandbox — standalone test scene.
## Replaces the over-layered globe pipeline with a single-mesh, single-material shader.
## Exposes the 4 interface hooks required by main.gd:
## 1. UV / province / sea picking
## 2. Palette & owner texture updates (supporting all 8 map modes)
## 3. Selection / hover ID uniforms
## 4. Camera distance / rotation (exact main.gd camera physics)

const MapPalette = preload("res://scripts/map_palette.gd")
const OCEAN := Color("16394d")
const OUTLOOK_COLORS := {
	"Western Outlook": Color("498fe0"),
	"Emerging Outlook": Color("d75650"),
	"Non-Aligned Outlook": Color("65b060"),
	"Unspecified": Color("718793")
}

const MAP_MODES: Array[String] = [
	"Political map",
	"Organizations",
	"Population",
	"Outlook",
	"GDP",
	"GDP per capita",
	"Physical Earth",
	"Relations"
]

# ------------------------------------------------------------------
# Nodes
# ------------------------------------------------------------------
var planet: Node3D
var globe_mesh: MeshInstance3D
var camera: Camera3D
var info_label: Label
var mode_picker: OptionButton

# ------------------------------------------------------------------
# Materials & Shaders (both pre-warmed so mode switching is instant)
# ------------------------------------------------------------------
var political_material: ShaderMaterial
var physical_material: ShaderMaterial
var active_material: ShaderMaterial

# ------------------------------------------------------------------
# Data helpers (reused from main pipeline, read-only)
# ------------------------------------------------------------------
var map_rendering: RefCounted        # map_rendering.gd
var display_coverage: RefCounted     # display_coverage.gd (boundary SDF, coast distance)
var resident_terrain: RefCounted     # resident_terrain.gd (terrain materials, terrain_types)
var terrain_shading: RefCounted      # terrain_shading.gd  (far_terrain baked normals)
var relief_surface: ReliefSurface

# ------------------------------------------------------------------
# World database (cached on load)
# ------------------------------------------------------------------
var _state_data: Dictionary

# ------------------------------------------------------------------
# Map mode
# ------------------------------------------------------------------
var map_mode: int = 0  # 0 = Political, 6 = Physical Earth
var active_org: String = ""

# ------------------------------------------------------------------
# Camera / interaction state (matching main.gd physics)
# ------------------------------------------------------------------
var distance: float = 3.65
var camera_tilt_degrees: float = 0.0
var dragging: bool = false
var last_drag_time: int = 0
var rotation_velocity: Vector2 = Vector2.ZERO
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
# Lifecycle
# ==================================================================
func _ready() -> void:
	planet = Node3D.new()
	planet.name = "Planet"
	planet.rotation_order = EULER_ORDER_XYZ
	add_child(planet)

	camera = Camera3D.new()
	camera.fov = 45.0
	camera.near = 0.01
	camera.far = 20.0
	camera.name = "Camera"
	add_child(camera)

	relief_surface = ReliefSurface.new()
	_state_data = _load_state_data()

	# Build single 384×192 sphere mesh — no detail_patch needed
	globe_mesh = MeshInstance3D.new()
	globe_mesh.mesh = _sphere_mesh(384, 192)
	globe_mesh.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	globe_mesh.name = "GlobeMesh"
	planet.add_child(globe_mesh)

	# Pre-build both materials (political + physical)
	political_material = ShaderMaterial.new()
	political_material.shader = load("res://scripts/clean_globe.gdshader")

	physical_material = ShaderMaterial.new()
	physical_material.shader = load("res://scripts/clean_globe_physical.gdshader")

	# Initialize data helpers on both materials
	map_rendering = preload("res://scripts/map_rendering.gd").new()
	map_rendering.initialize(_state_data.provinces, _state_data.regions, _state_data.countries)

	resident_terrain = preload("res://scripts/resident_terrain.gd").new()
	terrain_shading = preload("res://scripts/terrain_shading.gd").new()
	display_coverage = preload("res://scripts/display_coverage.gd").new()

	_init_material_uniforms(political_material)
	_init_material_uniforms(physical_material)

	# Set active
	active_material = political_material
	globe_mesh.material_override = active_material

	# Atmosphere rim
	var atmo := MeshInstance3D.new()
	var atmo_sphere := SphereMesh.new()
	atmo_sphere.radius = 1.028
	atmo_sphere.height = 2.056
	atmo_sphere.radial_segments = 128
	atmo_sphere.rings = 64
	atmo.mesh = atmo_sphere
	var rim_mat := ShaderMaterial.new()
	rim_mat.shader = load("res://scripts/atmosphere.gdshader")
	atmo.material_override = rim_mat
	atmo.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	atmo.name = "Atmosphere"
	planet.add_child(atmo)

	# Build palette & UI
	_rebuild_palette()
	_build_ui()

	_update_camera_pose()
	_update_camera_uniforms()

func _init_material_uniforms(mat: ShaderMaterial) -> void:
	mat.set_shader_parameter("map_resolution", Vector2(map_rendering.region_images[0].get_size()))
	for tile: int in map_rendering.region_textures.size():
		mat.set_shader_parameter("region_map_%d" % tile, map_rendering.region_textures[tile])
	mat.set_shader_parameter("palette_width", 8192.0)
	mat.set_shader_parameter("province_index", map_rendering.province_texture)
	mat.set_shader_parameter("relief_data", load("res://assets/relief_data.png"))
	mat.set_shader_parameter("sea_map", map_rendering.create_sea_mask_texture())
	mat.set_shader_parameter("urban_density", load("res://assets/urban_density.png"))
	mat.set_shader_parameter("urban_material", load("res://assets/materials/urban.png"))
	resident_terrain.initialize(mat, false)
	terrain_shading.initialize(mat)
	display_coverage.initialize(mat)

func _set_param(name: String, value: Variant) -> void:
	political_material.set_shader_parameter(name, value)
	physical_material.set_shader_parameter(name, value)

# ==================================================================
# UI
# ==================================================================
func _build_ui() -> void:
	var canvas := CanvasLayer.new()
	add_child(canvas)

	var panel := PanelContainer.new()
	panel.position = Vector2(16, 16)
	canvas.add_child(panel)

	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 6)
	panel.add_child(vbox)

	var title := Label.new()
	title.text = "Clean Globe Sandbox"
	title.add_theme_font_size_override("font_size", 16)
	title.add_theme_color_override("font_color", Color("7fe1c8"))
	vbox.add_child(title)

	mode_picker = OptionButton.new()
	for mode_name: String in MAP_MODES:
		mode_picker.add_item(mode_name)
	mode_picker.select(map_mode)
	mode_picker.item_selected.connect(_on_map_mode_selected)
	vbox.add_child(mode_picker)

	info_label = Label.new()
	info_label.add_theme_font_size_override("font_size", 13)
	info_label.add_theme_color_override("font_color", Color("d5e4ec"))
	vbox.add_child(info_label)

	var help := Label.new()
	help.text = "RMB drag: Orbit (distance-scaled) | Wheel: Zoom | LMB: Select | Keys 1-8: Map modes | P: Physical"
	help.add_theme_font_size_override("font_size", 11)
	help.add_theme_color_override("font_color", Color("718b9e"))
	vbox.add_child(help)

func _on_map_mode_selected(index: int) -> void:
	map_mode = index
	_switch_map_mode(map_mode)

func _switch_map_mode(index: int) -> void:
	map_mode = index
	if mode_picker != null and mode_picker.selected != index:
		mode_picker.select(index)

	# Swap material: mode 6 is Physical Earth, all others use Political
	if map_mode == 6:
		active_material = physical_material
	else:
		active_material = political_material

	globe_mesh.material_override = active_material
	_rebuild_palette()
	_update_camera_uniforms()

# ==================================================================
# State data loader
# ==================================================================
func _load_state_data() -> Dictionary:
	var world: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json"))
	var provinces_raw: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/provinces.json"))
	var orgs: Dictionary = world.get("organizations", {})
	if not orgs.is_empty():
		active_org = orgs.keys()[0]
	return {
		"provinces": provinces_raw,
		"regions": world.get("regions", {}),
		"countries": world.get("countries", {}),
		"organizations": orgs,
	}

# ==================================================================
# Hook 1 — Picking (exact main.gd logic)
# ==================================================================
func uv_at(screen_pos: Vector2) -> Vector2:
	var key: Array = [screen_pos, camera.global_transform, planet.global_transform]
	if key == _last_pick_key:
		return _last_pick_uv
	_last_pick_key = key
	var inverse := planet.global_transform.affine_inverse()
	var origin: Vector3 = inverse * camera.project_ray_origin(screen_pos)
	var direction: Vector3 = inverse.basis * camera.project_ray_normal(screen_pos)
	var point: Vector3 = relief_surface.ray_point(origin, direction.normalized())
	_last_pick_uv = ReliefSurface.uv_of(point) if point != Vector3.ZERO else Vector2(-1.0, -1.0)
	return _last_pick_uv

func _map_pixel_at(screen_pos: Vector2) -> Color:
	var uv := uv_at(screen_pos)
	if uv.x < 0.0: return Color.BLACK
	return map_rendering.pixel_at_uv(uv)

func region_at(screen_pos: Vector2) -> int:
	var pixel: Color = _map_pixel_at(screen_pos)
	var pid := int(round(pixel.r * 255.0)) + int(round(pixel.g * 255.0)) * 256
	if pid == 65535: return 8191
	return int(_state_data.provinces.get(str(pid), {}).get("region", 0))

func province_at_screen(screen_pos: Vector2) -> int:
	var pixel: Color = _map_pixel_at(screen_pos)
	var pid := int(round(pixel.r * 255.0)) + int(round(pixel.g * 255.0)) * 256
	return pid if _state_data.provinces.has(str(pid)) else 0

# ==================================================================
# Hook 2 — Palette / Owner updates (supporting all 8 modes)
# ==================================================================
func update_palette(colors_tex: ImageTexture, owners_tex: ImageTexture) -> void:
	palette_texture = colors_tex
	owners_texture = owners_tex
	_set_param("colors", palette_texture)
	_set_param("owners", owners_texture)

func _rebuild_palette() -> void:
	var color_image := Image.create(8192, 1, false, Image.FORMAT_RGBA8)
	var owner_image := Image.create(8192, 1, false, Image.FORMAT_RGBA8)
	color_image.fill(OCEAN)
	color_image.set_pixel(8191, 0, Color("d5e5eb"))
	owner_image.fill(Color(0, 0, 0, 1))

	var national_gdp: Dictionary = {}
	var max_gdp := 1.0
	var populations: Dictionary = {}
	for entry: Dictionary in _state_data.regions.values():
		var owner: String = entry.get("owner", "")
		populations[owner] = int(populations.get(owner, 0)) + int(entry.get("population", 0))

	for tag: String in _state_data.countries:
		var per_capita := float(_state_data.countries[tag].get("starting_stats", {}).get("gdp_per_capita_usd", 0))
		national_gdp[tag] = per_capita * float(populations.get(tag, 0))
		max_gdp = maxf(max_gdp, national_gdp[tag])

	var max_population := 1.0
	for entry: Dictionary in _state_data.regions.values():
		max_population = maxf(max_population, float(entry.get("population", 0)))

	for sid: String in _state_data.regions:
		var region: Dictionary = _state_data.regions[sid]
		var tag: String = region.get("owner", "")
		var rgb := Color("556b78")
		var index: int = 0
		if _state_data.countries.has(tag):
			var c: Dictionary = _state_data.countries[tag]
			index = int(c.get("index", 0))
			var cols: Array = c.get("color", [85, 107, 120])
			rgb = Color(float(cols[0]) / 255.0, float(cols[1]) / 255.0, float(cols[2]) / 255.0)
			if map_mode == 1:
				var org_members: Array = _state_data.organizations.get(active_org, {}).get("members", [])
				rgb = Color("4ecab1") if tag in org_members else Color("273f50")

		if map_mode == 2:
			var weight := log(1.0 + float(region.get("population", 0))) / log(1.0 + max_population)
			rgb = Color("1b354c").lerp(Color("ffd36b"), pow(weight, 4.0))
		elif map_mode == 3:
			rgb = OUTLOOK_COLORS.get(_state_data.countries.get(tag, {}).get("outlook", "Unspecified"), Color("718793"))
		elif map_mode in [4, 5]:
			var value := float(national_gdp.get(tag, 0)) if map_mode == 4 else float(_state_data.countries.get(tag, {}).get("starting_stats", {}).get("gdp_per_capita_usd", 0))
			rgb = MapPalette.economic(value, map_mode == 5)
		elif map_mode == 7:
			rgb = Color("556b78")

		color_image.set_pixel(int(sid), 0, rgb)
		owner_image.set_pixel(int(sid), 0, Color(float(index & 255) / 255.0, float(index >> 8) / 255.0, 0, 1))

	if palette_texture == null:
		palette_texture = ImageTexture.create_from_image(color_image)
		owners_texture = ImageTexture.create_from_image(owner_image)
	else:
		palette_texture.update(color_image)
		owners_texture.update(owner_image)

	_set_param("colors", palette_texture)
	_set_param("owners", owners_texture)
	_set_param("physical_mode", map_mode == 6)
	_set_param("information_mode", map_mode in [1, 2, 3, 4, 5, 7])
	_set_param("border_width", 1.15 if map_mode == 0 else 0.7)

# ==================================================================
# Hook 3 — Selection & Hover
# ==================================================================
func update_selection(country_idx: float, region_id: float, province_id: float, sea_id: float, active: bool) -> void:
	selected_country = country_idx
	selected_region = region_id
	selected_province = province_id
	selected_sea = sea_id
	inspection_active = active

	_set_param("selected_country", country_idx)
	_set_param("inspection_active", active)
	_set_param("selected_region", region_id)
	_set_param("selected_province", province_id)
	_set_param("selected_sea", sea_id)

	if display_coverage != null:
		display_coverage.select(int(region_id) if active else 0, int(province_id) if active else 0, int(sea_id))

func update_hover(country_idx: float, amount: float) -> void:
	hovered_country = country_idx
	hover_amount = amount
	_set_param("hovered_country", country_idx)
	_set_param("hover_amount", amount)

# ==================================================================
# Hook 4 — Camera & input physics (exact main.gd logic)
# ==================================================================
func _update_camera_pose() -> void:
	if camera == null: return
	var front := planet.global_transform.basis.inverse() * Vector3.BACK
	var uv := ReliefSurface.uv_of(front)
	var radius: float = 1.0 + relief_surface.height_at(uv)
	var amount := smoothstep(0.0, 1.0, clampf((1.18 - distance) / .165, 0.0, 1.0))
	camera_tilt_degrees = 38.0 * amount
	var tilt := deg_to_rad(camera_tilt_degrees)
	var anchor := Vector3(0.0, 0.0, radius)
	var clearance := maxf(.015, distance - 1.0)
	camera.position = anchor + Vector3(0.0, -sin(tilt), cos(tilt)) * clearance
	camera.look_at(anchor, Vector3.UP)

func _update_camera_uniforms() -> void:
	var vis_regions := distance <= 1.65
	if show_regions != vis_regions:
		show_regions = vis_regions
		_set_param("show_regions", show_regions)

	_set_param("camera_distance", distance)
	_set_param("region_opacity", clampf((1.65 - distance) / 0.15, 0.0, 1.0))
	_set_param("province_opacity", clampf((1.2 - distance) / 0.08, 0.0, 1.0))
	_set_param("city_detail", clampf((1.50 - distance) / .25, 0.0, 1.0))
	_set_param("far_filter", clampf((distance - 2.4) / 1.0, 0.0, 1.0))
	_set_param("border_strength", clampf((4.1 - distance) / 1.3, 0.0, 1.0))
	_set_param("coast_strength", clampf((3.2 - distance) / 1.0, 0.0, 1.0))
	_set_param("terrain_mix", clampf((1.5 - distance) / 0.25, 0.0, 1.0) if map_mode == 6 else 0.0)
	_set_param("physical_mode", map_mode == 6)

# ==================================================================
# Sphere Mesh Builder (single mesh, no detail_patch)
# ==================================================================
func _sphere_mesh(segments: int, rings: int) -> ArrayMesh:
	var vertices := PackedVector3Array()
	var normals := PackedVector3Array()
	var uvs := PackedVector2Array()
	var indices := PackedInt32Array()
	for y: int in range(rings + 1):
		var v := float(y) / rings
		var latitude := PI / 2.0 - v * PI
		for x: int in range(segments + 1):
			var u := float(x) / segments
			var longitude := (u - 0.5) * TAU
			var p := Vector3(cos(latitude) * sin(longitude), sin(latitude), cos(latitude) * cos(longitude))
			vertices.append(p)
			normals.append(p)
			uvs.append(Vector2(u, v))
	for y: int in range(rings):
		for x: int in range(segments):
			var a := y * (segments + 1) + x
			var b := a + segments + 1
			indices.append_array(PackedInt32Array([a, a + 1, b, a + 1, b + 1, b]))
	var arrays := []
	arrays.resize(Mesh.ARRAY_MAX)
	arrays[Mesh.ARRAY_VERTEX] = vertices
	arrays[Mesh.ARRAY_NORMAL] = normals
	arrays[Mesh.ARRAY_TEX_UV] = uvs
	arrays[Mesh.ARRAY_INDEX] = indices
	var mesh := ArrayMesh.new()
	mesh.add_surface_from_arrays(Mesh.PRIMITIVE_TRIANGLES, arrays)
	return mesh

# ==================================================================
# Input Handling (exact main.gd controls)
# ==================================================================
func _input(event: InputEvent) -> void:
	if event is InputEventMouseButton:
		var mb := event as InputEventMouseButton
		if mb.button_index == MOUSE_BUTTON_WHEEL_UP and mb.pressed:
			distance = maxf(1.015, 1.0 + (distance - 1.0) * 0.82)
			_update_camera_pose()
		elif mb.button_index == MOUSE_BUTTON_WHEEL_DOWN and mb.pressed:
			distance = minf(8.0, 1.0 + (distance - 1.0) / 0.82)
			_update_camera_pose()
		elif mb.button_index == MOUSE_BUTTON_RIGHT:
			dragging = mb.pressed
			if dragging:
				rotation_velocity = Vector2.ZERO
				last_drag_time = Time.get_ticks_msec()
			elif Time.get_ticks_msec() - last_drag_time > 100:
				rotation_velocity = Vector2.ZERO
		elif mb.button_index == MOUSE_BUTTON_LEFT and mb.pressed:
			rotation_velocity = Vector2.ZERO
			_handle_click(mb.position)
	elif event is InputEventMouseMotion:
		if dragging and (event.button_mask & MOUSE_BUTTON_MASK_RIGHT) != 0:
			var step: Vector2 = event.relative * 0.006 * clampf((distance - 1.0) * 0.35, 0.0025, 1.0)
			planet.rotation.y += step.x
			planet.rotation.x = clampf(planet.rotation.x + step.y, -1.5, 1.5)
			var now := Time.get_ticks_msec()
			var elapsed := maxf(0.008, float(now - last_drag_time) / 1000.0)
			rotation_velocity = rotation_velocity.lerp((step / elapsed).limit_length(0.8), 0.4)
			last_drag_time = now
		else:
			dragging = false
	elif event is InputEventKey and event.pressed:
		var ke := event as InputEventKey
		if ke.keycode == KEY_P:
			_switch_map_mode(0 if map_mode == 6 else 6)
		elif ke.keycode >= KEY_1 and ke.keycode <= KEY_8:
			var idx: int = ke.keycode - KEY_1
			if idx < MAP_MODES.size():
				_switch_map_mode(idx)

func _handle_click(position: Vector2) -> void:
	var uv := uv_at(position)
	if uv.x < 0.0:
		update_selection(0.0, 0.0, 0.0, 0.0, false)
		info_label.text = "Clicked: ocean"
		return
	var pixel: Color = map_rendering.pixel_at_uv(uv)
	var pid := int(round(pixel.r * 255.0)) + int(round(pixel.g * 255.0)) * 256
	var rid := int(_state_data.provinces.get(str(pid), {}).get("region", 0))
	var tag: String = _state_data.regions.get(str(rid), {}).get("owner", "")
	var idx: float = float(_state_data.countries.get(tag, {}).get("index", 0))
	if rid > 0:
		update_selection(idx, float(rid), float(pid), 0.0, true)
		info_label.text = "Country: %s (idx %.0f) | State %d | Province %d" % [tag, idx, rid, pid]
	else:
		update_selection(0.0, 0.0, 0.0, 0.0, false)
		info_label.text = "Clicked: unowned land"

# ==================================================================
# Process loop
# ==================================================================
func _process(delta: float) -> void:
	if not dragging:
		planet.rotation.y += rotation_velocity.x * delta
		planet.rotation.x = clampf(planet.rotation.x + rotation_velocity.y * delta, -1.5, 1.5)
		rotation_velocity *= exp(-10.0 * delta)
		if rotation_velocity.length() < 0.0001:
			rotation_velocity = Vector2.ZERO

	_update_camera_pose()
	_update_camera_uniforms()

	# Display FPS & coordinates
	var fps := Engine.get_frames_per_second()
	var mouse_uv := uv_at(get_viewport().get_mouse_position())
	var mode_name: String = MAP_MODES[map_mode]
	info_label.text = "%s | %d FPS | dist=%.2f | tilt=%.1f° | UV=(%.3f, %.3f)" % [
		mode_name, fps, distance, camera_tilt_degrees, mouse_uv.x, mouse_uv.y
	]
