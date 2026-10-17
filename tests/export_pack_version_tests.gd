extends SceneTree

func _initialize() -> void:
	var version: String = str(ProjectSettings.get_setting("application/config/version", ""))
	var expected_version := ""
	var expected_scenario := ""
	for arg: String in OS.get_cmdline_user_args():
		if arg.begins_with("--expected-version="): expected_version = arg.trim_prefix("--expected-version=")
		if arg.begins_with("--expected-scenario="): expected_scenario = arg.trim_prefix("--expected-scenario=")
	if expected_version.is_empty() or expected_scenario.is_empty():
		push_error("Pass source --expected-version and --expected-scenario when validating an export.")
		quit(1)
		return
	if version != expected_version:
		push_error("Wrong exported project version: " + version + "; expected " + expected_version)
		quit(1)
		return
	for path in ["res://assets/materials/terrain_materials.bwm", "res://scripts/resident_terrain.gd", "res://data/waterways.json", "res://scripts/foundation_ui.gd", "res://assets/display/map_contract.json", "res://assets/ui/menu_background.jpg"]:
		if not FileAccess.file_exists(path) and not ResourceLoader.exists(path):
			push_error("Missing export resource: " + path)
			quit(1)
			return
	var world: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json"))
	if str(world.get("scenario_id", "")) != expected_scenario:
		push_error("Wrong embedded scenario");quit(1);return
	print("EMBEDDED_PACK_VERSION_PASS: " + version)
	quit(0)
