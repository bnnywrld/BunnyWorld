extends RefCounted
# Daily, player-only construction. No frame callbacks, workers or market simulation.
const MAX_FACTORIES := 10
var owner: WeakRef
var world: RefCounted:
	get: return owner.get_ref()
var catalog: Dictionary = {}
var coastal: Dictionary = {}
var queue: Array[Dictionary] = []
var next_id := 1
var revision := 0
var map_revision := 0
var reservation_revision := -1
var pending_counts: Dictionary = {}
var shared_counts: Dictionary = {}

func initialize(state: RefCounted) -> void:
	owner = weakref(state)
	var source: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/construction.json"))
	catalog = source["buildings"]
	for sid: int in source["coastal_states"]: coastal[str(sid)] = true

func reset() -> void:
	queue.clear()
	next_id = 1
	for sid: String in world.regions:
		var region: Dictionary = world.regions[sid]
		for key: String in ["infrastructure", "internet_station", "rail_terminal"]:
			if int(region["buildings"].get(key, 0)) > 10: region["buildings"][key] = 10
		var curve := capacity(float(region.get("area_km2", 0)), int(region["population"]))
		var used := shared_used(region["buildings"])
		region["construction_slots"] = maxi(curve, used + maxi(4, ceili(used * .25)))
		region["construction_gdp"] = 0.0
	_changed(true)

static func capacity(area: float, population: int) -> int:
	# Generous logarithmic curve: scarce room for tiny states, substantial room
	# for dense/large states. Existing buildings always receive extra headroom.
	return maxi(2, floori(2 + 5 * log(1 + maxf(area, 0) / 250.0) + 8 * log(1 + maxf(population, 0) / 50000.0)))

func shared_used(buildings: Dictionary) -> int:
	var result := 0
	for key: String in buildings:
		if catalog.get(key, {}).get("shared", false): result += int(buildings[key])
	return result

func _ensure_reservations() -> void:
	if reservation_revision == map_revision: return
	pending_counts.clear()
	shared_counts.clear()
	for job: Dictionary in queue:
		var sid := str(int(job["state"]))
		var key: String = job["building"]
		pending_counts[sid] = int(pending_counts.get(sid,0)) + 1
		pending_counts[sid+":"+key] = int(pending_counts.get(sid+":"+key,0)) + 1
		if catalog[key]["shared"]: shared_counts[sid] = int(shared_counts.get(sid,0)) + 1
	reservation_revision = map_revision

func pending(sid: String, key: String = "") -> int:
	_ensure_reservations()
	return int(pending_counts.get(sid if key.is_empty() else sid+":"+key,0))

func reserved_shared(sid: String) -> int:
	_ensure_reservations()
	return int(shared_counts.get(sid,0))

func free_slots(sid: String) -> int:
	var r: Dictionary = world.regions[sid]
	return maxi(0, int(r["construction_slots"]) - shared_used(r["buildings"]) - reserved_shared(sid))

func limit(sid: String, key: String) -> int:
	var seed: int = int(world.database["regions"][sid]["buildings"].get(key, 0))
	return 10 if key in ["infrastructure", "internet_station", "rail_terminal"] else maxi(seed, int(catalog[key]["max_level"]))

func blocked(sid: String, key: String) -> String:
	if not world.regions.has(sid) or not catalog.has(key): return "Choose a building and one of your states."
	var r: Dictionary = world.regions[sid]
	if r["owner"] != world.player_country: return "Construction is limited to your own states."
	if queue.size() >= 10000: return "Construction queue is full."
	if catalog[key]["coastal"] and not coastal.has(sid): return "Requires a coastal state."
	if int(r["buildings"].get(key, 0)) + pending(sid, key) >= limit(sid, key): return "Maximum building level already built or queued."
	if catalog[key]["shared"] and free_slots(sid) <= 0: return "No free shared building slots."
	if key in ["energy_infrastructure", "industrial_infrastructure"]:
		var other := "industrial_infrastructure" if key == "energy_infrastructure" else "energy_infrastructure"
		if int(r["buildings"].get(other, 0)) + pending(sid, other) > 0: return "This state already has the other electrical-grid specialization."
	return ""

