class_name WorldState
extends RefCounted
signal territory_changed(id: int,old_owner: String,new_owner: String)

const SAVE_VERSION := 21
const GovernmentRules = preload("res://scripts/government_rules.gd")
const BASE_DAILY_POLITICAL_POWER := 1.0
const HOUR_SECONDS := 3600
const SPEEDS := [1, 3, 10, 30]
var database: Dictionary = {}
var countries: Dictionary = {}
var regions: Dictionary = {}
var organizations: Dictionary = {}
var provinces: Dictionary = {}
var province_database: Dictionary = {}
var urban_database: Dictionary = {}
var selected_province: int = 0
var sea_regions: Dictionary = {}
var selected_sea: int = 0
var relation_database: Dictionary = {}
var relation_offsets: Dictionary = {}
var world_tension: float = 0.0
var tension_events: Array = []
var hour: int = 0
# Day accessor retained for dated scenario tools; simulation ticks are hours.
var day: int:
	get: return hour / 24
	set(value): hour = value * 24
var paused: bool = true
var speed: int = 1
var selected_country: String = "JAP"
var selected_region: int = 0
var player_country: String = "JAP"
var scenario_epoch: int = 0
var last_error: String = ""
var accumulator: float = 0.0
var government_properties: Dictionary = {}
var government_starting_laws: Dictionary = {}
var political_power_modifiers: Dictionary = {}

func initialize(data: Dictionary) -> void:
	database = data
	government_starting_laws = JSON.parse_string(FileAccess.get_file_as_string("res://data/government_laws_2000.json"))["countries"]
	relation_database = JSON.parse_string(FileAccess.get_file_as_string("res://data/relations.json"))
	province_database = JSON.parse_string(FileAccess.get_file_as_string("res://data/provinces.json"))
	urban_database = JSON.parse_string(FileAccess.get_file_as_string("res://data/urban_population.json"))
	sea_regions = JSON.parse_string(FileAccess.get_file_as_string("res://data/sea_regions.json"))
	var start: Array = data["start_date"]
	scenario_epoch = int(Time.get_unix_time_from_datetime_dict({"year": int(start[0]), "month": int(start[1]), "day": int(start[2]), "hour": 0, "minute": 0, "second": 0}))
	reset()

func reset() -> void:
	countries = database["countries"].duplicate(true)
	government_properties.clear()
	political_power_modifiers.clear()
	for tag: String in countries:
		government_properties[tag] = government_starting_laws[tag].duplicate(true)
		if not countries[tag].has("starting_stats"): countries[tag]["starting_stats"] = {}
		if not countries[tag]["starting_stats"].has("political_power"):
			countries[tag]["starting_stats"]["political_power"] = 100.0
	regions = database["regions"].duplicate(true)
	organizations = database["organizations"].duplicate(true)
	provinces = province_database.duplicate(true)
	selected_province = 0
	selected_sea = 0
	relation_offsets = {}
	hour = 0
	world_tension = 0.0
	tension_events = []
	paused = true
	speed = 1
	accumulator = 0.0
	selected_country = "JAP" if countries.has("JAP") else str(countries.keys()[0])
	player_country = selected_country
	selected_region = 0
	last_error = ""

func advance(delta: float) -> bool:
	if paused:
		return false
	accumulator += clampf(delta, 0.0, 0.25) * speed
	var steps := int(accumulator)
	if steps <= 0:
		return false
	accumulator -= steps
	var previous_day := day
	hour += steps
	var elapsed_days := day - previous_day
	if elapsed_days > 0:
		# Update once at crossed midnight(s), never once per rendered frame.
		for tag: String in countries:
			countries[tag]["starting_stats"]["political_power"] = political_power(tag) + elapsed_days * daily_political_power(tag)
	return true

func political_power(tag: String) -> float:
	return float(countries.get(tag, {}).get("starting_stats", {}).get("political_power", 0.0))

func political_power_breakdown(tag: String) -> Array[Dictionary]:
	var rows: Array[Dictionary] = [{"name":"Base gain", "value":BASE_DAILY_POLITICAL_POWER}]
	for source: String in political_power_modifiers.get(tag, {}):
		rows.append({"name":source, "value":float(political_power_modifiers[tag][source])})
	return rows

func daily_political_power(tag: String) -> float:
	var total := 0.0
	for row: Dictionary in political_power_breakdown(tag): total += float(row["value"])
	return total

func government_property(tag: String, key: String) -> String:
	return str(government_properties.get(tag, {}).get(key, ""))

