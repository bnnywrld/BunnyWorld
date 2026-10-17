extends RefCounted
# A draw policy only. WorldState.advance() and the main process loop never
# depend on this result. Heartbeat retains shader animation and catches new
# scene content; camera/selection/palette changes render immediately.
const IDLE_INTERVAL := 0.1
const SETTLE_SECONDS := 0.3
var force_continuous := false
var requested_frames := 0
var skipped_frames := 0
var revision := 0
var previous_key: Array = []
var elapsed := IDLE_INTERVAL
var settle := SETTLE_SECONDS

func invalidate() -> void:
	revision += 1

func request_frame(key: Array, delta: float) -> bool:
	elapsed += maxf(delta, 0.0)
	if key != previous_key:
		previous_key = key.duplicate()
		settle = SETTLE_SECONDS
	else:
		settle = maxf(0.0, settle - delta)
	var draw := force_continuous or settle > 0.0 or elapsed + .000001 >= IDLE_INTERVAL
	if draw:
		elapsed = 0.0
		requested_frames += 1
	else:
		skipped_frames += 1
	return draw
