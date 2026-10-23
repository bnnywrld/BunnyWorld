extends RefCounted
## One sequential reform agenda. PP is paid once, when a proposal is accepted.
const Rules = preload("res://scripts/government_rules.gd")
var owner: WeakRef
var world: RefCounted:
	get: return owner.get_ref()
var queue: Array = []
var revision := 0
signal changed

func initialize(state: RefCounted) -> void: owner = weakref(state)
func reset() -> void:
	queue.clear()
	_touch()
func pending(key: String) -> bool:
	for item: Dictionary in queue:
		if item["key"] == key: return true
	return false
func duration(key: String, current: String, target: String) -> int:
	return 30 * maxi(1, Rules.steps(key, current, target)) ** 2
func propose(tag: String, key: String, value: String, faith: String = "") -> bool:
	if tag != world.player_country or not world.countries.has(tag) or not Rules.valid_choice(key, value) or pending(key): return false
	var current: String = world.government_property(tag, key)
	var cost := Rules.change_cost(key, current, value)
	if key == "religion":
		if value in world.society.AFFILIATED:
			if faith not in preload("res://scripts/religion_catalog.gd").affiliations(): return false
		else: faith = ""
		if current == value and world.society.nations[tag]["affiliation"] == faith: return false
		cost = world.society.religion_cost(tag, value, faith)
	elif current == value: return false
	if world.political_power(tag) < cost: return false
	world.countries[tag]["starting_stats"]["political_power"] = world.political_power(tag) - cost
	queue.append({"country":tag, "key":key, "from":current, "value":value, "faith":faith, "days":duration(key,current,value), "elapsed":0, "cost":cost})
	_touch()
	return true
func advance_days(days: int) -> void:
	if queue.is_empty(): return
	for day: int in days:
		if queue.is_empty(): break
		var item: Dictionary = queue[0]
		item["elapsed"] += 1
		if item["elapsed"] < item["days"]: continue
		world.government_properties[item["country"]][item["key"]] = item["value"]
		if item["key"] == "religion":
			world.society.nations[item["country"]]["affiliation"] = item["faith"]
		world.society.revision += 1
		queue.pop_front()
		world.completion_notice.emit("Agenda completed", title(item) + "\n" + str(item["value"]))
	_touch()
func title(item: Dictionary) -> String:
	for property: Dictionary in Rules.PROPERTIES:
		if property["key"] == item["key"]: return property["title"]
	return item["key"]
func _touch() -> void:
	revision += 1
	changed.emit()
func export_state() -> Array: return queue.duplicate(true)
func import_state(saved: Array) -> void:
	queue = saved.duplicate(true)
	_touch()
func valid(saved: Variant, player: String, national: Dictionary, societies: Dictionary) -> bool:
	if not saved is Array or saved.size() > Rules.PROPERTIES.size(): return false
	var keys := {}
	for index: int in saved.size():
		var item: Variant = saved[index]
		if not item is Dictionary or item.size() != 8: return false
		for field: String in ["country","key","from","value","faith"]:
			if not item.get(field) is String: return false
		var key: String = item["key"]
		if item["country"] != player or keys.has(key) or not Rules.valid_choice(key,item["value"]): return false
		if item["from"] != national[player]["government_properties"].get(key): return false
		if not item.get("days") is float and not item.get("days") is int: return false
		if item["days"] != duration(key,item["from"],item["value"]): return false
		if not (item.get("elapsed") is float or item.get("elapsed") is int): return false
		var elapsed := float(item["elapsed"])
		if not is_finite(elapsed) or elapsed < 0 or elapsed >= item["days"] or elapsed != floor(elapsed) or (index > 0 and elapsed != 0): return false
		var cost := Rules.change_cost(key,item["from"],item["value"])
		if key == "religion":
			if item["value"] in world.society.AFFILIATED:
				if item["faith"] not in preload("res://scripts/religion_catalog.gd").affiliations(): return false
			elif item["faith"] != "": return false
			if item["from"] == item["value"]:
				var faith: String = societies[player]["affiliation"]
				if faith == item["faith"]: return false
				cost = 0.0 if faith.is_empty() else Rules.CHANGE_COST
		elif item["from"] == item["value"] or item["faith"] != "": return false
		if not (item.get("cost") is float or item.get("cost") is int) or item["cost"] != cost: return false
		keys[key] = true
	return true
