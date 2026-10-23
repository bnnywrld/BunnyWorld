extends RefCounted
## Aggregate national economy. State locations feed production; no provincial markets.
const Demography = preload("res://scripts/demography.gd")
const Society = preload("res://scripts/society.gd")
const FLOW_FIELDS := ["produced","demand","domestic","imports","exports","consumed","unmet"]
const SECTORS := ["military","administration","security","education","healthcare","welfare","research"]
var owner: WeakRef
var world: RefCounted:
	get: return owner.get_ref()
var rules: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/economy_rules.json"))
var nations := {}
var seeds := {}
var prices := {}
var settlement_prices := {}
var flows: Array = []
var ledger := {}
var prices_history: Array = []
var partners := {}
var rankings := {}
var preference_signature := ""
var preference_hour := 0
var country_order: Array = []
var aggregate := {}
var last_month := 0
var processing_month := 0
var revision := 0
signal changed

func initialize(state: RefCounted) -> void: owner = weakref(state)
func reset() -> void:
	country_order=world.countries.keys();country_order.sort()
	nations.clear(); seeds.clear(); prices.clear(); flows.clear(); ledger.clear(); partners.clear();rankings.clear();preference_signature=""; prices_history.clear()
	last_month = Society.month_index(world.date_dictionary())
	processing_month=last_month
	for key: String in rules["goods"]: prices[key] = float(rules["goods"][key]["base_price_usd"])
	for sid: String in world.regions:
		var region: Dictionary = world.regions[sid]
		var workers: Dictionary = world.employment.states[sid]
		seeds[sid] = {"population":int(region["population"]),"employed":int(workers["employed"]),"required":int(workers["required"])}
	for tag: String in country_order:
		var pc := float(world.countries[tag]["starting_stats"].get("gdp_per_capita_usd",0))
		var quality := clampf(25+12*log(maxf(1,pc/300)),20,85)
		var education := quality
		var health := quality
		for idea: String in world.countries[tag].get("starting_ideas",[]):
			if idea.begins_with("edu_") and idea.trim_prefix("edu_").is_valid_int(): education = clampf(25+10*int(idea.trim_prefix("edu_")),20,90)
			if idea.begins_with("health_") and idea.trim_prefix("health_").is_valid_int(): health = clampf(25+10*int(idea.trim_prefix("health_")),20,90)
		var budget: Dictionary = rules["budget"].duplicate(true)
		budget["education"] = maintenance("education",education)
		budget["healthcare"] = maintenance("healthcare",health)
		var cap := tax_cap(tag)
		for key: String in ["population_tax","corporate_tax"]: budget[key] = minf(cap,budget[key])
		nations[tag] = {"budget":budget,"pending":{},"education_quality":education,"healthcare_quality":health,"education_trend":0.,"healthcare_trend":0.,"productivity":1.,"real_factor":1.,"price_index":1.,"inflation":.02,"input_factor":1.,"food_stress":0.,"shortage_months":0,"employment_ratio":1.,"revenue":0.,"spending":0.,"interest":0.,"interest_rate":.03,"balance":0.,"real_growth":0.,"last_real_gdp":0.,"exports_value":0.,"imports_value":0.,"construction_paid":0.,"construction_last_month":0.,"electricity":rules["electricity"].duplicate(true),"computing":rules["computing"].duplicate(true)}
	_refresh_aggregate()
	for tag: String in country_order: nations[tag]["last_real_gdp"]=raw_real_gdp(tag)
	_calibrate()
	_refresh_aggregate()
	_market(false)
	for tag: String in country_order: _budget(tag,false)
	_touch()

