extends RefCounted
## Monthly population ledger; polling and a separate dated parliament snapshot.
## Unimplemented systems have null values, never fabricated neutral scores.
const Religions = preload("res://scripts/religion_catalog.gd")
const Demographics = preload("res://scripts/demography.gd")
const Rules = preload("res://scripts/government_rules.gd")
const OUTLOOKS := ["Western Outlook", "Multipolar Outlook", "Non-Aligned Outlook", "Nationalist Outlook"]
const AFFILIATED := ["Cultural Religion", "State Religion", "Theocracy"]
var owner: WeakRef
var world: RefCounted:
	get: return owner.get_ref()
var definitions: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/parties_2000.json"))
var rules: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/society_rules.json"))
var remainders: Dictionary = {}
var nations: Dictionary = {}
var initial_affiliations: Dictionary = {}
var last_month := 0
var revision := 0

func initialize(state: RefCounted) -> void:
	owner = weakref(state)

static func normalize_outlook(value: String) -> String:
	if value == "Emerging Outlook": return "Multipolar Outlook"
	return value if value in OUTLOOKS else "Unspecified"

static func month_index(date: Dictionary) -> int:
	return int(date["year"]) * 12 + int(date["month"]) - 1

func reset() -> void:
	remainders.clear()
	nations.clear()
	initial_affiliations.clear()
	last_month = month_index(world.date_dictionary())
	for sid: String in world.regions: remainders[sid] = 0.0
	for tag: String in world.countries:
		world.countries[tag]["outlook"] = normalize_outlook(world.countries[tag]["outlook"])
		var polls: Dictionary = {}
		for party: Dictionary in parties(tag): polls[party["id"]] = float(party["support"])
		var faith := ""
		var ideas: Array = world.countries[tag].get("starting_ideas", [])
		# Only explicit, unambiguous source identities; never choose a majority faith.
		for idea: String in ["sunni", "shia", "orthodox_christian"]:
			if idea in ideas: faith = {"sunni":"Sunni", "shia":"Shia", "orthodox_christian":"Orthodox"}[idea]; break
		if world.government_property(tag, "religion") not in AFFILIATED: faith = ""
		initial_affiliations[tag] = faith
		nations[tag] = {"polls":polls, "seats":allocate_seats(polls), "seat_date":"2000-01-01", "affiliation":faith,
			"last_growth":0, "total_growth":0, "attitudes":{"social_liberalism":null, "secularism":null, "international_integration":null},
			"approval":null, "migration":{"attractiveness":null, "immigration":null, "emigration":null, "capacity":null}, "religious_funding":null}
	revision += 1

func parties(tag: String) -> Array:
	return definitions.get("countries", {}).get(tag, {}).get("parties", [])

func allocate_seats(polls: Dictionary) -> Dictionary:
	var eligible: Dictionary = {}
	for id: String in polls:
		if float(polls[id]) >= float(rules["seat_support_threshold"]): eligible[id] = polls[id]
	if eligible.is_empty(): return {}
	return Demographics.allocate(int(rules["parliament_seats"]), eligible)

func unrepresented(tag: String) -> float:
	var total := 0.0
	for value: Variant in nations[tag]["polls"].values(): total += float(value)
	return maxf(0, 100.0 - total)

func outlook_totals(tag: String) -> Dictionary:
	var result: Dictionary = {}
	for outlook: String in OUTLOOKS: result[outlook] = 0.0
	for party: Dictionary in parties(tag): result[party["outlook"]] += float(nations[tag]["polls"].get(party["id"], 0))
	return result

func seat_parties(tag: String) -> Array[Dictionary]:
	var result: Array[Dictionary] = []
	for party: Dictionary in parties(tag):
		var seats := int(nations[tag]["seats"].get(party["id"], 0))
		if seats <= 0: continue
		var row := party.duplicate()
		row["seats"] = seats
		row["support"] = nations[tag]["polls"][party["id"]]
		row["government_status"] = preload("res://scripts/government_roster.gd").status(world,tag,party["id"])
		result.append(row)
	return result

func annual_growth_rate(tag: String) -> float:
	var rate := float(rules["annual_population_growth"])
	for modifier: float in world.economy.growth_modifiers(tag).values(): rate += modifier
	return clampf(rate,-.08,.04)