func change_government_property(tag: String, key: String, value: String) -> bool:
	if tag != player_country or not countries.has(tag) or not GovernmentRules.valid_choice(key, value): return false
	if government_property(tag, key) == value or political_power(tag) < GovernmentRules.CHANGE_COST: return false
	if not government_properties.has(tag): government_properties[tag] = {}
	countries[tag]["starting_stats"]["political_power"] = political_power(tag) - GovernmentRules.CHANGE_COST
	government_properties[tag][key] = value
	return true

func date_dictionary() -> Dictionary:
	return Time.get_datetime_dict_from_unix_time(scenario_epoch + hour * HOUR_SECONDS)

func date_label() -> String:
	var dt := date_dictionary()
	var months := ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
	return "%02d:00  ·  %d %s %d" % [dt["hour"], dt["day"], months[int(dt["month"]) - 1], dt["year"]]

func country_metrics(tag: String) -> Dictionary:
	var population: int = 0
	var ids: Array[int] = []
	var buildings: Dictionary = {}
	for region: Dictionary in regions.values():
		if region["owner"] == tag:
			population += int(region["population"])
			ids.append(int(region["id"]))
			for key: String in region.get("buildings", {}):
				buildings[key] = int(buildings.get(key, 0)) + int(region["buildings"][key])
	return {"population": population, "regions": ids, "buildings": buildings}

func country_record(tag: String) -> Dictionary:
	return countries.get(tag, database.get("country_registry", {}).get(tag, {}))

func opinion_breakdown(from_tag: String, toward_tag: String) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	if from_tag == toward_tag: return result
	var months := float(hour) / (24.0 * 30.4375)
	for id: String in relation_database.get("pairs", {}).get(from_tag + "|" + toward_tag, []):
		var definition: Dictionary = relation_database["definitions"][id]
		if definition["trade_only"]: continue
		var expires := float(definition["expires_hour"])
		if expires >= 0 and float(hour) >= expires: continue
		var initial := float(definition["value"])
		var value := signf(initial) * maxf(0, absf(initial) - months * float(definition["decay_per_month"]))
		if not is_zero_approx(value): result.append({"name": definition["name"], "value": value})
	var offset := float(relation_offsets.get(from_tag + "|" + toward_tag, 0))
	if not is_zero_approx(offset): result.append({"name": "Diplomatic adjustment", "value": offset})
	return result

func opinion(from_tag: String, toward_tag: String) -> float:
	if from_tag == toward_tag: return 0.0
	var total := 0.0
	for entry: Dictionary in opinion_breakdown(from_tag, toward_tag): total += float(entry["value"])
	return total

func set_opinion(from_tag: String, toward_tag: String, value: float) -> bool:
	if not countries.has(from_tag) or not countries.has(toward_tag) or from_tag == toward_tag or not is_finite(value) or absf(value) > 1000: return false
	var key := from_tag + "|" + toward_tag
	relation_offsets.erase(key)
	relation_offsets[key] = value - opinion(from_tag, toward_tag)
	return true

func country_color(tag: String) -> Array:
	var c: Dictionary = countries[tag]
	var override: Array = c.get("color_override", [])
	if override.size() == 3: return override
	return database.get("cosmetic_colors", {}).get(c.get("cosmetic", ""), c["color"])

func province_owner(id: int) -> String:
	var province: Dictionary = provinces.get(str(id), {})
	return str(regions.get(str(int(province.get("region", 0))), {}).get("owner", ""))

func memberships(tag: String) -> Array[String]:
	var result: Array[String] = []
	for oid: String in organizations:
		if tag in organizations[oid]["members"]:
			result.append(oid)
	return result

func transfer_region(id: int, new_owner: String) -> bool:
	if not regions.has(str(id)) or not countries.has(new_owner):
		return false
	var old_owner: String=regions[str(id)]["owner"]
	if old_owner==new_owner:return true
	regions[str(id)]["owner"] = new_owner
	territory_changed.emit(id,old_owner,new_owner)
	return true

