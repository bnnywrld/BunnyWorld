extends Control
## Lightweight vector placeholders. No portraits, party data or seat allocations.
signal activated
var can_activate := false
var portrait := false
var hovered_seat := -1
var seats: Array[Vector2] = []
var seat_radius := 4.0

func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP if not portrait else Control.MOUSE_FILTER_IGNORE
	if can_activate: mouse_default_cursor_shape = Control.CURSOR_POINTING_HAND
	resized.connect(queue_redraw)
	mouse_exited.connect(func(): hovered_seat = -1; queue_redraw())

func _draw() -> void:
	if portrait:
		var center := size * Vector2(.5, .42)
		draw_style_box(_plate(), Rect2(Vector2.ZERO, size))
		draw_circle(center, size.x * .17, Color("60757d"))
		var shoulders := Rect2(size.x * .19, size.y * .63, size.x * .62, size.y * .28)
		var style := StyleBoxFlat.new()
		style.bg_color = Color("60757d")
		style.set_corner_radius_all(20)
		draw_style_box(style, shoulders)
		return
	seats.clear()
	var center := Vector2(size.x * .5, size.y - 14)
	var outer := minf(size.x * .47, size.y - 24)
	seat_radius = clampf(outer / 27.0, .9, 5.0)
	# Exactly 100 empty seats. All neutral until political data is introduced.
	var counts: Array[int] = [12, 16, 20, 24, 28]
	for row: int in counts.size():
		var radius := outer * (.38 + .155 * row)
		for seat: int in counts[row]:
			var angle := PI + PI * (float(seat) + .5) / counts[row]
			var point := center + Vector2(cos(angle), sin(angle)) * radius
			seats.append(point)
	for i: int in seats.size():
		var point := seats[i]
		draw_circle(point, seat_radius + 1, Color("314a54"))
		draw_circle(point, seat_radius, Color("87b9b4") if i == hovered_seat else Color("647a83"))
	draw_arc(center, outer * .25, PI, TAU, 40, Color("3d686c"), 2, true)

func _plate() -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = Color("142a35")
	style.border_color = Color("35505a")
	style.set_border_width_all(1)
	style.set_corner_radius_all(6)
	return style

func _gui_input(event: InputEvent) -> void:
	if can_activate and event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT and event.pressed:
		activated.emit()
		accept_event()
		return
	if event is InputEventMouseMotion:
		var next := -1
		for i: int in seats.size():
			if event.position.distance_to(seats[i]) <= seat_radius + 2:
				next = i
				break
		if next != hovered_seat:
			hovered_seat = next
			tooltip_text = "Open government" if can_activate else ("Unassigned seat" if next >= 0 else "Parliament · 100 unassigned seats")
			queue_redraw()
