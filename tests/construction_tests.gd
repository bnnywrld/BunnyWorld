extends SceneTree
const State = preload("res://scripts/world_state.gd")
const Build = preload("res://scripts/construction.gd")
var checks := 0
var failures := 0
func check(ok: bool, label: String) -> void:
	checks += 1
	if not ok:
		failures += 1
		push_error(label)
func _initialize() -> void:
	var db: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json"))
	var state := State.new()
	state.initialize(db)
	state.player_country = "GER"
	var model = state.construction
	var sid := str(int(state.countries["GER"]["capital"]))
	var region: Dictionary = state.regions[sid]
	check(model.catalog.size() == 22, "22 MD state building types")
	check(model.catalog["industrial_complex"]["points"] == 33150 and model.catalog["industrial_complex"]["money_usd"] == 7.5e9, "MD time and money costs are separate")
	check(Build.capacity(1, 100) < Build.capacity(500, 50000), "tiny states have less capacity")
	check(Build.capacity(500, 50000) < Build.capacity(100000, 5000000), "capacity grows with population/area")
	for id: String in state.regions:
		check(model.free_slots(id) >= 4, "starting buildings fit with headroom: " + id)
		check(state.regions[id]["buildings"] == db["regions"][id]["buildings"], "starting buildings preserved: " + id)
	var stats: Dictionary = state.countries["GER"]["starting_stats"]
	stats["treasury_usd"] = 1e9
	stats["debt_usd"] = 10e9
	var gdp: float = state.gdp("GER")
	check(model.add(sid, "industrial_complex"), "queue factory")
	check(stats["treasury_usd"] == 0 and stats["debt_usd"] == 16.5e9, "cash spent first and shortfall borrowed")
	check(state.gdp("GER") == gdp, "queueing does not add GDP")
	check(model.allocations().values()[0] == 10, "maximum 10 factories per project")
	check(model.manufactured_factories() == model.factory_count("GER")-10, "unassigned factories counted as goods production")
	var job: Dictionary = model.queue[0]
	var id := int(job["id"])
	var initial_free := model.free_slots(sid)
	model.advance_days(1)
	check(is_equal_approx(job["progress"], model.rate(job, 10)), "daily MD construction points with infrastructure factor")
	job["progress"] = float(job["points"])*.5
	check(model.cancel(id), "cancel partial job")
	check(stats["treasury_usd"] == .5e9 and stats["debt_usd"] == 13.25e9, "50 percent cash and borrowing refund")
	check(not model.cancel(id) and model.free_slots(sid) == initial_free+1, "cancellation is idempotent and frees reserved slot")
	check(state.gdp("GER") == gdp, "cancellation has no GDP gain")
	stats["treasury_usd"] = 100e9
	check(model.add(sid,"offices"), "queue fully cash funded")
	var debt: float = stats["debt_usd"]
	model.cancel(int(model.queue[0]["id"]))
	check(stats["treasury_usd"] == 100e9 and stats["debt_usd"] == debt, "cash-only cancellation does not repay unrelated debt")
	check(not model.add(str(int(state.countries["FRA"]["capital"])), "offices"), "foreign state rejected")
	region["construction_slots"] = model.shared_used(region["buildings"])
	check(not model.add(sid,"industrial_complex"), "full shared slots rejected")
	for key: String in ["infrastructure", "internet_station", "rail_terminal"]:
		region["buildings"][key] = 9
		check(model.add(sid,key), "network level bypasses shared slots: " + key)
		check(not model.add(sid,key), "queued level reserves 10th network level: " + key)
		check(model.free_slots(sid) == 0, "network does not occupy shared slot")
		model.cancel(int(model.queue[0]["id"]))
	region["construction_slots"] += 100
	for i: int in 6: model.add(sid, "industrial_complex")
	var allocated := 0
	for count: int in model.allocations().values():
		check(count <= 10, "project cap obeyed")
		allocated += count
	check(allocated <= model.factory_count("GER") and allocated+model.manufactured_factories() == model.factory_count("GER"), "no factory overcommitment")
	var last: Dictionary = model.queue.back()
	model.move(int(last["id"]),-1)
	check(int(model.queue[model.queue.size()-2]["id"]) == int(last["id"]), "queue priority changes order")
	model.set_factories(int(model.queue[0]["id"]),0)
	check(model.allocations()[int(model.queue[0]["id"])] == 0, "project can be paused")
	for entry: Dictionary in model.queue.duplicate(): model.cancel(int(entry["id"]))
	check(model.add(sid,"offices"), "new completion project")
	job = model.queue[0]
	job["progress"] = float(job["points"])-1
	var offices := int(region["buildings"].get("offices",0))
	var predicted: float = model.gdp_gain("GER","offices")
	state.paused = true
	state.advance(.25)
	check(model.queue.size() == 1, "paused clock does not advance projects")
	state.hour = 23
	state.accumulator = 1
	state.paused = false
	state.advance(0)
	check(model.queue.is_empty() and int(region["buildings"]["offices"]) == offices+1, "building completes at daily simulation tick")
	check(is_equal_approx(state.gdp("GER"),gdp+predicted), "completed building adds MD output exactly once")
	model.advance_days(4)
	check(is_equal_approx(state.gdp("GER"),gdp+predicted), "GDP is not repeatedly added")
	var view := {"rotation":[0,0],"distance":2.0,"map_mode":0,"organization":"EU","show_regions":false,"inspection_active":false,"relations_reverse":false}
	model.add(sid,"industrial_complex")
	job = model.queue[0]
	job["progress"] = 123
	var path := "user://tests/construction.json"
	check(state.save_game(path,view), "save partial construction")
	var saved_points := float(job["points"])
	model.cancel(int(job["id"]))
	region["buildings"]["offices"] = 0
	check(not state.load_game(path).is_empty(), "load new construction save")
	check(model.queue.size() == 1 and model.queue[0]["progress"] == 123 and model.queue[0]["points"] == saved_points, "partial progress survives reload")
	check(state.regions[sid]["buildings"]["offices"] == offices+1 and is_equal_approx(state.gdp("GER"),gdp+predicted), "completed buildings and GDP persist")
	var envelope: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(path))
	var payload: Dictionary = JSON.parse_string(envelope["payload"])
	payload["construction"]["queue"][0]["progress"] = -1
	var body := JSON.stringify(payload)
	var bad := "user://tests/construction_invalid.json"
	var file := FileAccess.open(bad,FileAccess.WRITE)
	file.store_string(JSON.stringify({"format":"BunnyWorldSave","payload":body,"checksum":body.sha256_text()}));file.close()
	check(state.load_game(bad).is_empty() and model.queue[0]["progress"] == 123, "invalid save rejected atomically")
	for file_path: String in [path,path+".bak",bad]: DirAccess.remove_absolute(file_path)
	print("CONSTRUCTION_MODEL checks=",checks," failures=",failures)
	quit(0 if failures==0 else 1)