func save_game(path: String, view: Dictionary, save_name: String = "") -> bool:
	last_error = ""
	var region_state: Dictionary = {}
	for sid: String in regions:
		region_state[sid] = {"owner": regions[sid]["owner"], "population": regions[sid]["population"], "cores": regions[sid]["cores"], "claims": regions[sid]["claims"], "workforce": {"participation_rate":regions[sid]["workforce"]["participation_rate"],"unemployment_rate":regions[sid]["workforce"]["unemployment_rate"]}}
	var national: Dictionary = {}
	for tag: String in countries:
		national[tag] = {"stats": countries[tag].get("starting_stats", {}), "outlook": countries[tag]["outlook"], "cosmetic": countries[tag].get("cosmetic", ""), "color_override": countries[tag].get("color_override", []), "government_properties":government_properties.get(tag, {}), "political_power_modifiers":political_power_modifiers.get(tag, {})}
	var province_buildings: Dictionary = {}
	for pid: String in provinces:
		if not provinces[pid]["buildings"].is_empty(): province_buildings[pid] = provinces[pid]["buildings"]
	var payload := {"schema_version": SAVE_VERSION, "save_name": save_name, "scenario_id": database["scenario_id"],
		"source_sha256": database["source"]["sha256"], "world_tension": world_tension, "tension_events": tension_events, "hour": hour, "speed": speed,
		"selected_country": selected_country, "player_country": player_country, "selected_region": selected_region,
		"relations": relation_offsets, "selected_province": selected_province, "selected_sea": selected_sea, "province_buildings": province_buildings, "national": national, "regions": region_state, "organizations": organizations, "view": view}
	var serialized := JSON.stringify(payload)
	var envelope := JSON.stringify({"format": "BunnyWorldSave", "checksum": serialized.sha256_text(), "payload": serialized})
	var full := ProjectSettings.globalize_path(path)
	var err := DirAccess.make_dir_recursive_absolute(full.get_base_dir())
	if err != OK:
		last_error = "Could not create the save folder."
		return false
	var temp := full + ".tmp"
	var file := FileAccess.open(temp, FileAccess.WRITE)
	if file == null:
		last_error = "Could not write the save file."
		return false
	file.store_string(envelope)
	file.flush()
	var write_error := file.get_error()
	file.close()
	if write_error != OK:
		last_error = "The save could not be completed."
		return false
	var backup := full + ".bak"
	if FileAccess.file_exists(full):
		if FileAccess.file_exists(backup) and DirAccess.remove_absolute(backup) != OK:
			last_error = "Could not update the previous-save backup."
			return false
		if DirAccess.rename_absolute(full, backup) != OK:
			last_error = "Could not preserve the previous save."
			return false
	if DirAccess.rename_absolute(temp, full) != OK:
		if FileAccess.file_exists(backup) and not FileAccess.file_exists(full):
			DirAccess.rename_absolute(backup, full)
		last_error = "Could not finish writing the save."
		return false
	return true

func _invalid(message: String) -> Dictionary:
	last_error = message
	return {}

func _whole_number(value: Variant, maximum: int) -> bool:
	if not (value is int or value is float):
		return false
	return is_finite(float(value)) and float(value) >= 0.0 and float(value) <= maximum and float(value) == floor(float(value))