func _refresh_aggregate(update_ratios: bool = true) -> void:
	aggregate.clear()
	for tag: String in country_order: aggregate[tag] = {"population":0,"area":0.,"cropland":0.,"buildings":{},"capacity":{},"employed":0,"baseline_employed":0.,"manufacturing":0.,"food_baseline":0.,"farm_baseline":0.,"added_output":0.}
	var assigned: Dictionary = world.construction.allocations()
	var construction_by_state := {}
	for job: Dictionary in world.construction.queue:
		var sid := str(int(job["state"]))
		construction_by_state[sid] = int(construction_by_state.get(sid,0))+int(assigned.get(int(job["id"]),0))
	for sid: String in world.regions:
		var region: Dictionary = world.regions[sid]
		var tag: String = region["owner"]
		var entry: Dictionary = aggregate[tag]
		var original_workers := float(seeds[sid]["employed"])
		var labor_factor := minf(1,float(world.employment.states[sid]["employed"])/original_workers) if original_workers>0 else 1.
		entry["population"] += int(region["population"])
		entry["area"] += float(region["area_km2"])
		entry["cropland"] += float(rules["agricultural_potential"][sid]["cropland_km2"])
		entry["added_output"] += world.employment.gdp_output(sid)
		entry["food_baseline"] += float(seeds[sid].get("food",0))*labor_factor
		entry["farm_baseline"] += float(seeds[sid].get("farms",0))
		entry["employed"] += int(world.employment.states[sid]["employed"])
		entry["baseline_employed"] += float(seeds[sid]["employed"])*int(region["population"])/maxf(1,seeds[sid]["population"])
		for key: String in region.get("resources",{}): entry["capacity"][key] = float(entry["capacity"].get(key,0))+float(region["resources"][key])*labor_factor
		for key: String in region["buildings"]:
			var staffed: float = float(region["buildings"][key])*world.employment.fulfillment(sid,key)
			entry["buildings"][key] = float(entry["buildings"].get(key,0))+staffed
			if key == "industrial_complex": entry["manufacturing"] += maxf(0,int(region["buildings"][key])-int(construction_by_state.get(sid,0)))*world.employment.fulfillment(sid,key)
	for tag: String in country_order:
		if update_ratios: nations[tag]["employment_ratio"] = clampf(float(aggregate[tag]["employed"])/maxf(1,aggregate[tag]["baseline_employed"]),.05,2.) if aggregate[tag]["baseline_employed"] > 0 else 1.

var output_scales := {}
var farm_baselines := {}
func _calibrate() -> void:
	output_scales.clear(); farm_baselines.clear()
	var demand := {}
	var resources := {}
	var factories := {"manufactured_goods":0.,"microchips":0.,"composites":0.}
	var food_total := 0.
	var population := 0.
	for key: String in rules["goods"]: demand[key] = 0.; resources[key] = 0.
	for tag: String in country_order:
		var a: Dictionary = aggregate[tag]
		var gdp := raw_real_gdp(tag)
		for key: String in demand:
			demand[key] += float(a["population"]) if key == "food" else gdp/12*float(rules["goods"][key]["gdp_demand_share"])/prices[key]
			resources[key] += float(a["capacity"].get(key,0))
		var productivity := source_productivity(tag)
		for pair: Array in [["manufactured_goods","industrial_complex"],["microchips","microchip_plant"],["composites","composite_plant"]]: factories[pair[0]] += float(a["buildings"].get(pair[1],0))*productivity
		var potential := clampf(sqrt((float(a["cropland"])+float(a["buildings"].get("agriculture_district",0))*500)*1000/maxf(1,a["population"])/2.3),0,2.5)
		farm_baselines[tag] = float(a["population"])*potential
		food_total += farm_baselines[tag]
		population += float(a["population"])
	for tag: String in farm_baselines: farm_baselines[tag] *= population*float(rules["initial_supply_margin"])/maxf(1,food_total)
	for sid: String in seeds:
		var region: Dictionary = world.regions[sid]
		var a: Dictionary = aggregate[region["owner"]]
		var weight: float = float(rules["agricultural_potential"][sid]["cropland_km2"])+int(region["buildings"].get("agriculture_district",0))*world.employment.fulfillment(sid,"agriculture_district")*500
		var total_weight := float(a["cropland"])+float(a["buildings"].get("agriculture_district",0))*500
		seeds[sid]["food"] = float(farm_baselines[region["owner"]])*(weight/maxf(1,total_weight) if total_weight>0 else int(region["population"])/maxf(1,a["population"]))
		seeds[sid]["farms"] = int(region["buildings"].get("agriculture_district",0))*world.employment.fulfillment(sid,"agriculture_district")
	for key: String in demand:
		if factories.has(key): output_scales[key] = float(demand[key])*float(rules["initial_supply_margin"])/maxf(1,factories[key])
		elif key == "food": output_scales[key] = population*.15/maxf(1,_building_total("agriculture_district"))
		else: output_scales[key] = float(demand[key])*float(rules["initial_supply_margin"])/maxf(1,resources[key])

func _building_total(key: String) -> float:
	var total := 0.
	for a: Dictionary in aggregate.values(): total += float(a["buildings"].get(key,0))
	return total
