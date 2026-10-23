extends SceneTree
var checks := 0
var failures := 0
func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		push_error(label)
func _initialize() -> void: run.call_deferred()
func run() -> void:
	var game = load("res://main.tscn").instantiate()
	root.add_child(game)
	while not game.boot_complete: await process_frame
	game.set_process(false)
	game._start_selection()
	game._show_country("POL", false)
	game._begin_campaign()
	game.state.paused = true
	game.rotation_velocity = Vector2.ZERO
	if game.focus_tween != null: game.focus_tween.kill()
	game.distance = 1.08
	game._update_camera_pose()
	game._update_view_uniforms()
	var obsolete_surface := false
	var globe: MeshInstance3D
	for child: Node in game.planet.get_children():
		if child is MeshInstance3D and child.material_override is StandardMaterial3D:
			obsolete_surface = true
		if child is MeshInstance3D and child.material_override == game.planet_material:
			globe = child
	check(not obsolete_surface, "no transparent legacy surface submitted")
	check(globe != null, "single globe surface available for travel checks")
	for uniform: String in ["boundary_hint", "boundary_pairs", "boundary_distance"]:
		check(game.planet_material.get_shader_parameter(uniform) == null, "unused field not uploaded: " + uniform)
	# Idle work must remain bounded while the actual application loop runs.
	for i: int in 60: game._process(1.0 / 60.0)
	var poses: int = game.camera_pose_updates
	var uniforms: int = game.view_uniform_updates
	var culls: int = game.spatial_map_layers.horizon_passes
	var uploads: int = game.display_coverage.upload_count
	var terrain_uploads: int = game.resident_terrain.quality_uploads
	var draws: int = game.map_frame_policy.requested_frames
	for i: int in 600: game._process(1.0 / 60.0)
	check(game.camera_pose_updates == poses, "stationary view performs no camera recomputation")
	check(game.view_uniform_updates == uniforms, "stationary view performs no view-uniform updates")
	check(game.spatial_map_layers.horizon_passes == culls, "stationary view performs no horizon scans")
	check(game.display_coverage.upload_count == uploads, "stationary view uploads no coverage")
	check(game.resident_terrain.quality_uploads == terrain_uploads, "stationary view reloads no terrain")
	var idle_draws: int = game.map_frame_policy.requested_frames - draws
	check(idle_draws == 100, "idle remains exactly 10 map draws/second")
	for mode: int in 8:
		game._map_changed(mode)
		game._process(1.0 / 60.0)
		check(game.map_mode == mode, "map mode switches: %d" % mode)
		check(game.planet_material.shader == (game.physical_shader if mode == 6 else game.political_shader), "correct shader: %d" % mode)
		check(game.planet_material.get_shader_parameter("physical_mode") == (mode == 6), "mode uniforms restored: %d" % mode)
	for zoom: float in [3.65, 1.5, 1.19, 1.025, 3.65]:
		game.distance = zoom
		game._process(1.0 / 60.0)
		check(is_equal_approx(game.planet_material.get_shader_parameter("camera_distance"), zoom), "zoom reaches shader")
		check(game.show_regions == (zoom <= 1.65), "zoom updates region visibility")
	# Preserve resident-resource and passage checks from retired detail-patch tests.
	game._map_changed(6)
	var mesh_id: int = globe.mesh.get_instance_id()
	var texture_id: int = game.resident_terrain.texture.get_instance_id()
	var scenery_builds: int = game.urban_scenery.mesh_builds
	var travel_uploads: int = game.display_coverage.upload_count
	check(game.resident_terrain.texture.get_layers() == 8, "eight resident material layers")
	check(game.resident_terrain.texture.get_width() == (2048 if game.graphics_setting == 1 else 4096), "selected startup material quality")
	game.distance = 1.03
	for city: Vector2 in [Vector2(139.75,35.66),Vector2(121.5,31.2),Vector2(29,41),Vector2(14,37.5),Vector2(2.3,48.9),Vector2(121.5,31.2),Vector2(29,41),Vector2(-112,33.5),Vector2(87,28),Vector2(0,-80)]:
		game.planet.rotation = Vector3(deg_to_rad(city.y), -deg_to_rad(city.x), 0)
		game._process(1.0 / 60.0)
		game.urban_scenery.update_view(game.camera, game.distance, true, .3)
		check(globe.mesh.get_instance_id() == mesh_id, "travel retains globe mesh")
		check(game.resident_terrain.texture.get_instance_id() == texture_id, "travel retains material textures")
		check(game.urban_scenery.mesh_builds == scenery_builds, "travel builds no scenery meshes")
		check(game.display_coverage.upload_count == travel_uploads, "travel uploads no coverage")
		check(game.urban_scenery.visible_buildings <= game.urban_scenery.BUILDING_CAP, "bounded scenery during travel")
	for passage: Dictionary in game.water_passages:
		var point: Array = passage["coordinates"][passage["coordinates"].size() / 2]
		var uv := Vector2((float(point[0]) + 180.0) / 360.0, (90.0 - float(point[1])) / 180.0)
		check(game._water_passage_at(uv) == int(passage["ends"][0]), "passage CPU centreline")
		game.planet.rotation = Vector3(deg_to_rad(float(point[1])), -deg_to_rad(float(point[0])), 0)
		game.distance = 1.015
		game._update_camera_pose()
		var center := Vector2(game.world_view.size) * .5
		check(game._region_at(center) == 0, "narrow passage is selectable water")
		check(game._sea_at(center) == int(passage["ends"][0]), "narrow passage selects linked sea zone")
	# Selection changes must wake culling even without camera movement.
	game._show_sea(int(game.state.sea_regions.keys()[0]))
	check(game.display_coverage.last_sea == game.state.selected_sea, "sea selection updates coverage")
	check(game.planet_material.get_shader_parameter("sea_coverage_enabled"), "sea highlight enabled")
	var first_sea_uploads: int = game.display_coverage.upload_count
	game._update_selection_shader()
	check(game.display_coverage.upload_count == first_sea_uploads, "same sea selection does not reupload")
	game._show_country("POL", false)
	var sid: int = int(game.state.countries["POL"]["regions"][0])
	var old_owner: String = game.state.regions[str(sid)]["owner"]
	check(game.state.transfer_region(sid, "GER"), "ownership transfer accepted")
	game._process(1.0 / 60.0)
	var pid: int = int(game.state.regions[str(sid)]["provinces"][0])
	var bytes: PackedByteArray = game.map_rendering.membership_bytes
	check(int(bytes[pid*4+2]) + int(bytes[pid*4+3])*256 == int(game.state.countries["GER"]["index"]), "live owner reaches GPU membership")
	game.state.transfer_region(sid, old_owner)
	game._process(1.0 / 60.0)
	# Rendering optimizations must never suppress daily simulation.
	game.state.hour = 23
	game.state.speed = 1
	game.state.accumulator = 1.0
	game.state.paused = false
	var pp: float = game.state.political_power(game.state.player_country)
	game._process(0.0)
	check(game.state.hour == 24, "simulation advances independently of redraws")
	check(is_equal_approx(game.state.political_power(game.state.player_country), pp + game.state.daily_political_power(game.state.player_country)), "daily political power preserved")
	game.state.paused = true
	print("CLEAN_GLOBE_STABILITY checks=", checks, " failures=", failures, " idle_draws=", idle_draws)
	game.queue_free()
	await process_frame
	quit(1 if failures else 0)
