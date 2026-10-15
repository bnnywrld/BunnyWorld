extends SceneTree
const Surface = preload("res://scripts/relief_surface.gd")
var failures := 0
func check(value: bool, label: String) -> void:
	if not value: failures += 1; printerr("FAIL: ", label)
func _initialize() -> void:
	var relief := Surface.new()
	check(relief.bytes.size() == 8192 * 4096 * 2, "bounded binary elevation field")
	var image: Image = load("res://assets/relief_data.png").get_image()
	if image.is_compressed(): image.decompress()
	for y: int in range(0, 4096, 277):
		for x: int in range(0, 8192, 431):
			var uv := Vector2((x + .5) / 8192.0, (y + .5) / 4096.0)
			var pixel := image.get_pixel(x, y)
			var gpu := (roundf(pixel.r * 255) + roundf(pixel.g * 255) * 256) / 65535.0 * .016
			check(absf(gpu - relief.height_at(uv)) < .00000005, "GPU/CPU elevation channels agree")
	for coordinates: Vector2 in [Vector2(86.8, 28), Vector2(80.5,31), Vector2(-40,73), Vector2(-140,0), Vector2(139.75,35.68), Vector2(142.74,46.95)]:
		var uv := Vector2((coordinates.x + 180) / 360, (90 - coordinates.y) / 180)
		var target := relief.point_at(uv); var n := target.normalized()
		var east := Vector3(cos((uv.x-.5)*TAU), 0, -sin((uv.x-.5)*TAU))
		for degrees: float in [0.0, 20.0, 38.0]:
			var origin := target + (n * cos(deg_to_rad(degrees)) + east * sin(deg_to_rad(degrees))) * .02
			var point := relief.ray_point(origin, (target - origin).normalized())
			check(point != Vector3.ZERO, "raised surface ray hit")
			if point != Vector3.ZERO:
				check(absf(point.length() - 1.0 - relief.height_at(Surface.uv_of(point))) < .000001, "ray solves displaced surface")
				check(point.distance_to(target) < .00004, "close camera anchor remains on terrain")
	check(relief.ray_point(Vector3(0,0,3), Vector3(0,1,0)) == Vector3.ZERO, "sky ray misses planet")
	check(relief.height_at(Vector2(-.001,.5)) == relief.height_at(Vector2(.999,.5)), "elevation wraps dateline")
	if failures == 0: print("RELIEF_TESTS_PASS: raw imported channels, elevation rays, oblique anchors, ocean/land, dateline and bounded field")
	quit(failures)