func source_productivity(tag: String) -> float: return maxf(.1,float(world.countries[tag].get("starting_variables",{}).get("overall_productivity",650))/1000.)
func raw_real_gdp(tag: String) -> float:
	return float(aggregate.get(tag,{}).get("population",0))*float(world.countries[tag]["starting_stats"].get("gdp_per_capita_usd",0))
func real_gdp(tag: String, baseline: float) -> float:
	if not nations.has(tag): return baseline
	var n: Dictionary = nations[tag]
	return baseline*float(n["real_factor"])*float(n["employment_ratio"])*float(n["input_factor"])
func nominal_gdp(tag: String, baseline: float) -> float: return real_gdp(tag,baseline)*float(nations.get(tag,{}).get("price_index",1.))
func maintenance(kind: String, quality: float) -> float:
	var range: Array = rules[kind+"_maintenance"]
	return float(range[0])+float(range[1])*quality/100
func tax_cap(tag: String, laws: Dictionary = {}) -> float:
	var value := str(laws.get("taxation",world.government_property(tag,"taxation")))
	return {"Low Taxes":20.,"Moderate Taxes":35.,"High Taxes":60.}.get(value,35.)
func set_budget(tag: String, key: String, value: float) -> bool:
	if tag != world.player_country or not nations.has(tag) or not rules["budget_limits"].has(key) or not is_finite(value) or value < 0 or value > float(rules["budget_limits"][key]): return false
	if key.ends_with("_tax") and value > tax_cap(tag): return false
	nations[tag]["pending"][key] = value
	_touch()
	return true
func research_multiplier(tag: String) -> float:
	if not nations.has(tag): return 1.
	return (.5+float(nations[tag]["education_quality"])/100)*(.9+.1*sqrt(float(nations[tag]["budget"]["research"])))
func growth_modifiers(tag: String) -> Dictionary:
	if not nations.has(tag): return {"Healthcare quality":0.,"Sustained food shortage":0.}
	return {"Healthcare quality":(float(nations[tag]["healthcare_quality"])-50)*float(rules["health_growth_per_quality_point"]),"Sustained food shortage":-float(nations[tag]["food_stress"])*float(rules["food_growth_penalty"])}

func advance_month(month: int) -> void:
	if month <= last_month: return
	assert(month == last_month+1)
	processing_month=month
	for tag: String in country_order:
		var n: Dictionary = nations[tag]
		for key: String in n["pending"]: n["budget"][key] = n["pending"][key]
		n["pending"].clear()
		for key: String in ["population_tax","corporate_tax"]: n["budget"][key] = minf(tax_cap(tag),n["budget"][key])
		for kind: String in ["education","healthcare"]:
			var bounds: Array = rules[kind+"_maintenance"]
			var target := clampf((float(n["budget"][kind])-float(bounds[0]))/float(bounds[1])*100,0,100)
			var delta := clampf((target-float(n[kind+"_quality"]))*float(rules["quality_adjustment"]),-float(rules["quality_monthly_limit"]),float(rules["quality_monthly_limit"]))
			n[kind+"_quality"] = clampf(float(n[kind+"_quality"])+delta,0,100)
			n[kind+"_trend"] = delta
		var productivity_growth := float(rules["base_productivity_growth"])+float(rules["education_productivity_growth"])*float(n["education_quality"])/100
		n["productivity"] = minf(1000,float(n["productivity"])*pow(1+productivity_growth,1./12))
		n["real_factor"] = n["productivity"]
	_update_employment()
	_refresh_aggregate()
	_market(true)
	for tag: String in country_order:
		var n: Dictionary = nations[tag]
		var shortage := 1.-fulfillment(tag,"food")
		n["food_stress"] = lerpf(float(n["food_stress"]),shortage,float(rules["food_stress_adjustment"]))
		n["shortage_months"] = int(n["shortage_months"])+1 if shortage > .03 else 0
		var inputs := 0.
		for key: String in rules["goods"]:
			if key not in ["food","manufactured_goods"]: inputs += fulfillment(tag,key)/8
		n["input_factor"] = lerpf(float(n["input_factor"]),.8+.2*inputs,.1)
		# CPI is distinct from real productivity and global commodity prices.
		var pressure := .02 + shortage*.08 + maxf(0,float(n["interest_rate"])-.06)*.1
		n["inflation"] = clampf(lerpf(float(n["inflation"]),pressure,.1),-.03,.25)
		n["price_index"] = clampf(float(n["price_index"])*pow(1+float(n["inflation"]),1./12),.1,1000)
		_budget(tag,true)
		n["construction_last_month"] = n["construction_paid"]
		n["construction_paid"] = 0.
	last_month = month
	prices_history.append({"month":month,"prices":prices.duplicate()})
	if prices_history.size()>120: prices_history.pop_front()
