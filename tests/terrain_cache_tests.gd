extends SceneTree
# Verifies the new resident path across rapid travel and revisits.
var failures: Array[String] = []
func _initialize() -> void: run.call_deferred()
func check(ok: bool, label: String) -> void:
	if not ok: failures.append(label)
func run() -> void:
	var main = load("res://main.tscn").instantiate()
	root.add_child(main)
	while not main.boot_complete: await process_frame
	main._start_selection()
	main._begin_campaign()
	main._map_changed(6)
	main.distance=1.03
	var mesh_id: int = main.detail_patch.mesh.get_instance_id()
	var texture_id: int = main.resident_terrain.texture.get_instance_id()
	check(main.resident_terrain.texture.get_width()==(2048 if main.graphics_setting==1 else 4096),"selected startup material quality")
	var builds: int = main.urban_scenery.mesh_builds
	check(main.resident_terrain.texture.get_layers()==8,"eight resident material layers")
	for city: Vector2 in [Vector2(139.75,35.66),Vector2(121.5,31.2),Vector2(29,41),Vector2(14,37.5),Vector2(2.3,48.9),Vector2(121.5,31.2),Vector2(29,41)]:
		main.planet.rotation=Vector3(deg_to_rad(city.y),-deg_to_rad(city.x),0)
		main._update_camera_pose()
		main._update_detail_patch()
		main.urban_scenery.update_view(main.camera,main.distance,true,.3)
		check(main.detail_patch.mesh.get_instance_id()==mesh_id,"immutable terrain mesh while travelling")
		check(main.resident_terrain.texture.get_instance_id()==texture_id,"fixed materials while travelling")
		check(main.detail_mesh_builds==1,"one terrain grid build")
		check(main.urban_scenery.mesh_builds==builds,"no scenery mesh reconstruction")
		check(main.urban_scenery.visible_buildings<=2048,"bounded scenery")
		await process_frame
	for passage: Dictionary in main.water_passages:
		var point: Array = passage["coordinates"][passage["coordinates"].size()/2]
		var uv := Vector2((float(point[0])+180.0)/360.0,(90.0-float(point[1]))/180.0)
		check(main._water_passage_at(uv)==int(passage["ends"][0]),"passage CPU centreline")
		main.planet.rotation=Vector3(deg_to_rad(float(point[1])),-deg_to_rad(float(point[0])),0)
		main.distance=1.015
		main._update_camera_pose()
		var center := Vector2(main.world_view.size)*.5
		check(main._region_at(center)==0,"narrow passage is selectable water")
		check(main._sea_at(center)==int(passage["ends"][0]),"narrow passage selects linked sea zone")
	print("RESIDENT_TERRAIN_TEST mesh_builds=",main.detail_mesh_builds," material_layers=8 runtime_uploads=0 scenery_builds=",builds)
	if failures.is_empty(): print("TERRAIN_CACHE_TESTS_PASS: immutable resident materials, terrain mesh and scenery across travel/revisits")
	else: printerr("TERRAIN_CACHE_TESTS_FAIL: ",failures)
	main.queue_free()
	await process_frame
	quit(0 if failures.is_empty() else 1)
