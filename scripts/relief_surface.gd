class_name ReliefSurface
extends RefCounted
const WIDTH := 8192
const HEIGHT := 4096
const SCALE := 0.016
const MAX_RADIUS := 1.016
var bytes: PackedByteArray

func _init() -> void:
	bytes = FileAccess.get_file_as_bytes("res://assets/relief_data.bin")

func _value(x: int, y: int) -> float:
	var i := (clampi(y, 0, HEIGHT - 1) * WIDTH + posmod(x, WIDTH)) * 2
	return float(int(bytes[i]) + int(bytes[i + 1]) * 256) * SCALE / 65535.0

func height_at(uv: Vector2) -> float:
	var x := fposmod(uv.x, 1.0) * WIDTH - 0.5
	var y := clampf(uv.y * HEIGHT - 0.5, 0.0, HEIGHT - 1.0)
	var ix := int(floor(x)); var iy := int(floor(y))
	return lerpf(lerpf(_value(ix, iy), _value(ix + 1, iy), x - ix), lerpf(_value(ix, iy + 1), _value(ix + 1, iy + 1), x - ix), y - iy)

static func uv_of(point: Vector3) -> Vector2:
	var n := point.normalized()
	return Vector2(fposmod(atan2(n.x, n.z) / TAU + .5, 1.0), acos(clampf(n.y, -1.0, 1.0)) / PI)

static func unit_point(uv: Vector2) -> Vector3:
	var lon := (uv.x - .5) * TAU; var lat := (.5 - uv.y) * PI
	return Vector3(cos(lat) * sin(lon), sin(lat), cos(lat) * cos(lon))

func point_at(uv: Vector2) -> Vector3:
	return unit_point(uv) * (1.0 + height_at(uv))

func ray_point(origin: Vector3, direction: Vector3) -> Vector3:
	var b := origin.dot(direction)
	var disc := b * b - (origin.length_squared() - MAX_RADIUS * MAX_RADIUS)
	if disc < 0: return Vector3.ZERO
	var t := maxf(0.0, -b - sqrt(disc))
	var closest := maxf(t, -b)
	var previous := t
	for i: int in 96:
		var p := origin + direction * t
		var error := p.length() - 1.0 - height_at(uv_of(p))
		if absf(error) < 0.0000005: return p
		if error < 0:
			var lo := previous; var hi := t
			for j: int in 20:
				var mid := (lo + hi) * .5; var q := origin + direction * mid
				if q.length() - 1.0 - height_at(uv_of(q)) > 0: lo = mid
				else: hi = mid
			return origin + direction * ((lo + hi) * .5)
		previous = t
		t += maxf(error * .48, .0000002)
		if t > closest: return Vector3.ZERO
	# Grazing rays converge slowly. Bracket against the closest sphere point.
	var end := origin + direction * closest
	if end.length() - 1.0 - height_at(uv_of(end)) > 0: return Vector3.ZERO
	var lo := previous; var hi := closest
	for i: int in 28:
		var mid := (lo + hi) * .5; var q := origin + direction * mid
		if q.length() - 1.0 - height_at(uv_of(q)) > 0: lo = mid
		else: hi = mid
	return origin + direction * ((lo + hi) * .5)
