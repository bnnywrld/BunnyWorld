extends RefCounted
signal changed
const Institutions = preload("res://scripts/research_institutions.gd")
var owner: WeakRef
var world: RefCounted:
	get: return owner.get_ref()
var catalog: Dictionary = {}
var categories: Array = []
var starting: Dictionary = {}
var ahead_factor := 1.0
var completed: Dictionary = {}
var progress: Dictionary = {}
var assignments: Dictionary = {}
var notifications: Array = []

func initialize(state: RefCounted) -> void:
	owner = weakref(state)
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/research.json"))
	catalog = data["technologies"]
	categories = data["categories"]
	starting = data["countries"]
	ahead_factor = float(data["ahead_factor"])

func reset() -> void:
	completed.clear()
	progress.clear()
	assignments.clear()
	notifications.clear()
	for tag: String in world.countries:
		completed[tag] = {}
		for tech: String in starting.get(tag, []): completed[tag][tech] = true
		progress[tag] = {}
		assignments[tag] = {}
	changed.emit()

func reason(tag: String, tech: String) -> String:
	if not catalog.has(tech) or not completed.has(tag): return "Unknown technology"
	if completed[tag].has(tech): return "Researched"
	for institution: String in assignments[tag]:
		if assignments[tag][institution] == tech: return "Researching at " + institution
	var t: Dictionary = catalog[tech]
	for other: String in t["exclusive"]:
		if completed[tag].has(other): return "Exclusive with " + str(catalog[other]["name"])
	var parent_known: bool = t["parents"].is_empty()
	for parent: String in t["parents"]:
		if completed[tag].has(parent): parent_known = true
	if not parent_known: return "Requires a preceding technology"
	for dependency: String in t["dependencies"]:
		if not completed[tag].has(dependency): return "Requires " + str(catalog[dependency]["name"])
	return ""

func start(tag: String, institution: String, tech: String) -> bool:
	if tag != world.player_country or institution not in Institutions.for_country(world, tag): return false
	if not reason(tag, tech).is_empty(): return false
	# Progress belongs to the nation and technology, so switching institutions or
	# pausing an assignment never loses previous work.
	assignments[tag][institution] = tech
	changed.emit()
	return true

func stop(tag: String, institution: String) -> void:
	if assignments.get(tag, {}).erase(institution): changed.emit()

func penalty(tech: String, at_hour: int = -1) -> float:
	if at_hour < 0: at_hour = world.hour
	var epoch := int(Time.get_unix_time_from_datetime_dict({"year":int(catalog[tech]["year"]), "month":1, "day":1, "hour":0, "minute":0, "second":0}))
	var ahead_days := maxf(0, (epoch - world.scenario_epoch - at_hour * 3600) / 86400.0)
	return 1.0 + ahead_days / 365.0 * ahead_factor

func fraction(tag: String, tech: String) -> float:
	return clampf(float(progress[tag].get(tech, 0)) / float(catalog[tech]["days"]), 0, 1)

func remaining_days(tag: String, tech: String) -> int:
	# Forecast the same daily integration as the simulation, including the
	# declining ahead-of-time penalty. Only called on UI refresh, never per frame.
	var remaining := float(catalog[tech]["days"]) - float(progress[tag].get(tech, 0))
	var days := 0
	while remaining > 0 and days < 100000:
		days += 1
		remaining -= float(world.economy.research_multiplier(tag)) / penalty(tech, (world.day + days) * 24)
	return days

func advance_days(count: int) -> void:
	var tag: String = world.player_country
	if assignments.get(tag, {}).is_empty(): return
	for offset: int in count:
		var at_hour: int = (world.day - count + offset + 1) * 24
		for institution: String in assignments[tag].keys():
			var tech: String = assignments[tag][institution]
			progress[tag][tech] = float(progress[tag].get(tech, 0)) + float(world.economy.research_multiplier(tag)) / penalty(tech, at_hour)
			if float(progress[tag][tech]) + 0.000001 >= float(catalog[tech]["days"]):
				completed[tag][tech] = true
				progress[tag].erase(tech)
				assignments[tag].erase(institution)
				notifications.append({"tag":tag, "tech":tech, "institution":institution, "hour":at_hour})
	changed.emit()

func dismiss(index: int) -> void:
	if index >= 0 and index < notifications.size():
		notifications.remove_at(index)
		changed.emit()

func export_state() -> Dictionary:
	return {"completed":completed, "progress":progress, "assignments":assignments, "notifications":notifications}.duplicate(true)

func valid(data: Variant, player: String, saved_hour: int) -> bool:
	if not data is Dictionary: return false
	for field: String in ["completed", "progress", "assignments"]:
		if not data.get(field) is Dictionary or data[field].size() != world.countries.size(): return false
		for tag: String in world.countries:
			if not data[field].get(tag) is Dictionary: return false
	for tag: String in world.countries:
		var known: Dictionary = data["completed"][tag]
		for tech: Variant in known:
			if not tech is String or not catalog.has(tech) or known[tech] != true: return false
		for tech: String in starting.get(tag, []):
			if not known.has(tech): return false
		for tech: Variant in data["progress"][tag]:
			if not tech is String or not catalog.has(tech) or known.has(tech): return false
			var amount: Variant = data["progress"][tag][tech]
			if not (amount is float or amount is int) or not is_finite(float(amount)) or float(amount) < 0 or float(amount) >= float(catalog[tech]["days"]): return false
		var used := {}
		var institutions := Institutions.for_country(world, tag)
		for institution: Variant in data["assignments"][tag]:
			var tech: Variant = data["assignments"][tag][institution]
			if tag != player or institution not in institutions or not tech is String or not catalog.has(tech) or known.has(tech) or used.has(tech): return false
			used[tech] = true
			var t: Dictionary = catalog[tech]
			var parent_known: bool = t["parents"].is_empty()
			for parent: String in t["parents"]:
				if known.has(parent): parent_known = true
			if not parent_known: return false
			for dependency: String in t["dependencies"]:
				if not known.has(dependency): return false
			for other: String in t["exclusive"]:
				if known.has(other): return false
	if not data.get("notifications") is Array or data["notifications"].size() > catalog.size(): return false
	var notices := {}
	for entry: Variant in data["notifications"]:
		if not entry is Dictionary or entry.get("tag") != player or not entry.get("tech") is String: return false
		if not data["completed"][player].has(entry["tech"]) or notices.has(entry["tech"]): return false
		if entry.get("institution") not in Institutions.for_country(world, player): return false
		var hour: Variant = entry.get("hour")
		if not (hour is float or hour is int) or not is_finite(float(hour)) or float(hour) != floor(float(hour)) or float(hour) < 0 or float(hour) > saved_hour: return false
		notices[entry["tech"]] = true
	return true

func import_state(data: Dictionary) -> void:
	completed = data["completed"].duplicate(true)
	progress = data["progress"].duplicate(true)
	assignments = data["assignments"].duplicate(true)
	notifications = data["notifications"].duplicate(true)
	changed.emit()
