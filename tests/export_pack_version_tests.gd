extends SceneTree

func _initialize() -> void:
	var version: String = str(ProjectSettings.get_setting("application/config/version", ""))
	if version != "0.2.0.5":
		push_error("Wrong exported project version: " + version)
		quit(1)
		return
	for path in ["res://assets/materials/terrain_materials.bwm", "res://assets/materials/terrain_materials_high.bwm", "res://scripts/resident_terrain.gd", "res://data/waterways.json", "res://scripts/foundation_ui.gd"]:
		if not FileAccess.file_exists(path) and not ResourceLoader.exists(path):
			push_error("Missing 0.2.0.5 export resource: " + path)
			quit(1)
			return
	var world: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json"))
	if str(world.get("scenario_id", "")) != "bunny_world_2000_0_2_0_3":
		push_error("Wrong embedded scenario");quit(1);return
	print("EMBEDDED_PACK_VERSION_PASS: " + version)
	quit(0)
