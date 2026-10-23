extends SceneTree
const State = preload("res://scripts/world_state.gd")
var checks := 0
var failures := 0
func check(ok: bool,message: String) -> void:
	checks+=1
	if not ok: failures+=1;push_error(message)
func _initialize() -> void: run.call_deferred()
func step(world: RefCounted,count: int=1) -> void:
	for i: int in count:
		var month: int = world.society.last_month+1
		world.hour=int((Time.get_unix_time_from_datetime_dict({"year":month/12,"month":month%12+1,"day":1,"hour":0,"minute":0,"second":0})-world.scenario_epoch)/3600)
		world.society.advance_months()
func conservation(world: RefCounted) -> void:
	var sold := 0.;var bought := 0.
	for n: Dictionary in world.economy.nations.values(): sold+=float(n["exports_value"]);bought+=float(n["imports_value"])
	check(is_equal_approx(sold,bought),"trade cash flow conserved")
	for key: String in world.economy.prices:
		var imports := 0.;var exports := 0.
		for tag: String in world.countries:
			var row: Dictionary=world.economy.ledger[tag][key]
			imports+=float(row["imports"]);exports+=float(row["exports"])
			check(float(row["exports"])+float(row["domestic"])<=float(row["produced"])+.001,"exports never exceed surplus")
			check(is_equal_approx(float(row["consumed"])+float(row["unmet"]),float(row["demand"])),"consumption plus unmet demand conserved")
		check(is_equal_approx(imports,exports),"international units conserved: "+key)
