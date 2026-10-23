extends RefCounted
## Assign current employment; the monthly economy adjusts unemployment separately.
const Demographics = preload("res://scripts/demography.gd")
var owner: WeakRef
var world: RefCounted:
	get: return owner.get_ref()
var demographics := Demographics.new()
var states: Dictionary = {}
var national: Dictionary = {}
var revision := 0

func initialize(state: RefCounted) -> void:
	owner = weakref(state)

func refresh() -> void:
	states.clear()
	national.clear()
	var requirements: Dictionary = world.state_economy["workers_per_level"]
	for sid: String in world.regions:
		var region: Dictionary = world.regions[sid]
		var workforce: Dictionary = demographics.state_workforce(world, int(sid))
		var employed := int(workforce["employed"])
		var demand: Dictionary = {}
		var required := 0
		for key: String in requirements:
			var jobs := int(region["buildings"].get(key, 0)) * int(requirements[key])
			if jobs > 0: demand[key] = jobs; required += jobs
		var available := mini(employed, required)
		var assigned := Demographics.allocate(available, demand) if not demand.is_empty() else {}
		states[sid] = {"required":required, "assigned":available, "other_employment":employed - available, "employed":employed, "unemployed":workforce["unemployed"], "inactive":workforce["outside_labour_force"], "demand":demand, "workers":assigned}
		var tag := str(region["owner"])
		if not national.has(tag): national[tag] = {"demand":{}, "workers":{}}
		for key: String in demand:
			national[tag]["demand"][key] = int(national[tag]["demand"].get(key, 0)) + int(demand[key])
			national[tag]["workers"][key] = int(national[tag]["workers"].get(key, 0)) + int(assigned.get(key, 0))
	revision += 1

func fulfillment(sid: String, building: String) -> float:
	var entry: Dictionary = states.get(sid, {})
	var required := int(entry.get("demand", {}).get(building, 0))
	return float(entry.get("workers", {}).get(building, 0)) / required if required > 0 else 1.0

func national_fulfillment(tag: String, building: String) -> float:
	var entry: Dictionary = national.get(tag, {})
	var required := int(entry.get("demand", {}).get(building, 0))
	return float(entry.get("workers", {}).get(building, 0)) / required if required > 0 else 1.0

func gdp_output(sid: String) -> float:
	var total := 0.0
	for key: String in world.regions[sid].get("construction_output", {}):
		total += float(world.regions[sid]["construction_output"][key]) * fulfillment(sid, key)
	return total