func finish_population_month() -> void:
	_refresh_aggregate(false)
	for tag: String in country_order:
		var n: Dictionary=nations[tag]
		var actual := real_gdp(tag,raw_real_gdp(tag)+float(aggregate[tag]["added_output"]))
		n["real_growth"] = actual/float(n["last_real_gdp"])-1 if float(n["last_real_gdp"])>0 else 0.
		n["last_real_gdp"]=actual
	world.research.changed.emit();_touch()
func productivity_growth_for(tag: String) -> float: return float(rules["base_productivity_growth"])+float(rules["education_productivity_growth"])*float(nations[tag]["education_quality"])/100

func _update_employment() -> void:
	for sid: String in world.regions:
		var r: Dictionary = world.regions[sid]
		var seed: Dictionary = seeds[sid]
		var workforce: Dictionary = world.employment.states[sid]
		var labor := int(workforce["employed"])+int(workforce["unemployed"])
		if labor <= 0: continue
		var demand := 0.
		for key: String in world.state_economy["workers_per_level"]: demand += int(r["buildings"].get(key,0))*int(world.state_economy["workers_per_level"][key])
		var n: Dictionary = nations[r["owner"]]
		var baseline := float(seed["employed"])*int(r["population"])/maxf(1,seed["population"])
		var business_activity := (.95+.05*float(n["input_factor"]))*pow(float(n["productivity"]),.25)
		var desired := clampf(baseline*business_activity+demand-float(seed["required"]),0,labor*(1-float(rules["frictional_unemployment"])))
		var actual := lerpf(float(workforce["employed"]),desired,float(rules["employment_adjustment"]))
		r["workforce"]["unemployment_rate"] = clampf(1.-actual/labor,0,1)
	world.employment.refresh()

