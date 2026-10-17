class_name Demography
extends RefCounted
var data: Dictionary = {}
var state_data: Dictionary = {}
func _init() -> void:
	data = JSON.parse_string(FileAccess.get_file_as_string("res://data/demographics.json"))
	state_data = JSON.parse_string(FileAccess.get_file_as_string("res://data/state_demographics.json"))

static func allocate(total: int, shares: Dictionary) -> Dictionary:
	var result: Dictionary = {}
	var weights := 0.0
	for value: Variant in shares.values(): weights += maxf(0, float(value))
	if weights <= 0: return {"Unknown": total}
	var used := 0
	var remainders: Array[Dictionary] = []
	for key: String in shares:
		var exact := float(total) * maxf(0, float(shares[key])) / weights
		var count := int(floor(exact))
		result[key] = count
		used += count
		remainders.append({"key": key, "fraction": exact - count})
	remainders.sort_custom(func(a: Dictionary, b: Dictionary): return str(a["key"]) < str(b["key"]) if is_equal_approx(a["fraction"], b["fraction"]) else float(a["fraction"]) > float(b["fraction"]))
	for i: int in total - used:
		var key: String = remainders[i % remainders.size()]["key"]
		result[key] = int(result[key]) + 1
	return result

func profile(tag: String) -> Dictionary:
	return data.get("profiles", {}).get(tag, {})

func state_metrics(world: WorldState, sid: int) -> Dictionary:
	var region: Dictionary = world.regions.get(str(sid), {})
	if region.is_empty(): return {}
	var tag := str(region.get("demographic_profile", region["owner"]))
	var p: Dictionary = state_data.get("states", {}).get(str(sid), profile(tag))
	var total := int(region["population"])
	var retirement := clampi(int(world.countries.get(str(region["owner"]), {}).get("starting_stats", {}).get("retirement_age", p.get("retirement_age", 65))),18,100)
	var metrics: Dictionary = {}
	var age_shares: Dictionary = {}
	var singles: Array = p.get("age_single_year", [])
	if singles.size() == 101:
		age_shares = {"Underage": 0.0, "Working age": 0.0, "Retired": 0.0}
		for age: int in singles.size():
			var key := "Underage" if age < 18 else ("Working age" if age < retirement else "Retired")
			age_shares[key] += float(singles[age])
	else: age_shares = {"Unknown": 1.0}
	var age_counts := allocate(total, age_shares)
	var adult25 := 0
	if p.get("adult25_share") != null: adult25 = int(round(total * float(p["adult25_share"])))
	for key: String in ["age", "religion", "education"]:
		var meta: Dictionary = p.get("metrics", {}).get(key, {"shares": {"Unknown": 1.0}, "source": "Unavailable", "year": 2000, "status": "unavailable"}).duplicate(true)
		var denominator := total
		var shares: Dictionary = meta["shares"]
		if key == "age": shares = age_shares
		if key == "education": denominator = adult25
		meta["shares"] = shares
		meta["counts"] = allocate(denominator, shares)
		meta["denominator"] = denominator
		metrics[key] = meta
	var rates: Dictionary = region.get("workforce", p.get("workforce", {}))
	var working_age := int(age_counts.get("Working age", 0))
	var labour_force := clampi(int(round(working_age * float(rates.get("participation_rate", .6)))),0,working_age)
	var unemployed := clampi(int(round(labour_force * float(rates.get("unemployment_rate", .08)))),0,labour_force)
	var workforce := {"working_age":working_age,"labour_force":labour_force,"employed":labour_force-unemployed,"unemployed":unemployed,"outside_labour_force":working_age-labour_force,"participation_rate":float(labour_force)/working_age if working_age>0 else 0.,"unemployment_rate":float(unemployed)/labour_force if labour_force>0 else 0.,"source":rates.get("source","Modeled 2000 workforce estimate"),"status":rates.get("status","estimated"),"retirement_age":retirement}
	return {"population": total, "metrics": metrics, "retirement_age": retirement, "scope": region["name"],"workforce":workforce}

func country_metrics(world: WorldState, tag: String) -> Dictionary:
	var result := {"population": 0, "metrics": {}, "scope": world.countries.get(tag, {}).get("name", tag), "retirement_age": 65, "urban": 0, "shared": 0,"workforce":{"working_age":0,"labour_force":0,"employed":0,"unemployed":0,"outside_labour_force":0}}
	for key: String in ["age", "religion", "education"]:
		result["metrics"][key] = {"counts": {}, "denominator": 0, "sources": [], "statuses": []}
	for sid: String in world.regions:
		if world.regions[sid]["owner"] != tag: continue
		var entry := state_metrics(world, int(sid))
		result["population"] += int(entry["population"])
		for field: String in ["working_age","labour_force","employed","unemployed","outside_labour_force"]: result["workforce"][field]+=int(entry["workforce"][field])
		for key: String in entry["metrics"]:
			var dest: Dictionary = result["metrics"][key]
			var source: Dictionary = entry["metrics"][key]
			dest["denominator"] += int(source["denominator"])
			for category: String in source["counts"]: dest["counts"][category] = int(dest["counts"].get(category, 0)) + int(source["counts"][category])
			var reference := "%s · %s" % [source.get("source", ""), str(int(source["year"])) if source.get("year") is float else str(source.get("year", ""))]
			if reference not in dest["sources"]: dest["sources"].append(reference)
			if source.get("status", "") not in dest["statuses"]: dest["statuses"].append(source.get("status", ""))
	result["retirement_age"] = int(world.countries[tag].get("starting_stats", {}).get("retirement_age", 65))
	var workforce: Dictionary=result["workforce"]
	workforce["participation_rate"]=float(workforce["labour_force"])/int(workforce["working_age"]) if int(workforce["working_age"])>0 else 0.
	workforce["unemployment_rate"]=float(workforce["unemployed"])/int(workforce["labour_force"]) if int(workforce["labour_force"])>0 else 0.
	workforce["source"]="Sum of currently owned states; participation weighted by working-age residents, unemployment by labour force."
	workforce["status"]="Modeled 2000 starting workforce; rates change separately from age shares."
	workforce["retirement_age"]=result["retirement_age"]
	return result
