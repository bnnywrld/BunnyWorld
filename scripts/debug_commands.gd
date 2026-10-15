extends RefCounted
static func execute(state: WorldState, line: String) -> String:
	var args := line.strip_edges().split(" ", false)
	if args.is_empty(): return ""
	var command := args[0].to_lower()
	if command == "help": return "tag TAG | set FIELD VALUE [TAG] | add FIELD VALUE [TAG]\nFields: pp, stability, war_support, population, gdp, gdp_per_capita\noutlook western/emerging/nonaligned/salafist/nationalist [TAG]\ncosmetic NAME/none [TAG] | color R G B [TAG] | owner STATE TAG\nopinion FROM TO VALUE (-1000 to 1000)\nPercentages use 0–100. GDP and GDP/capita use USD."
	if command == "tag":
		if args.size() != 2 or not state.countries.has(args[1].to_upper()): return "Unknown country. Example: tag jap"
		state.player_country = args[1].to_upper()
		state.selected_country = state.player_country
		state.selected_region = 0
		state.selected_province = 0
		return "Now playing " + state.countries[state.player_country]["name"]
	if command == "opinion":
		if args.size() != 4 or not args[3].is_valid_float() or not state.set_opinion(args[1].to_upper(), args[2].to_upper(), float(args[3])): return "Use opinion FROM TO VALUE (-1000 to 1000)."
		return "Directional opinion updated."
	if command == "color":
		if args.size() not in [4, 5]: return "Use color R G B [TAG] (0–255)."
		var target := args[4].to_upper() if args.size() == 5 else state.player_country
		if not state.countries.has(target): return "Unknown country."
		var rgb: Array = []
		for i: int in range(1, 4):
			if not args[i].is_valid_int() or int(args[i]) < 0 or int(args[i]) > 255: return "Color channels must be whole numbers from 0 to 255."
			rgb.append(int(args[i]))
		state.countries[target]["color_override"] = rgb
		return "Country color updated."
	if command == "owner":
		if args.size() != 3 or not args[1].is_valid_int() or not state.transfer_region(int(args[1]), args[2].to_upper()): return "Use owner STATE TAG with an existing state and country."
		return "State ownership changed."
	if command in ["outlook", "cosmetic"]:
		if args.size() < 2 or args.size() > 3: return "Use " + command + " VALUE [TAG]"
		var tag := args[2].to_upper() if args.size() == 3 else state.player_country
		if not state.countries.has(tag): return "Unknown country."
		if command == "outlook":
			var choices := {"western":"Western Outlook", "emerging":"Emerging Outlook", "nonaligned":"Non-Aligned Outlook", "salafist":"Salafist Outlook", "nationalist":"Nationalist Outlook"}
			if not choices.has(args[1].to_lower()): return "Unknown outlook. Use help."
			state.countries[tag]["outlook"] = choices[args[1].to_lower()]
		else:
			if args[1].length() > 80: return "Cosmetic name is too long."
			state.countries[tag]["cosmetic"] = "" if args[1].to_lower() == "none" else args[1]
			state.countries[tag]["color_override"] = []
		return "Country appearance updated."
	if command not in ["set", "add"] or args.size() < 3 or args.size() > 4: return "Unknown command. Type help."
	if not args[2].is_valid_float(): return "Value must be a finite number."
	var value := float(args[2])
	if not is_finite(value): return "Value must be finite."
	var tag := args[3].to_upper() if args.size() == 4 else state.player_country
	if not state.countries.has(tag): return "Unknown country."
	var field := args[1].to_lower()
	var stats: Dictionary = state.countries[tag].get("starting_stats", {}).duplicate(true)
	if field == "population":
		var metrics := state.country_metrics(tag)
		if command == "add": value += float(metrics["population"])
		if value < 0 or value > 10000000000 or value != floor(value) or metrics["regions"].is_empty(): return "Population must be a whole number between 0 and 10 billion for a territorial country."
		var remaining := int(value)
		var total := maxf(1, float(metrics["population"]))
		var regions: Array = metrics["regions"]
		for i: int in regions.size():
			var region: Dictionary = state.regions[str(regions[i])]
			var share := remaining if i == regions.size() - 1 else mini(remaining, int(value * float(region["population"]) / total))
			region["population"] = share
			remaining -= share
		return "Population updated."
	var key: String = {"pp":"political_power", "political_power":"political_power", "stability":"stability", "war_support":"war_support", "gdp_per_capita":"gdp_per_capita_usd", "gdp":"gdp_per_capita_usd"}.get(field, "")
	if key == "": return "Unknown field. Type help."
	if field == "gdp":
		var population := float(state.country_metrics(tag)["population"])
		if population <= 0: return "GDP requires population."
		value /= population
	if field in ["stability", "war_support"]: value /= 100.0
	if command == "add": value += float(stats.get(key, 0))
	if not is_finite(value) or value < 0 or value > 1000000000 or (field in ["stability", "war_support"] and value > 1): return "Value is outside the allowed range. Percentages use 0–100."
	stats[key] = value
	state.countries[tag]["starting_stats"] = stats
	return "Country value updated."