func _market(update_prices: bool) -> void:
	var previous_ledger := ledger
	ledger = {}; flows.clear()
	var signature := str(world.relation_offsets.hash())+":"+str(processing_month/6)
	for tag: String in country_order: signature+=str(world.countries[tag]["outlook"])
	if signature != preference_signature:
		partners.clear();rankings.clear();preference_signature=signature
		var review_month := processing_month-processing_month%6
		preference_hour = int((Time.get_unix_time_from_datetime_dict({"year":review_month/12,"month":review_month%12+1,"day":1,"hour":0,"minute":0,"second":0})-world.scenario_epoch)/3600)
	settlement_prices = prices.duplicate()
	var balances := {}
	var global_supply := {}
	var global_demand := {}
	for key: String in rules["goods"]: global_supply[key]=0.; global_demand[key]=0.
	for tag: String in country_order:
		var a: Dictionary = aggregate[tag]
		var n: Dictionary = nations[tag]
		var nominal := nominal_gdp(tag,raw_real_gdp(tag)+float(a["added_output"]))
		ledger[tag] = {}
		balances[tag] = nominal/12*float(rules["private_import_budget_gdp_share"])
		n["exports_value"] = 0.; n["imports_value"] = 0.
		for key: String in rules["goods"]:
			var produced := float(a["capacity"].get(key,0))*float(output_scales.get(key,0))*float(n["productivity"])
			if key == "manufactured_goods": produced = float(a["manufacturing"])*source_productivity(tag)*float(output_scales[key])*float(n["productivity"])
			elif key in ["microchips","composites"]:
				produced = float(a["buildings"].get("microchip_plant" if key=="microchips" else "composite_plant",0))*source_productivity(tag)*float(output_scales[key])*float(n["productivity"])
			elif key == "food":
				produced = maxf(0,float(a["food_baseline"])+(float(a["buildings"].get("agriculture_district",0))-float(a["farm_baseline"]))*float(output_scales[key]))*float(n["productivity"])
			var producer: String = {"manufactured_goods":"industrial_complex","food":"agriculture_district","microchips":"microchip_plant","composites":"composite_plant"}.get(key,"")
			if not producer.is_empty() and previous_ledger.has(tag):
				var input_quality := 1.
				for input: String in rules["buildings"][producer]["inputs"]:
					var previous: Dictionary = previous_ledger[tag][input]
					if float(previous["demand"]) > 0: input_quality = minf(input_quality,float(previous["consumed"])/float(previous["demand"]))
				produced *= .5+.5*input_quality
			if key == "oil": produced += float(a["buildings"].get("synthetic_refinery",0))*float(output_scales[key])*float(rules["buildings"]["synthetic_refinery"]["output_capacity"])
			var demand := float(a["population"]) if key == "food" else nominal/12*float(rules["goods"][key]["gdp_demand_share"])/float(prices[key])
			var row := {}
			for field: String in FLOW_FIELDS: row[field] = 0.
			row["produced"] = maxf(0,produced)
			row["demand"] = maxf(0,demand)
			row["domestic"] = minf(row["produced"],row["demand"])
			row["consumed"] = row["domestic"]
			row["unmet"] = maxf(0,row["demand"]-row["domestic"])
			ledger[tag][key] = row
			global_supply[key] += row["produced"]
			global_demand[key] += row["demand"]
	# Essential food first. Buyers receive a proportionate affordable share of scarcity.
	var order: Array = rules["goods"].keys()
	order.erase("food");order.push_front("food")
	for key: String in order:
		var sellers: Array = []
		var eligible := {}
		var wants := {}
		var supply := 0.
		var requested := 0.
		for tag: String in country_order:
			var row: Dictionary = ledger[tag][key]
			var surplus := float(row["produced"])-float(row["domestic"])
			if surplus > .000001: sellers.append(tag); eligible[tag]=true; supply += surplus
			var affordable := minf(float(row["unmet"]),float(balances[tag])/float(prices[key]))
			if affordable > .000001: wants[tag]=affordable; requested += affordable
		var share := minf(1,supply/maxf(.000001,requested))
		for buyer: String in wants:
			var needed := float(wants[buyer])*share
			var ranked: Array = ranked_partners(buyer)
			for seller: String in ranked:
				if needed <= .000001: break
				if not eligible.has(seller): continue
				if not trade_access(buyer,seller,key): continue
				var source: Dictionary = ledger[seller][key]
				var amount := minf(needed,maxf(0,float(source["produced"])-float(source["domestic"])-float(source["exports"])))
				if amount <= .000001: continue
				var cost := amount*float(prices[key])
				source["exports"] += amount
				ledger[buyer][key]["imports"] += amount
				ledger[buyer][key]["consumed"] += amount
				ledger[buyer][key]["unmet"] = maxf(0,float(ledger[buyer][key]["unmet"])-amount)
				nations[seller]["exports_value"] += cost
				nations[buyer]["imports_value"] += cost
				balances[buyer] = maxf(0,float(balances[buyer])-cost)
				needed -= amount
				flows.append({"seller":seller,"buyer":buyer,"good":key,"quantity":amount,"value":cost})
		if update_prices:
			var ratio := float(global_demand[key])/maxf(.000001,global_supply[key])
			var change := clampf((ratio-1)*float(rules["price_response"]),-float(rules["price_monthly_limit"]),float(rules["price_monthly_limit"]))
			prices[key] = clampf(float(prices[key])*(1+change),float(rules["goods"][key]["base_price_usd"])*float(rules["price_minimum_factor"]),float(rules["goods"][key]["base_price_usd"])*float(rules["price_maximum_factor"]))

func preference(buyer: String,seller: String) -> float:
	var key := buyer+":"+seller
	if partners.has(key): return partners[key]
	var a: Dictionary = world.countries[buyer]
	var b: Dictionary = world.countries[seller]
	var score: float = world.opinion(buyer,seller,preference_hour)*.1 + (10. if a["outlook"]==b["outlook"] else 0.)
	var ac: Array = a["map_center"]
	var bc: Array = b["map_center"]
	var distance := Vector2(float(ac[0]),float(ac[1])).distance_to(Vector2(float(bc[0]),float(bc[1])))
	score += maxf(0,15-distance*.1)
	partners[key] = score
	return score
func ranked_partners(buyer: String) -> Array:
	if rankings.has(buyer): return rankings[buyer]
	var scores := {}
	for seller: String in country_order:
		if seller != buyer: scores[seller]=preference(buyer,seller)
	var ranked: Array = scores.keys()
	ranked.sort_custom(func(a: String,b: String): return scores[a]>scores[b] if scores[a]!=scores[b] else a<b)
	rankings[buyer]=ranked
	return ranked
