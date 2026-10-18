extends SceneTree
func _initialize() -> void:
 var db: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/world.json"))
 var ps: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/provinces.json"))
 var render=load("res://scripts/map_rendering.gd").new()
 var start:=Time.get_ticks_usec()
 render.initialize(ps,db["regions"],db["countries"])
 var bytes:=0
 for image: Image in render.region_images:bytes+=image.get_data().size()
 print("MAP_LOAD_BENCH ",JSON.stringify({"elapsed_ms":(Time.get_ticks_usec()-start)/1000.,"source_bytes":bytes,"textures":render.region_images.size(),"headless":true}))
 quit()
