extends SceneTree
func _initialize() -> void:
 var w=load("res://scripts/world_state.gd").new()
 var db: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json"))
 assert(db["version"]=="0.2.0.28")
 w.initialize(db)
 var d=load("res://scripts/demography.gd").new()
 var result={"states":{},"countries":{}}
 for sid in w.regions:result["states"][sid]=d.state_metrics(w,int(sid))
 for tag in w.countries:result["countries"][tag]=d.country_metrics(w,tag)
 var f=FileAccess.open("res://tools/cartography/edits_0229/runtime_before.json",FileAccess.WRITE)
 f.store_string(JSON.stringify(result));f.close()
 print("BASELINE_0229_CAPTURED ",result["states"].size())
 quit()