func trade_access(buyer: String,seller: String,_good: String) -> bool:
	# Agreements, sanctions and transport can attach here; none are invented now.
	return buyer != seller
func fulfillment(tag: String,key: String) -> float:
	var row: Dictionary = ledger.get(tag,{}).get(key,{})
	return clampf(float(row.get("consumed",0))/maxf(.000001,row.get("demand",0)),0,1) if float(row.get("demand",0))>0 else 1.
func _budget(tag: String, settle: bool) -> void:
	var n: Dictionary = nations[tag]
	var stats: Dictionary = world.countries[tag]["starting_stats"]
	var annual := nominal_gdp(tag,raw_real_gdp(tag)+float(aggregate[tag]["added_output"]))
	var debt := maxf(0,float(stats.get("debt_usd",0)))
	var ratio := debt/maxf(1,annual)
	n["interest_rate"] = clampf(.025+maxf(0,ratio-.6)*.025+maxf(0,-float(n["balance"]))*12/maxf(1,annual)*.02,.025,.25)
	n["interest"] = debt*float(n["interest_rate"])/12
	n["revenue"] = annual/12*(.62*float(n["budget"]["population_tax"])+.38*float(n["budget"]["corporate_tax"]))/100
	var spending := float(n["interest"])
	for key: String in SECTORS: spending += annual/12*float(n["budget"][key])/100
	n["spending"] = spending
	n["balance"] = float(n["revenue"])-spending
	if settle:
		var treasury := maxf(0,float(stats.get("treasury_usd",0)))+float(n["balance"])
		if treasury < 0: debt -= treasury; treasury = 0
		stats["treasury_usd"] = treasury
		stats["debt_usd"] = debt
func repay_debt(tag: String, amount: float) -> bool:
	if tag != world.player_country or not is_finite(amount) or amount <= 0: return false
	var stats: Dictionary = world.countries[tag]["starting_stats"]
	var payment := minf(amount,minf(float(stats.get("treasury_usd",0)),float(stats.get("debt_usd",0))))
	if payment <= 0: return false
	stats["treasury_usd"] -= payment;stats["debt_usd"] -= payment
	_budget(tag,false);_touch()
	return true
func record_construction(tag: String, amount: float) -> void:
	if nations.has(tag): nations[tag]["construction_paid"] += amount
func _touch() -> void:
	revision += 1
	changed.emit()
func export_state() -> Dictionary:
	return {"last_month":last_month,"nations":nations.duplicate(true),"prices":prices.duplicate(),"settlement_prices":settlement_prices.duplicate(),"flows":flows.duplicate(true),"ledger":ledger.duplicate(true),"history":prices_history.duplicate(true)}
func import_state(saved: Dictionary) -> void:
	last_month = int(saved["last_month"])
	processing_month=last_month
	nations = saved["nations"].duplicate(true);prices=saved["prices"].duplicate();flows=saved["flows"].duplicate(true);ledger=saved["ledger"].duplicate(true);prices_history=saved["history"].duplicate(true)
	settlement_prices = saved["settlement_prices"].duplicate()
	partners.clear();rankings.clear();preference_signature="";_refresh_aggregate(false);_touch()
static func number(value: Variant, low: float = 0, high: float = 1e16) -> bool:
	return (value is float or value is int) and is_finite(float(value)) and float(value)>=low and float(value)<=high