func advance_months() -> void:
	var target := month_index(world.date_dictionary())
	while last_month < target:
		world.economy.advance_month(last_month+1)
		for tag: String in nations: nations[tag]["last_growth"] = 0
		for sid: String in world.regions:
			var region: Dictionary = world.regions[sid]
			var tag := str(region["owner"])
			var monthly := pow(1.0 + annual_growth_rate(tag), 1.0 / 12.0) - 1.0
			var exact := float(region["population"]) * monthly + float(remainders[sid])
			var gain := maxi(-int(region["population"]),int(floor(exact)))
			remainders[sid] = exact - gain
			region["population"] = int(region["population"]) + gain
			if nations.has(tag):
				nations[tag]["last_growth"] += gain
				nations[tag]["total_growth"] += gain
		last_month += 1
		world.construction.refresh_capacities()
		world.employment.refresh()
		world.economy.finish_population_month()
		revision += 1

func religion_cost(tag: String, policy: String, faith: String) -> float:
	var current: String = world.government_property(tag, "religion")
	if current == policy:
		return 0.0 if str(nations[tag]["affiliation"]).is_empty() else Rules.CHANGE_COST
	return Rules.change_cost("religion", current, policy)

func change_religion(tag: String, policy: String, faith: String) -> bool:
	return world.agenda.propose(tag, "religion", policy, faith)

func export_state() -> Dictionary:
	return {"last_month":last_month, "remainders":remainders.duplicate(), "nations":nations.duplicate(true)}

func valid(value: Variant, saved_hour: int, national: Dictionary) -> bool:
	if not value is Dictionary or value.size() != 3: return false
	var expected := month_index(Time.get_datetime_dict_from_unix_time(world.scenario_epoch + saved_hour * 3600))
	if value.get("last_month") != expected: return false
	var residuals: Variant = value.get("remainders")
	var saved: Variant = value.get("nations")
	if not residuals is Dictionary or residuals.size() != remainders.size() or not saved is Dictionary or saved.size() != nations.size(): return false
	for sid: String in remainders:
		if not _number(residuals.get(sid), 0, 1) or float(residuals[sid]) >= 1: return false
	for tag: String in nations:
		var item: Variant = saved.get(tag)
		if not item is Dictionary or item.size() != nations[tag].size(): return false
		var polls: Variant = item.get("polls")
		var seats: Variant = item.get("seats")
		if not polls is Dictionary or polls.size() != nations[tag]["polls"].size() or not seats is Dictionary: return false
		var support := 0.0
		for id: String in nations[tag]["polls"]:
			if not _number(polls.get(id), 0, 100): return false
			support += float(polls[id])
		if support > 100.00001: return false
		# No elections/poll changes are implemented yet. Keep this initial snapshot honest.
		if seats.size() != nations[tag]["seats"].size() or item.get("seat_date") != "2000-01-01": return false
		for id: String in nations[tag]["seats"]:
			if not _number(seats.get(id), 0, 100) or float(seats[id]) != float(nations[tag]["seats"][id]): return false
		for id: String in polls:
			if absf(float(polls[id]) - float(nations[tag]["polls"][id])) > .00001: return false
		for field: String in ["last_growth", "total_growth"]:
			if not _number(item.get(field), -1e15, 1e15) or floor(float(item[field])) != float(item[field]): return false
		for field: String in ["attitudes", "approval", "migration", "religious_funding"]:
			if not item.has(field) or item[field] != nations[tag][field]: return false
		var faith: Variant = item.get("affiliation")
		if not faith is String: return false
		var policy: String = national[tag]["government_properties"]["religion"]
		if policy in AFFILIATED:
			if faith not in Religions.affiliations() and not (faith == "" and initial_affiliations[tag] == "" and policy == world.government_starting_laws[tag]["religion"]): return false
		elif faith != "": return false
	return true

static func _number(value: Variant, low: float, high: float) -> bool:
	return (value is int or value is float) and is_finite(float(value)) and float(value) >= low and float(value) <= high

func import_state(value: Dictionary) -> void:
	last_month = int(value["last_month"])
	remainders = value["remainders"].duplicate()
	nations = value["nations"].duplicate(true)
	for tag: String in nations:
		for id: String in nations[tag]["seats"]: nations[tag]["seats"][id] = int(nations[tag]["seats"][id])
		for field: String in ["last_growth", "total_growth"]: nations[tag][field] = int(nations[tag][field])
	revision += 1

