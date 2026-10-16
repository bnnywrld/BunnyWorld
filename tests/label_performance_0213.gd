extends SceneTree
func _initialize() -> void:run.call_deferred()
func summary(values: Array) -> Dictionary:
	values.sort()
	return {"median_us":values[values.size()/2],"p95_us":values[int(values.size()*.95)],"maximum_us":values[-1]}
func run() -> void:
	var main=load("res://main.tscn").instantiate();root.add_child(main)
	while not main.boot_complete:await process_frame
	main._start_selection();main._show_country("GER",false);main._begin_campaign();main._close_panels();main._focus_country("GER",false)
	if main.focus_tween!=null:main.focus_tween.kill()
	main.country_labels_enabled=true;main.distance=2.0;main._update_camera_pose();main.set_process(false)
	var labels=main.country_label_layer
	var builds: int=labels.geometry_builds
	var reads: int=labels.preparation_reads
	var uploads: int=main.display_coverage.upload_count
	var result: Dictionary={"measurement":"CPU label updates with names enabled; not game FPS"}
	for forced: bool in [false,true]:
		var values: Array=[]
		for i: int in 220:
			main.planet.rotation.y+=.004
			var start:=Time.get_ticks_usec();labels.update_view(forced)
			values.append(Time.get_ticks_usec()-start)
			if i%20==0:await process_frame
		result["forced_visibility" if forced else "cached"]=summary(values)
	result["no_geometry_rebuild"]=builds==labels.geometry_builds
	result["no_geography_reads"]=reads==labels.preparation_reads
	result["no_coverage_uploads"]=uploads==main.display_coverage.upload_count
	print("LABEL_CPU_0213 ",JSON.stringify(result))
	var folder:=OS.get_environment("BUNNY_VALIDATION_DIR")
	if not folder.is_empty():
		var f:=FileAccess.open(folder.path_join("label_performance.json"),FileAccess.WRITE);f.store_string(JSON.stringify(result,"\t"))
	main.queue_free();await process_frame
	quit(0 if result["no_geometry_rebuild"] and result["no_geography_reads"] and result["no_coverage_uploads"] else 1)