static func same_amount(a: float,b: float) -> bool: return absf(a-b)<=maxf(.00001,maxf(absf(a),absf(b))*1e-11)
func valid(saved: Variant,saved_hour: int) -> bool:
	if not saved is Dictionary or saved.size()!=7: return false
	var month := Society.month_index(Time.get_datetime_dict_from_unix_time(world.scenario_epoch+saved_hour*3600))
	if saved.get("last_month") != month: return false
	for field: String in ["nations","prices","settlement_prices","ledger"]:
		if not saved.get(field) is Dictionary: return false
	if saved["nations"].size()!=nations.size() or saved["prices"].size()!=prices.size() or saved["settlement_prices"].size()!=prices.size() or saved["ledger"].size()!=nations.size(): return false
	for tag: String in country_order:
		var n: Variant = saved["nations"].get(tag)
		if not n is Dictionary or n.size()!=nations[tag].size(): return false
		for field: String in nations[tag]:
			if not n.has(field): return false
		for field: String in ["budget","pending"]:
			if not n.get(field) is Dictionary or (field=="budget" and n[field].size()!=rules["budget"].size()): return false
			for key: Variant in n[field]:
				if not key is String or not rules["budget_limits"].has(key) or not number(n[field][key],0,rules["budget_limits"][key]): return false
		for key: String in n:
			if key in ["budget","pending"]: continue
			if key in ["electricity","computing"]:
				if n[key] != rules[key]: return false
			elif not number(n[key],-1e16,1e16): return false
		for key: String in ["education_quality","healthcare_quality"]:
			if not number(n[key],0,100): return false
		for key: String in ["education_trend","healthcare_trend"]:
			if not number(n[key],-float(rules["quality_monthly_limit"]),float(rules["quality_monthly_limit"])): return false
		for key: String in ["food_stress","input_factor"]:
			if not number(n[key],0,1): return false
		for key: String in ["productivity","real_factor","price_index"]:
			if not number(n[key],.05,1000): return false
		for key: String in ["revenue","spending","interest","exports_value","imports_value"]:
			if not number(n[key]): return false
		if not number(n["last_real_gdp"]): return false
		if not number(n["interest_rate"],.025,.25) or not number(n["inflation"],-.03,.25) or not number(n["employment_ratio"],.05,2.): return false
		if not number(n["shortage_months"],0,100000) or floor(float(n["shortage_months"]))!=float(n["shortage_months"]): return false
		if not saved["ledger"].get(tag) is Dictionary or saved["ledger"][tag].size()!=prices.size(): return false
		for good: String in prices:
			var row: Variant = saved["ledger"][tag].get(good)
			if not row is Dictionary or row.size()!=FLOW_FIELDS.size(): return false
			for field: String in FLOW_FIELDS:
				if not number(row.get(field)): return false
			if not same_amount(float(row["domestic"])+float(row["imports"]),float(row["consumed"])) or not same_amount(float(row["consumed"])+float(row["unmet"]),float(row["demand"])): return false
			if float(row["exports"])+float(row["domestic"])>float(row["produced"])+.001: return false
	for key: String in prices:
		var base := float(rules["goods"][key]["base_price_usd"])
		if not number(saved["prices"].get(key),base*float(rules["price_minimum_factor"]),base*float(rules["price_maximum_factor"])): return false
		if not number(saved["settlement_prices"].get(key),base*float(rules["price_minimum_factor"]),base*float(rules["price_maximum_factor"])): return false
	if not saved.get("flows") is Array or saved["flows"].size()>100000 or not saved.get("history") is Array or saved["history"].size()>120: return false
	var exported := {};var imported := {}
	for item: Variant in saved["flows"]:
		if not item is Dictionary or item.size()!=5 or not nations.has(item.get("seller")) or not nations.has(item.get("buyer")) or item["seller"]==item["buyer"] or not prices.has(item.get("good")) or not number(item.get("quantity")) or not number(item.get("value")): return false
		if not same_amount(float(item["quantity"])*float(saved["settlement_prices"][item["good"]]),float(item["value"])): return false
		var sold: String=item["seller"]+":"+item["good"];var bought: String=item["buyer"]+":"+item["good"]
		exported[sold]=float(exported.get(sold,0))+float(item["quantity"]);imported[bought]=float(imported.get(bought,0))+float(item["quantity"])
	for tag: String in country_order:
		for key: String in prices:
			if not same_amount(float(exported.get(tag+":"+key,0)),float(saved["ledger"][tag][key]["exports"])) or not same_amount(float(imported.get(tag+":"+key,0)),float(saved["ledger"][tag][key]["imports"])): return false
	var previous_month := -1
	for sample: Variant in saved["history"]:
		if not sample is Dictionary or sample.size()!=2 or not number(sample.get("month"),0,month) or sample["month"]<=previous_month or not sample.get("prices") is Dictionary or sample["prices"].size()!=prices.size(): return false
		previous_month=int(sample["month"])
		for key: String in prices:
			if not number(sample["prices"].get(key),float(rules["goods"][key]["base_price_usd"])*float(rules["price_minimum_factor"]),float(rules["goods"][key]["base_price_usd"])*float(rules["price_maximum_factor"])): return false
	return true