func quote(sid: String, key: String) -> Dictionary:
	var level := int(world.regions[sid]["buildings"].get(key, 0)) + pending(sid, key)
	return {"cost":float(catalog[key]["money_usd"]), "points":float(catalog[key]["points"]) + float(catalog[key]["extra_points"]) * level}

func add(sid: String, key: String) -> bool:
	if not blocked(sid, key).is_empty(): return false
	var price := quote(sid, key)
	var stats: Dictionary = world.countries[world.player_country]["starting_stats"]
	var cash := minf(maxf(0, float(stats.get("treasury_usd", 0))), price["cost"])
	var borrowed: float = price["cost"] - cash
	stats["treasury_usd"] = maxf(0, float(stats.get("treasury_usd", 0))) - cash
	stats["debt_usd"] = maxf(0, float(stats.get("debt_usd", 0))) + borrowed
	queue.append({"id":next_id,"state":int(sid),"country":world.player_country,"building":key,"points":price["points"],"progress":0.0,"cash":cash,"borrowed":borrowed,"factories":MAX_FACTORIES})
	next_id += 1
	_changed(true)
	return true

func factory_count(tag: String) -> int:
	var total := 0
	for r: Dictionary in world.regions.values():
		if r["owner"] == tag: total += int(r["buildings"].get("industrial_complex", 0))
	return total

func allocations() -> Dictionary:
	var available := factory_count(world.player_country)
	var result: Dictionary = {}
	for job: Dictionary in queue:
		var sid := str(int(job["state"]))
		var count := 0
		if world.regions[sid]["owner"] == job["country"] and job["country"] == world.player_country:
			count = mini(available, int(job["factories"]))
			available -= count
		result[int(job["id"])] = count
	return result

func manufactured_factories() -> int:
	var assigned := 0
	for value: int in allocations().values(): assigned += value
	return factory_count(world.player_country) - assigned

func rate(job: Dictionary, factories: int) -> float:
	var level := int(world.regions[str(int(job["state"]))]["buildings"].get("infrastructure", 0))
	# Adapt MD's maximum infrastructure construction bonus (.75) to 10 levels.
	var bonus := 1.0 if job["building"] == "infrastructure" else 1 + .075 * level
	return factories * 4.0 * bonus

func gdp_gain(tag: String, key: String) -> float:
	var productivity := maxf(0, float(world.countries[tag].get("starting_variables", {}).get("overall_productivity", 650))) / 1000.0
	return float(catalog[key]["gdp_base_billion"]) * 1e9 * productivity

func advance_days(days: int) -> void:
	if queue.is_empty(): return
	for day: int in days:
		var assigned := allocations()
		var completed: Array[Dictionary] = []
		for job: Dictionary in queue:
			job["progress"] = minf(float(job["points"]), float(job["progress"]) + rate(job, assigned[int(job["id"])]))
			if job["progress"] >= job["points"]: completed.append(job)
		for job: Dictionary in completed:
			var r: Dictionary = world.regions[str(int(job["state"]))]
			var key: String = job["building"]
			r["buildings"][key] = int(r["buildings"].get(key, 0)) + 1
			r["construction_gdp"] += gdp_gain(job["country"], key)
			queue.erase(job)
		_changed(not completed.is_empty())
		if queue.is_empty(): break

func cancel(id: int) -> bool:
	for job: Dictionary in queue:
		if int(job["id"]) != id or job["country"] != world.player_country: continue
		var remainder := clampf(1 - float(job["progress"]) / float(job["points"]), 0, 1)
		var stats: Dictionary = world.countries[job["country"]]["starting_stats"]
		var borrowed: float = job["borrowed"] * remainder
		var repay := minf(float(stats.get("debt_usd", 0)), borrowed)
		stats["debt_usd"] = float(stats.get("debt_usd", 0)) - repay
		stats["treasury_usd"] = float(stats.get("treasury_usd", 0)) + job["cash"] * remainder + borrowed - repay
		queue.erase(job)
		_changed(true)
		return true
	return false

