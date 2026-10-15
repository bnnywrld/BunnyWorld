extends SceneTree
const State = preload("res://scripts/world_state.gd")
const Places = preload("res://scripts/place_catalog.gd")
var failures := 0
func check(value: bool, label: String) -> void:
	if not value: failures+=1; printerr("FAIL: ",label)
func _initialize() -> void:
	var state := State.new()
	state.initialize(JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json")))
	var cities: Array = JSON.parse_string(FileAccess.get_file_as_string("res://data/cities.json"))
	var scenery: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/urban_scenery.json"))
	var catalog := Places.new()
	catalog.initialize(state,cities,scenery)
	check(catalog.find_places("").is_empty(),"empty query")
	check(catalog.find_places("zzzzunknown").is_empty(),"no match")
	check(catalog.find_places("Tokyo").any(func(r: Dictionary):return r["kind"]=="City" and r["name"]=="Tokyo"),"city search")
	check(catalog.find_places("Kanto").any(func(r: Dictionary):return r["kind"]=="State"),"state search")
	check(catalog.find_places("JAP").any(func(r: Dictionary):return r["kind"]=="Country" and r["country"]=="JAP"),"country tag search")
	check(catalog.find_places("Eiffel")[0]["kind"]=="Landmark","landmark search")
	check(catalog.find_places("Osaka").any(func(r: Dictionary):return r["name"]=="Ōsaka"),"accent normalization")
	check(catalog.find_places("Erbil").any(func(r: Dictionary):return r["name"]=="Irbil"),"city alias")
	check(catalog.find_places("Tokyo Japan").any(func(r: Dictionary):return r["name"]=="Tokyo"),"country qualifier")
	check(catalog.find_places("a",7).size()<=7,"bounded results")
	check(catalog.find_places("Greater Tokyo").any(func(r: Dictionary):return r["kind"]=="Metropolitan area"),"metropolitan grouping")
	for record: Dictionary in catalog.entries:
		check(record["uv"].x>=0 and record["uv"].x<=1 and record["uv"].y>=0 and record["uv"].y<=1,"valid focus coordinate")
		if record["kind"]=="City":check(state.provinces.has(str(int(record["province"]))),"city province link")
	if failures==0:print("PLACE_CATALOG_TESTS_PASS: cities, states, countries/tags, landmarks, accents, qualifiers, aliases, bounded results, valid coordinates")
	quit(0 if failures==0 else 1)