func load_game(path: String) -> Dictionary:
	last_error = ""
	if not FileAccess.file_exists(path):
		return _invalid("There is no saved world yet. Press Save first.")
	if FileAccess.get_file_as_bytes(path).size() > 16000000:
		return _invalid("The save is too large for this version.")
	var envelope: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not envelope is Dictionary or envelope.get("format") != "BunnyWorldSave" or not envelope.get("payload") is String:
		return _invalid("This is not a valid Bunny World save.")
	var body: String = envelope["payload"]
	if body.sha256_text() != envelope.get("checksum"):
		return _invalid("The save is incomplete or damaged. The current world has been kept.")
	var payload: Variant = JSON.parse_string(body)
	if not payload is Dictionary:
		return _invalid("The save contents could not be read.")
	if payload.get("schema_version") != SAVE_VERSION or payload.get("scenario_id") != database["scenario_id"] or payload.get("source_sha256") != database["source"]["sha256"]:
		return _invalid("This save belongs to a different version or starting world. Start a fresh campaign.")
	var tension: Variant = payload.get("world_tension")
	var events: Variant = payload.get("tension_events")
	if not (tension is int or tension is float) or not is_finite(float(tension)) or float(tension) < 0 or float(tension) > 100 or not events is Array or events.size() > 10000:
		return _invalid("The saved World Tension is invalid.")
	for event: Variant in events:
		if not event is Dictionary or not event.get("date") is String or not event.get("description") is String or not (event.get("increase") is int or event.get("increase") is float) or not is_finite(float(event["increase"])) or float(event["increase"]) < 0 or float(event["increase"]) > 100:
			return _invalid("The saved tension history is invalid.")
	var saved_hour: Variant = payload.get("hour")
	if not _whole_number(saved_hour, 8766000) or not _whole_number(payload.get("speed"), 30) or int(payload["speed"]) not in SPEEDS or not countries.has(payload.get("selected_country")):
		return _invalid("The saved clock or country is invalid.")
	if not countries.has(payload.get("player_country")):
		return _invalid("The saved player country is invalid.")
	var saved_regions: Variant = payload.get("regions")
	if not saved_regions is Dictionary or saved_regions.size() != regions.size():
		return _invalid("The saved states do not match this world.")
	for sid: String in regions:
		var entry: Variant = saved_regions.get(sid)
		if not entry is Dictionary or not _whole_number(entry.get("population"), 10000000000):
			return _invalid("The saved population is invalid.")
		if entry.get("owner") != "" and not countries.has(entry.get("owner")):
			return _invalid("The saved territorial ownership is invalid.")
		if not entry.get("workforce") is Dictionary: return _invalid("The saved workforce is invalid.")
		for rate: String in ["participation_rate","unemployment_rate"]:
			var value: Variant=entry["workforce"].get(rate)
			if not (value is int or value is float) or not is_finite(float(value)) or float(value)<0 or float(value)>1: return _invalid("The saved workforce rate is invalid.")
		for field: String in ["cores", "claims"]:
			if not entry.get(field) is Array: return _invalid("The saved territorial rights are invalid.")
			var seen: Dictionary = {}
			for tag: Variant in entry[field]:
				if not tag is String or country_record(tag).is_empty() or seen.has(tag): return _invalid("The saved territorial rights are invalid.")
				seen[tag] = true
	var saved_orgs: Variant = payload.get("organizations")
	if not saved_orgs is Dictionary or saved_orgs.size() != organizations.size():
		return _invalid("The saved organizations do not match this world.")
	for oid: String in organizations:
		var org: Variant = saved_orgs.get(oid)
		if not org is Dictionary or org.get("id") != oid or not org.get("members") is Array or not org.get("projects") is Array:
			return _invalid("An organization could not be read.")
		if not org.get("name") is String or not org.get("purpose") is String or not org.get("direction") is String or not org.get("charter") is Dictionary:
			return _invalid("The saved organization information is invalid.")
		var members: Dictionary = {}
		for member: Variant in org["members"]:
			if not member is String or not countries.has(member) or members.has(member):
				return _invalid("The saved organization membership is invalid.")
			members[member] = true
		if not (org.get("budget") is float or org.get("budget") is int) or not is_finite(float(org["budget"])) or float(org["budget"]) < 0:
			return _invalid("The saved organization budget is invalid.")
	var view: Variant = payload.get("view")
	if not view is Dictionary or not view.get("rotation") is Array or view["rotation"].size() != 2:
		return _invalid("The saved globe view is invalid.")
	for angle: Variant in view["rotation"]:
		if not (angle is int or angle is float) or not is_finite(float(angle)) or absf(float(angle)) > 100000:
			return _invalid("The saved globe rotation is invalid.")
	if not (view.get("distance") is int or view.get("distance") is float) or not is_finite(float(view["distance"])) or float(view["distance"]) < 1.015 or float(view["distance"]) > 8:
		return _invalid("The saved zoom is invalid.")
	if not _whole_number(view.get("map_mode"), 7) or not view.get("show_regions") is bool or not organizations.has(view.get("organization")):
		return _invalid("The saved map mode is invalid.")
	var saved_selected: Variant = payload.get("selected_region", 0)
	if not _whole_number(saved_selected, 8191) or (int(saved_selected) != 0 and not regions.has(str(int(saved_selected)))):
		return _invalid("The selected state is invalid.")
	var national: Variant = payload.get("national")
	if not national is Dictionary or national.size() != countries.size():
		return _invalid("Saved country values are invalid.")
	for tag: String in countries:
		var entry: Variant = national.get(tag)
		if not entry is Dictionary or not entry.get("stats") is Dictionary or not entry.get("cosmetic") is String or entry["cosmetic"].length() > 80 or entry.get("outlook") not in ["Western Outlook", "Emerging Outlook", "Non-Aligned Outlook", "Salafist Outlook", "Nationalist Outlook", "Unspecified"]:
			return _invalid("Saved country values are invalid.")
		var properties: Variant = entry.get("government_properties")
		var modifiers: Variant = entry.get("political_power_modifiers")
		if not properties is Dictionary or properties.size() != GovernmentRules.PROPERTIES.size() or not modifiers is Dictionary or modifiers.size() > 64:
			return _invalid("Saved political settings are invalid.")
		for key: Variant in properties:
			if not key is String or not properties[key] is String or not GovernmentRules.valid_choice(key, properties[key]): return _invalid("Saved government property is invalid.")
		for source: Variant in modifiers:
			var modifier: Variant = modifiers[source]
			if not source is String or source.length() > 96 or not (modifier is int or modifier is float) or not is_finite(float(modifier)) or absf(float(modifier)) > 1000:
				return _invalid("Saved political power modifier is invalid.")
		if not entry["stats"].has("political_power"): return _invalid("Saved political power is missing.")
		for value: Variant in entry["stats"].values():
			if not (value is int or value is float) or not is_finite(float(value)) or absf(float(value)) > 10000000000000000:
				return _invalid("Saved statistics are invalid.")
	var saved_province: Variant = payload.get("selected_province")
	var saved_sea: Variant = payload.get("selected_sea")
	if not _whole_number(saved_sea, 65535) or (int(saved_sea) != 0 and not sea_regions.has(str(int(saved_sea)))): return _invalid("The selected sea region is invalid.")
	if not _whole_number(saved_province, 65535) or (int(saved_province) != 0 and (not provinces.has(str(int(saved_province))) or int(provinces[str(int(saved_province))]["region"]) != int(saved_selected))):
		return _invalid("The selected province is invalid.")
	var province_buildings: Variant = payload.get("province_buildings")
	if not province_buildings is Dictionary: return _invalid("Province buildings are invalid.")
	for pid: String in province_buildings:
		if not provinces.has(pid) or not province_buildings[pid] is Dictionary: return _invalid("Province buildings are invalid.")
		for value: Variant in province_buildings[pid].values():
			if not _whole_number(value, 1000000): return _invalid("Province buildings are invalid.")
	for tag: String in countries:
		var color: Variant = national[tag].get("color_override")
		if not color is Array or color.size() not in [0, 3]: return _invalid("Country color is invalid.")
		for channel: Variant in color:
			if not _whole_number(channel, 255): return _invalid("Country color is invalid.")
	var saved_relations: Variant = payload.get("relations")
	if not saved_relations is Dictionary or saved_relations.size() > countries.size() * countries.size(): return _invalid("Saved opinions are invalid.")
	for pair: String in saved_relations:
		var parts := pair.split("|")
		var value: Variant = saved_relations[pair]
		if parts.size() != 2 or not countries.has(parts[0]) or not countries.has(parts[1]) or parts[0] == parts[1] or not (value is float or value is int) or not is_finite(float(value)) or absf(float(value)) > 10000: return _invalid("Saved opinions are invalid.")
	if not view.get("inspection_active") is bool or not view.get("relations_reverse") is bool: return _invalid("Saved selection view is invalid.")
	# Commit only after every field has been validated.
	world_tension = float(tension)
	tension_events = events.duplicate(true)
	for sid: String in regions:
		regions[sid]["owner"] = saved_regions[sid]["owner"]
		regions[sid]["population"] = int(saved_regions[sid]["population"])
		regions[sid]["cores"] = saved_regions[sid]["cores"].duplicate()
		regions[sid]["claims"] = saved_regions[sid]["claims"].duplicate()
		for rate: String in ["participation_rate","unemployment_rate"]: regions[sid]["workforce"][rate]=float(saved_regions[sid]["workforce"][rate])
	for tag: String in countries:
		government_properties[tag] = national[tag]["government_properties"].duplicate(true)
		political_power_modifiers[tag] = national[tag]["political_power_modifiers"].duplicate(true)
		countries[tag]["starting_stats"] = national[tag]["stats"].duplicate(true)
		countries[tag]["outlook"] = national[tag]["outlook"]
		countries[tag]["cosmetic"] = national[tag]["cosmetic"]
		countries[tag]["color_override"] = national[tag]["color_override"].map(func(value: Variant): return int(value))
	for pid: String in provinces: provinces[pid]["buildings"] = province_buildings.get(pid, {}).duplicate(true)
	selected_province = int(saved_province)
	selected_sea = int(saved_sea)
	relation_offsets = saved_relations.duplicate()
	organizations = saved_orgs.duplicate(true)
	hour = int(saved_hour)
	speed = int(payload["speed"])
	selected_country = payload["selected_country"]
	player_country = payload["player_country"]
	selected_region = int(saved_selected)
	paused = true
	accumulator = 0.0
	return view
