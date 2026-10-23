extends RefCounted
## Shared identity and color source for every religion chart and law picker.
static var data: Dictionary = {}

static func catalogue() -> Dictionary:
	if data.is_empty(): data = JSON.parse_string(FileAccess.get_file_as_string("res://data/religion_catalog.json"))
	return data

static func canonical(label: String) -> String:
	return str(catalogue().get("aliases", {}).get(label, label))

static func shares(source: Dictionary) -> Dictionary:
	var result: Dictionary = {}
	for label: String in source:
		var key := canonical(label)
		result[key] = float(result.get(key, 0.0)) + float(source[label])
	return result

static func color(label: String) -> Color:
	return Color(str(catalogue()["catalog"].get(canonical(label), {}).get("color", "647681")))

static func selectable(label: String) -> bool:
	return bool(catalogue()["catalog"].get(label, {}).get("selectable", false))

static func affiliations() -> Array:
	var result: Array = []
	for label: String in catalogue()["catalog"]:
		if selectable(label) and label != "Atheist": result.append(label)
	result.sort()
	return result
