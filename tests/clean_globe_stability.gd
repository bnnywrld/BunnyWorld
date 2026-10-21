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
	for child: Node in game.planet.get_children():
		if child is MeshInstance3D and child.material_override is StandardMaterial3D:
			obsolete_surface = true
	check(not obsolete_surface, "no transparent legacy surface submitted")
	check(game.display_coverage.coast_pack == null, "unused local coast pack stays closed")
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
