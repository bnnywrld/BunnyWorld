extends SceneTree
func _initialize() -> void:
	var policy = preload("res://scripts/map_frame_policy.gd").new()
	for i: int in 60: policy.request_frame([0], 1.0/60.0)
	var before: int = policy.requested_frames
	for i: int in 600: policy.request_frame([0], 1.0/60.0)
	var idle: int = policy.requested_frames-before
	assert(idle == 100, "Expected exactly 100 idle requests in 600 frames at 60 Hz")
	var changed: bool = policy.request_frame([1], 0.0)
	assert(changed, "A changed view must render immediately")
	before = policy.requested_frames
	for i: int in 60: policy.request_frame([i+2], 1.0/60.0)
	assert(policy.requested_frames-before == 60, "Every moving frame must render")
	var result := {"application_frames":600,"idle_map_draw_requests":idle,"moving_draws_per_60_frames":60,"change_wakes_immediately":changed,"simulation_gated":false}
	var file := FileAccess.open("res://validation_0222/frame_policy.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(result,"\t"))
	print("FRAME_POLICY_PASS ",JSON.stringify(result))
	quit()
