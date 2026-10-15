class_name PlaceCatalog
extends RefCounted

var entries: Array[Dictionary] = []

static func key(value: String) -> String:
	var result := value.to_lower().strip_edges()
	var accents := {"a":"àáâãäåāăą", "c":"çćč", "d":"ďđ", "e":"èéêëēėęě", "i":"ìíîïīı", "l":"ł", "n":"ñńň", "o":"òóôõöøōő", "r":"ř", "s":"śšş", "t":"ťţ", "u":"ùúûüūůű", "y":"ýÿ", "z":"źżž"}
	for replacement: String in accents:
		for character: String in str(accents[replacement]): result = result.replace(character, replacement)
	return result

func _append(record: Dictionary, country_name: String, aliases: String = "") -> void:
	record["search_key"] = key(str(record["name"]) + " " + country_name + " " + aliases)
	record["name_key"] = key(str(record["name"]))
	record["country_name"] = country_name
	entries.append(record)

func initialize(world: RefCounted, cities: Array, scenery: Dictionary) -> void:
	entries.clear()
	for tag: String in world.countries:
		var country: Dictionary = world.countries[tag]
		_append({"kind":"Country","name":country["name"],"country":tag,"uv":Vector2(float(country["map_center"][0]),float(country["map_center"][1])),"state":0,"province":0},str(country["name"]),tag)
	for sid: String in world.regions:
		var region: Dictionary = world.regions[sid]
		_append({"kind":"State","name":region["name"],"country":region["owner"],"uv":Vector2(float(region["map_center"][0]),float(region["map_center"][1])),"state":int(sid),"province":0},str(world.countries.get(region["owner"],{}).get("name",""))," ".join(PackedStringArray(region.get("geographic_divisions",[])))+" "+str(region.get("protected_territory_name","")))
	var clusters_by_province: Dictionary = {}
	var group_focus: Dictionary = {}
	for cluster: Dictionary in scenery.get("clusters",[]):
		var pid := int(cluster["province"])
		if not clusters_by_province.has(pid): clusters_by_province[pid] = []
		clusters_by_province[pid].append(cluster)
	for city: Dictionary in cities:
		var pid := int(city.get("province_id",0))
		if not world.provinces.has(str(pid)): continue
		var uv := Vector2((float(city["longitude"])+180.0)/360.0,(90.0-float(city["latitude"]))/180.0)
		# Prepared scenery anchors already snap coastal settlements onto their
		# own province; use the closest one to avoid focusing offshore.
		var best := INF
		var focus := uv
		for cluster: Dictionary in clusters_by_province.get(pid,[]):
			var candidate := Vector2((float(cluster["longitude"])+180.0)/360.0,(90.0-float(cluster["latitude"]))/180.0)
			var delta := Vector2(wrapf(candidate.x-uv.x,-.5,.5),candidate.y-uv.y)
			if delta.length_squared() < best: best = delta.length_squared(); focus = candidate
		var sid := int(world.provinces[str(pid)]["region"])
		var owner: String = world.regions[str(sid)]["owner"]
		var group_id := str(city.get("urban_group",""))
		if not group_focus.has(group_id): group_focus[group_id] = {"uv":focus,"province":pid,"state":sid}
		_append({"kind":"City","name":city["name"],"country":owner,"uv":focus,"state":sid,"province":pid},str(world.countries.get(owner,{}).get("name","")),"Erbil" if city["name"]=="Irbil" else "")
	for group: Dictionary in world.urban_database.get("groups",{}).values():
		if group["provinces"].is_empty(): continue
		var pid := int(group["provinces"][0])
		var province: Dictionary = world.provinces[str(pid)]
		var point: Array = province["map_center"]
		var focus_record: Dictionary = group_focus.get(group["id"],{"uv":Vector2(float(point[0]),float(point[1])),"state":int(province["region"]),"province":pid})
		_append({"kind":"Metropolitan area","name":group["name"],"country":group["country_at_start"],"uv":focus_record["uv"],"state":focus_record["state"],"province":focus_record["province"]},str(world.countries.get(group["country_at_start"],{}).get("name","")))
	for monument: Dictionary in scenery.get("landmarks",[]):
		var pid := int(monument["province"])
		_append({"kind":"Landmark","name":monument["name"],"country":monument["country"],"uv":Vector2((float(monument["longitude"])+180.0)/360.0,(90.0-float(monument["latitude"]))/180.0),"state":int(world.provinces[str(pid)]["region"]),"province":pid},str(world.countries.get(monument["country"],{}).get("name","")))

func find_places(query: String, limit: int = 80) -> Array[Dictionary]:
	var needle := key(query)
	var found: Array[Dictionary] = []
	if needle.is_empty(): return found
	var words := needle.split(" ",false)
	for entry: Dictionary in entries:
		var matches := true
		for word: String in words:
			if word not in str(entry["search_key"]): matches = false; break
		if not matches: continue
		var score := 0 if entry["name_key"]==needle else (10 if str(entry["name_key"]).begins_with(needle) else 20)
		if entry["kind"] in ["City","Landmark"]: score -= 2
		var record := entry.duplicate()
		record["score"] = score
		found.append(record)
	found.sort_custom(func(a: Dictionary,b: Dictionary): return a["score"]<b["score"] if a["score"]!=b["score"] else str(a["name"]).naturalnocasecmp_to(str(b["name"]))<0)
	if found.size()>limit: found.resize(limit)
	return found