func run() -> void:
	var world := State.new()
	world.initialize(JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json")))
	var economy=world.economy
	check(economy.rules["goods"].size()==10 and economy.ledger.size()==224,"ten-good economy runs for every country")
	for tag: String in world.countries:
		var baseline: float=world.country_metrics(tag)["population"]*world.countries[tag]["starting_stats"].get("gdp_per_capita_usd",0)
		check(is_equal_approx(world.gdp(tag),baseline),"initial GDP preserved")
		check(economy.nations[tag]["electricity"]["active"]==false and economy.nations[tag]["electricity"]["generation"]==null,"electricity inactive")
		check(world.countries[tag]["starting_stats"].get("treasury_usd")==world.database["countries"][tag]["starting_stats"].get("treasury_usd"),"initial trade never credits export value to government")
	conservation(world)
	check(not economy.flows.is_empty(),"automatic trade supplies actual buyers")
	check(economy.ledger["EGY"]["food"]["produced"]<economy.ledger["EGY"]["food"]["demand"] and economy.ledger["USA"]["food"]["produced"]>economy.ledger["USA"]["food"]["demand"],"cropland potential does not treat desert area as farmland")
	var technology := "nanofibers_4"
	var university: String=preload("res://scripts/research_institutions.gd").for_country(world,"JAP")[0]
	check(world.research.start("JAP",university,technology),"research quality test starts")
	world.hour=24;world.research.advance_days(1)
	check(is_equal_approx(world.research.progress["JAP"][technology],economy.research_multiplier("JAP")),"daily research integrates the quality/funding multiplier")
	world.hour=0;world.research.reset()
	var n: Dictionary=economy.nations["JAP"]
	var quality: float=n["education_quality"]
	var health: float=n["healthcare_quality"]
	var speed: float=economy.research_multiplier("JAP")
	n["budget"]["research"]=5.
	check(economy.research_multiplier("JAP")>speed and economy.research_multiplier("JAP")<speed*1.2,"research funding improves speed with diminishing returns")
	n["budget"]["research"]=1.
	var growth: float=world.society.annual_growth_rate("JAP")
	check(economy.set_budget("JAP","education",0) and economy.set_budget("JAP","healthcare",0),"funding cuts scheduled")
	check(n["budget"]["education"]>0 and n["education_quality"]==quality,"pending budget has no instant effect")
	check(not economy.set_budget("USA","education",10) and not economy.set_budget("JAP","education",NAN) and not economy.set_budget("JAP","population_tax",99),"invalid/foreign settings rejected")
	var treasury: float=world.countries["JAP"]["starting_stats"]["treasury_usd"]
	var old_prices: Dictionary=economy.prices.duplicate()
	step(world)
	check(n["budget"]["education"]==0 and n["pending"].is_empty(),"budget applies next month")
	check(n["education_quality"]<quality and n["education_quality"]>=quality-.600001,"quality falls gradually")
	check(n["healthcare_quality"]<health and economy.research_multiplier("JAP")<speed and world.society.annual_growth_rate("JAP")<growth,"quality has live research/population effects")
	check(is_equal_approx(world.countries["JAP"]["starting_stats"]["treasury_usd"],treasury+float(n["balance"])),"treasury settles net public budget, not exports")
	for key: String in old_prices: check(absf(float(economy.prices[key])/float(old_prices[key])-1)<=.025001,"monthly price movement bounded")
	check(economy.set_budget("JAP","education",10) and economy.set_budget("JAP","healthcare",15),"higher funding scheduled")
	var lower_quality: float=n["education_quality"]
	step(world)
	check(n["education_quality"]>lower_quality and n["education_quality"]<=lower_quality+.600001,"higher funding raises quality gradually")
	world.reset();n=economy.nations["JAP"]
	var stats: Dictionary=world.countries["JAP"]["starting_stats"]
	stats["treasury_usd"]=0
	for key: String in economy.rules["budget"]: economy.set_budget("JAP",key,0)
	economy.set_budget("JAP","military",15)
	var debt: float=stats["debt_usd"]
	step(world)
	check(n["balance"]<0 and stats["treasury_usd"]==0 and is_equal_approx(stats["debt_usd"],debt-float(n["balance"])),"deficit borrows exactly the cash shortfall")
	check(n["interest"]>0 and n["interest_rate"]>=.025,"debt incurs interest")
	world.reset();n=economy.nations["JAP"];stats=world.countries["JAP"]["starting_stats"]
	var sid := ""
	for id: String in world.regions:
		if world.regions[id]["owner"]=="JAP" and world.construction.blocked(id,"offices").is_empty(): sid=id;break
	var cash: float=stats["treasury_usd"]
	var price: float=world.construction.catalog["offices"]["money_usd"]
	var gdp: float=world.gdp("JAP")
	check(world.construction.add(sid,"offices") and stats["treasury_usd"]==cash-price,"full construction price remains upfront")
	check(n["construction_paid"]==price,"upfront investment recorded")
	check(world.construction.manufactured_factories()<world.construction.factory_count("JAP") and world.gdp("JAP")==gdp,"construction allocation preserves existing GDP")
	cash=stats["treasury_usd"]
	step(world)
	check(is_equal_approx(stats["treasury_usd"],cash+float(n["balance"])) and n["construction_last_month"]==price,"monthly settlement never pays construction twice")
	world.construction.cancel(int(world.construction.queue[0]["id"]))
	var unemployment: float=world.regions[sid]["workforce"]["unemployment_rate"]
	var participation: float=world.regions[sid]["workforce"]["participation_rate"]
	world.regions[sid]["buildings"]["offices"]=int(world.regions[sid]["buildings"].get("offices",0))+1
	step(world)
	check(world.regions[sid]["workforce"]["unemployment_rate"]<unemployment,"new jobs gradually hire unemployed residents")
	check(world.regions[sid]["workforce"]["participation_rate"]==participation,"inactive residents not recruited automatically")
	var directory := OS.get_environment("TEMP").path_join("bunnyworld-economy-qa")
	var path := directory.path_join("economy-%d.bws" % OS.get_process_id())
	var view := {"rotation":[0,0],"distance":2.,"map_mode":0,"organization":"EU","show_regions":false,"inspection_active":false,"relations_reverse":false}
	economy.set_budget("JAP","education",9)
	check(world.save_game(path,view),"save economy")
	var envelope: Dictionary=JSON.parse_string(FileAccess.get_file_as_string(path))
	var payload: Dictionary=JSON.parse_string(envelope["payload"])
	var expected: Dictionary=economy.export_state()
	var saved_gdp: float=world.gdp("JAP")
	world.reset()
	check(not world.load_game(path).is_empty(),"load economy: "+world.last_error)
	check(is_equal_approx(saved_gdp,world.gdp("JAP")),"loading does not reprice GDP")
	check(economy.nations["JAP"]["pending"].get("education")==9 and is_equal_approx(economy.nations["JAP"]["education_quality"],expected["nations"]["JAP"]["education_quality"]),"pending budget, quality and monthly ledger persist")
	for corrupt: String in ["quality","price","flow","ledger","energy","month","budget","interest","missing_field"]:
		var bad:=payload.duplicate(true)
		match corrupt:
			"quality": bad["economy"]["nations"]["JAP"]["education_quality"]=101
			"price": bad["economy"]["prices"]["food"]=-1
			"flow": bad["economy"]["flows"][0]["value"]=-1
			"ledger": bad["economy"]["ledger"]["JAP"]["food"]["consumed"]+=100
			"energy": bad["economy"]["nations"]["JAP"]["electricity"]["active"]=true
			"month": bad["economy"]["last_month"]-=1
			"budget": bad["economy"]["nations"]["JAP"]["budget"]["research"]=100
			"interest": bad["economy"]["nations"]["JAP"]["interest_rate"]=-1
			"missing_field": bad["economy"]["nations"]["JAP"].erase("education_quality");bad["economy"]["nations"]["JAP"]["unknown_quality"]=50
		var body:=JSON.stringify(bad)
		var file:=FileAccess.open(path+".bad",FileAccess.WRITE);file.store_string(JSON.stringify({"format":"BunnyWorldSave","payload":body,"checksum":body.sha256_text()}));file.close()
		check(world.load_game(path+".bad").is_empty() and is_equal_approx(economy.nations["JAP"]["education_quality"],expected["nations"]["JAP"]["education_quality"]),"corruption rejected atomically: "+corrupt)
	step(world)
	var expected_prices: Dictionary=economy.prices.duplicate()
	var expected_flows: Array=economy.flows.duplicate(true)
	check(not world.load_game(path).is_empty(),"reload deterministic checkpoint")
	step(world)
	check(expected_prices==economy.prices and expected_flows==economy.flows,"save/resume produces identical market settlement")
	world.reset()
	for seed: Dictionary in economy.seeds.values(): seed["food"]=0
	step(world,12)
	check(economy.nations["JAP"]["food_stress"]>.5 and world.society.annual_growth_rate("JAP")<0 and world.society.nations["JAP"]["last_growth"]<0,"sustained severe food shortage can cause population decline")
	check(world.save_game(path,view) and not world.load_game(path).is_empty(),"negative growth and remainders save/load")
	world.reset();step(world,12)
	var sequential_prices: Dictionary=economy.prices.duplicate()
	var sequential_population: int=world.country_metrics("JAP")["population"]
	var sequential_quality: float=economy.nations["JAP"]["education_quality"]
	world.reset();world.hour=366*24;world.society.advance_months()
	check(economy.prices==sequential_prices and world.country_metrics("JAP")["population"]==sequential_population and economy.nations["JAP"]["education_quality"]==sequential_quality,"batched months match sequential settlement and growth")
	world.reset()
	var started:=Time.get_ticks_msec()
	step(world,120)
	conservation(world)
	for tag: String in world.countries:
		check(is_finite(world.gdp(tag)) and world.gdp(tag)>=0 and world.countries[tag]["starting_stats"]["debt_usd"]>=0,"decade simulation stays finite")
	check(world.save_game(path,view) and not world.load_game(path).is_empty(),"long-run economy remains loadable")
	print("ECONOMY_MODEL checks=",checks," failures=",failures," decade_ms=",Time.get_ticks_msec()-started," trades=",economy.flows.size())
	quit(0 if failures==0 else 1)
