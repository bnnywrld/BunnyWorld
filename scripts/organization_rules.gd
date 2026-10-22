extends RefCounted
# Organization data is separate from geography; this never edits map inputs.
const TYPES := {"regional":"Regional integration", "security":"Security alliance", "global":"Global institution", "forum":"Forum / club", "cultural":"Cultural community", "movement":"Movement", "commodity":"Commodity cartel", "treaty":"Treaty regime"}
const LEVELS := ["Consultation forum", "Free trade area", "Customs union", "Single market", "Monetary and political union", "Federation"]
const STATUSES := ["full", "associate", "observer", "partner", "suspended"]
static var catalog: Dictionary = {}

static func definitions() -> Dictionary:
	if catalog.is_empty():
		catalog = JSON.parse_string(FileAccess.get_file_as_string("res://data/organization_rules.json"))["organizations"]
	return catalog

static func seed(organizations: Dictionary) -> void:
	for oid: String in organizations:
		var org: Dictionary = organizations[oid]
		var rules: Dictionary = definitions().get(oid, {})
		for field: String in rules: org[field] = rules[field].duplicate(true) if rules[field] is Dictionary or rules[field] is Array else rules[field]
		org["statuses"] = {}
		for tag: String in org["members"]: org["statuses"][tag] = "full"

static func status(org: Dictionary, tag: String) -> String:
	return str(org.get("statuses", {}).get(tag, "full")) if tag in org.get("members", []) else ""

static func full_members(org: Dictionary) -> Array[String]:
	var result: Array[String] = []
	for tag: String in org.get("members", []):
		if status(org, tag) == "full": result.append(tag)
	return result

static func display_name(org: Dictionary, date: Dictionary) -> String:
	var date_key := "%04d-%02d-%02d" % [date["year"], date["month"], date["day"]]
	var result := str(org["name"])
	for entry: Dictionary in org.get("renames", []):
		if date_key >= str(entry["date"]): result = str(entry["name"])
	return result

static func headquarters(org: Dictionary, entries: Array) -> Dictionary:
	var hq: Variant = org.get("hq")
	if not hq is Dictionary: return {}
	var wanted: String = PlaceCatalog.key(str(hq["city"]))
	if wanted == "washington": wanted = PlaceCatalog.key("Washington,  D.C.")
	var fallback: Dictionary = {}
	for entry: Dictionary in entries:
		if entry["country"] != hq["country"]: continue
		if entry["kind"] == "Country": fallback = entry
		if entry["kind"] == "City" and PlaceCatalog.key(str(entry["name"])) == wanted:
			var result := entry.duplicate()
			result["location_exact"] = true
			return result
	if not fallback.is_empty():
		fallback = fallback.duplicate()
		fallback["location_exact"] = false
	return fallback

static func hq_label(org: Dictionary, countries: Dictionary) -> String:
	var hq: Variant = org.get("hq")
	if hq is Dictionary:
		return "%s, %s" % [hq["city"], countries.get(hq["country"], {}).get("name", hq["country"])]
	if org.get("rotating_chair", false):
		return "No fixed headquarters · rotating chair"
	return str(org.get("hq_note", "No fixed headquarters"))

static func features(org: Dictionary) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	match str(org.get("type", "")):
		"regional":
			result.append({"name":"Integration level", "text":LEVELS[int(org["integration_level"])] + " · scenario setting", "planned":false})
			result.append({"name":"Trade integration", "text":"Uses the highest level across full memberships; economic effects await the trade system.", "planned":true})
			result.append({"name":"Deepen / loosen integration", "text":"Requires Political Power, member agreement and opt-outs. Federation requires country merging.", "planned":true})
		"security":
			result.append({"name":"Exclusive faction", "text":"One full security-alliance membership per country; partners do not use the slot.", "planned":false})
			result.append({"name":"Collective defence", "text":"Guarantees, military access and joint command await military diplomacy.", "planned":true})
		"global":
			var text := "Resolutions, voting and access rules await institutional diplomacy."
			if org.get("id", "") in ["IMF", "IBRD"]: text = "Loans and conditions await the economy and debt systems."
			elif org.get("id", "") == "WTO": text = "Trade rules and market access await the trade system."
			result.append({"name":"Institutional powers", "text":text, "planned":true})
		"forum", "movement": result.append({"name":"Policy coordination", "text":"Invitations, prestige, Political Power and opinion effects await agreed balance values and diplomatic actions.", "planned":true})
		"cultural": result.append({"name":"Cultural cooperation", "text":"Opinion, approval and demographic effects await agreed balance values and approval simulation.", "planned":true})
		"commodity": result.append({"name":"Production coordination", "text":"Quotas, price influence and compliance await resource production and the economy.", "planned":true})
		"treaty": result.append({"name":"Treaty compliance", "text":"Signatures, ratification, withdrawal and violation penalties await treaty diplomacy.", "planned":true})
	result.append({"name":"Membership effects", "text":"Only full members qualify. PP, outlook affinity and headquarters benefits have no agreed values yet.", "planned":true})
	return result

static func valid_state(organizations: Dictionary, countries: Dictionary) -> bool:
	var factions: Dictionary = {}
	for oid: String in organizations:
		var org: Dictionary = organizations[oid]
		if not TYPES.has(org.get("type")): return false
		var definition: Dictionary = definitions().get(oid, {})
		for field: String in definition:
			if field in ["statuses", "integration_level", "opt_out_levels"]: continue
			if org.get(field) != definition[field]: return false
		if not org.get("statuses") is Dictionary or org["statuses"].size() != org["members"].size(): return false
		if not org.get("integration_level") is int and not org.get("integration_level") is float: return false
		var level := float(org["integration_level"])
		if not is_finite(level) or level != floor(level) or level < 0 or level > 5: return false
		if not org.get("opt_out_levels") is Dictionary: return false
		for tag: String in org["opt_out_levels"]:
			var opt: Variant = org["opt_out_levels"][tag]
			if tag not in org["members"] or not (opt is int or opt is float): return false
			if not is_finite(float(opt)) or float(opt) != floor(float(opt)) or float(opt) < 0 or float(opt) > level: return false
		for tag: String in org["members"]:
			if not countries.has(tag) or status(org, tag) not in STATUSES: return false
			if org.get("type") == "security" and status(org, tag) == "full":
				if factions.has(tag): return false
				factions[tag] = oid
	return true
