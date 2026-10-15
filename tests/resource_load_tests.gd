extends SceneTree
func _initialize() -> void:
	for path: String in ["assets/region_ids_0.png","assets/region_ids_1.png","assets/region_ids_2.png","assets/region_ids_3.png","assets/province_index.png","assets/relief_data.png","assets/terrain_types.png","assets/terrain_color.png","assets/land_boundaries.res","assets/sea_boundaries.res","assets/province_boundaries.res","assets/waterways.res"]:
		if load("res://"+path) == null:
			printerr("RESOURCE_LOAD_FAILED ",path);quit(1);return
	print("RESOURCE_LOAD_TESTS_PASS")
	quit()