func move(id: int, direction: int) -> void:
	for i: int in queue.size():
		if int(queue[i]["id"]) != id: continue
		var target := clampi(i + clampi(direction, -1, 1), 0, queue.size()-1)
		var job: Dictionary = queue.pop_at(i)
		queue.insert(target, job)
		_changed(false)
		return

func set_factories(id: int, count: int) -> void:
	for job: Dictionary in queue:
		if int(job["id"]) == id:
			job["factories"] = clampi(count, 0, MAX_FACTORIES)
			_changed(false)
			return

func _changed(map: bool) -> void:
	revision += 1
	if map: map_revision += 1

func export_state() -> Dictionary:
	return {"queue":queue.duplicate(true),"next_id":next_id}

static func number(value: Variant, maximum: float = 1e18, integer: bool = false) -> bool:
	return (value is float or value is int) and is_finite(float(value)) and float(value) >= 0 and float(value) <= maximum and (not integer or float(value) == floor(float(value)))

func valid(saved: Variant, saved_regions: Dictionary, player: String) -> bool:
	if not saved is Dictionary or not saved.get("queue") is Array or saved["queue"].size() > 10000 or not number(saved.get("next_id"), 1e9, true): return false
	if int(saved["next_id"]) < 1: return false
	var ids := {}
	var shared := {}
	var levels := {}
	for sid: String in saved_regions:
		var r: Dictionary = saved_regions[sid]
		if not r.get("buildings") is Dictionary or not number(r.get("construction_slots"), 1e6, true) or not number(r.get("construction_gdp")): return false
		for key: Variant in r["buildings"]:
			if not key is String or not number(r["buildings"][key], 1e6, true): return false
			if not catalog.has(key) and not world.database["regions"][sid]["buildings"].has(key): return false
			if catalog.has(key) and float(r["buildings"][key]) > limit(sid, key): return false
		if shared_used(r["buildings"]) > int(r["construction_slots"]): return false
	for job: Variant in saved["queue"]:
		if not job is Dictionary: return false
		if not number(job.get("id"), float(saved["next_id"]) - 1, true) or float(job["id"]) < 1 or ids.has(job["id"]): return false
		if not number(job.get("state"), 8190, true) or not saved_regions.has(str(int(job["state"]))): return false
		var sid := str(int(job["state"]))
		var key: Variant = job.get("building")
		if not key is String or not catalog.has(key) or job.get("country") != player: return false
		for field: String in ["points", "progress", "cash", "borrowed"]:
			if not number(job.get(field)): return false
		if float(job["points"]) < float(catalog[key]["points"]) or float(job["points"]) > float(catalog[key]["points"])+float(catalog[key]["extra_points"])*maxi(0,limit(sid,key)-1) or float(job["progress"]) >= float(job["points"]) or not number(job.get("factories"), MAX_FACTORIES, true): return false
		if not is_equal_approx(float(job["cash"]) + float(job["borrowed"]), float(catalog[key]["money_usd"])): return false
		if catalog[key]["coastal"] and not coastal.has(sid): return false
		var level_key: String = sid + ":" + key
		levels[level_key] = int(levels.get(level_key, 0)) + 1
		if int(saved_regions[sid]["buildings"].get(key, 0)) + int(levels[level_key]) > limit(sid, key): return false
		if catalog[key]["shared"]: shared[sid] = int(shared.get(sid, 0)) + 1
		ids[job["id"]] = true
	for sid: String in shared:
		if shared_used(saved_regions[sid]["buildings"]) + int(shared[sid]) > int(saved_regions[sid]["construction_slots"]): return false
	return true

func import_state(saved: Dictionary) -> void:
	queue.assign(saved["queue"].duplicate(true))
	next_id = int(saved["next_id"])
	_changed(true)
