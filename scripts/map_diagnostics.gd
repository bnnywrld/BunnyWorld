extends RefCounted
# Opt-in, bounded full-application timing capture. No frame cap, simulation
# speed or rendering setting is changed by collecting a report.
var samples: Array = []
var remaining := 0
var report: Dictionary = {}
var last_path := ""
var last_tick := 0

func adapter() -> Dictionary:
	return {"name":RenderingServer.get_video_adapter_name(), "vendor":RenderingServer.get_video_adapter_vendor(), "renderer":ProjectSettings.get_setting("rendering/renderer/rendering_method"), "release":OS.has_feature("release"), "os":OS.get_name()}

func start(frames: int = 600) -> String:
	samples.clear()
	remaining = clampi(frames, 120, 3600)
	last_tick = Time.get_ticks_usec()
	report = {"version":ProjectSettings.get_setting("application/config/version"), "adapter":adapter(), "frame_limit":Engine.max_fps, "scope":"Wall frame intervals for the full application, including frame pacing; not GPU timings. Idle map redraws are counted separately."}
	return "Recording %d frames. Close the console and use the map; a report will be saved automatically. No graphics or simulation settings change." % remaining

func capture(main: Control, draw: bool) -> String:
	if remaining <= 0: return ""
	var now := Time.get_ticks_usec()
	samples.append({"frame_ms":float(now-last_tick)/1000.0, "process_ms":Performance.get_monitor(Performance.TIME_PROCESS)*1000.0, "map_draw":draw, "map_mode":main.map_mode, "distance":main.distance, "paused":main.state.paused, "hour":main.state.hour, "viewport":[main.world_view.size.x,main.world_view.size.y], "graphics":main.graphics_setting})
	last_tick = now
	remaining -= 1
	if remaining == 0: return finish(main)
	return ""

func finish(main: Control) -> String:
	remaining = 0
	if samples.is_empty(): return "No timing samples recorded. Use perf start."
	var times: Array = []
	var draws := 0
	for sample: Dictionary in samples:
		times.append(sample["frame_ms"])
		if sample["map_draw"]: draws += 1
	times.sort()
	report["summary"] = {"frames":times.size(), "median_ms":times[int(times.size()/2)], "p95_ms":times[mini(times.size()-1,int(ceil(times.size()*.95))-1)], "map_draws":draws, "textures_bytes":Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED), "buffers_bytes":Performance.get_monitor(Performance.RENDER_BUFFER_MEM_USED), "ray_marches":main.pick_ray_marches, "pick_cache_hits":main.pick_cache_hits}
	report["samples"] = samples
	DirAccess.make_dir_recursive_absolute("user://performance")
	last_path = "user://performance/render_%d.json" % Time.get_unix_time_from_system()
	var file := FileAccess.open(last_path, FileAccess.WRITE)
	if file == null: return "Could not save the timing report."
	file.store_string(JSON.stringify(report,"\t"))
	return "Timing report saved: " + ProjectSettings.globalize_path(last_path)
