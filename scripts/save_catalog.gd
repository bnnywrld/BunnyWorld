class_name SaveCatalog
extends RefCounted

static func valid_name(value: String) -> bool:
	var name := value.strip_edges()
	if name.is_empty() or name.length() > 80 or name.ends_with(".") or name.ends_with(" "):
		return false
	for character: String in ["/", "\\", ":", "*", "?", "\"", "<", ">", "|"]:
		if character in name:
			return false
	for index: int in name.length():
		if name.unicode_at(index) < 32:
			return false
	var stem := name.get_slice(".", 0).strip_edges().to_upper()
	return stem not in ["CON", "PRN", "AUX", "NUL", "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9", "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"]

static func path_for(directory: String, name: String) -> String:
	return directory.path_join(name.strip_edges() + ".json") if valid_name(name) else ""

static func scan(directory: String) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	var dir := DirAccess.open(directory)
	if dir == null:
		return result
	var world: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json"))
	for filename: String in dir.get_files():
		if not filename.ends_with(".json"):
			continue
		var path := directory.path_join(filename)
		var caption := filename.get_basename()
		if FileAccess.get_file_as_bytes(path).size() <= 16000000:
			var envelope: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
			if envelope is Dictionary and envelope.get("format") == "BunnyWorldSave" and envelope.get("payload") is String and str(envelope["payload"]).sha256_text() == envelope.get("checksum"):
				var payload: Variant = JSON.parse_string(envelope["payload"])
				if payload is Dictionary:
					var name: String = str(payload.get("save_name", ""))
					if not name.is_empty():
						caption = name
					var ticks := int(payload.get("hour", int(payload.get("day", 0)) * 24))
					var date := Time.get_datetime_dict_from_unix_time(946684800 + ticks * 3600)
					var tag: String = str(payload.get("player_country", payload.get("selected_country", "")))
					var country_name: String = str(world["countries"].get(tag, {}).get("name", "Unknown country"))
					caption += "  ·  %02d:00 %04d-%02d-%02d  ·  %s" % [date["hour"], date["year"], date["month"], date["day"], country_name]
		result.append({"filename": filename, "path": path, "label": caption, "modified": FileAccess.get_modified_time(path)})
	result.sort_custom(func(a: Dictionary, b: Dictionary): return a["modified"] > b["modified"] if a["modified"] != b["modified"] else str(a["filename"]).naturalnocasecmp_to(str(b["filename"])) < 0)
	return result
