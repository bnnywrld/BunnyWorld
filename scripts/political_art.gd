extends Control
## Shared parliament snapshot; leadership portraits remain placeholders.
signal activated
var can_activate := false
var portrait := false
var hovered_seat := -1
var seats: Array[Vector2] = []
var seat_radius := 4.0
var party_seats: Array[Dictionary] = []
var seat_info: Array[Dictionary] = []
var geometry_key: Array = []
var group_shapes: Dictionary = {}
var group_colors: Dictionary = {}
var seat_center := Vector2.ZERO
var outer_radius := 1.0

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
	var key := [size, hash(party_seats)]
	if key != geometry_key:
		geometry_key = key
		_rebuild_seats()
	var active := hovered_party()
	for id: String in group_shapes:
		var selected := id == active
		var tint := Color(group_colors[id])
		for polygon: PackedVector2Array in group_shapes[id]:
			draw_colored_polygon(polygon, Color(tint, .20 if selected else .05))
			var outline := polygon.duplicate()
			outline.append(polygon[0])
			draw_polyline(outline, Color("e1cf9e") if selected else Color(tint, .40), 1.6 if selected else .7, true)
	for i: int in seats.size():
		var point := seats[i]
		var selected := not active.is_empty() and i < seat_info.size() and str(seat_info[i].get("id", "")) == active
		draw_circle(point, seat_radius + 1, Color("314a54"))
		var tint := Color(seat_info[i]["color"]) if i < seat_info.size() and not seat_info[i].is_empty() else Color("647a83")
		draw_circle(point, seat_radius, tint.lightened(.35) if selected else tint)
	draw_arc(seat_center, outer_radius * .25, PI, TAU, 40, Color("3d686c"), 2, true)

func hovered_party() -> String:
	return str(seat_info[hovered_seat].get("id", "")) if hovered_seat >= 0 and hovered_seat < seat_info.size() else ""

func _rebuild_seats() -> void:
	seats.clear()
	seat_info.clear()
	group_shapes.clear()
	group_colors.clear()
	seat_center = Vector2(size.x * .5, size.y - 14)
	outer_radius = minf((size.x - 12) * .5 / 1.08, (size.y - 28) / 1.08)
	seat_radius = clampf(outer_radius / 27.0, .9, 5.0)
	var cells: Array[PackedVector2Array] = []
	var angular: Array[Dictionary] = []
	var counts: Array[int] = [12, 16, 20, 24, 28]
	for row: int in counts.size():
		var radius := outer_radius * (.38 + .155 * row)
		var inner := radius - outer_radius * .0775 - .6
		var outer := radius + outer_radius * .0775 + .6
		for seat: int in counts[row]:
			var angle := PI + PI * (float(seat) + .5) / counts[row]
			angular.append({"index":seats.size(), "angle":angle, "row":row})
			seats.append(seat_center + Vector2.from_angle(angle) * radius)
			seat_info.append({})
			var cell := PackedVector2Array()
			var begin := PI + PI * float(seat) / counts[row] - .0001
			var end := PI + PI * float(seat + 1) / counts[row] + .0001
			for step: int in 5: cell.append(seat_center + Vector2.from_angle(lerpf(begin, end, step / 4.0)) * outer)
			for step: int in 5: cell.append(seat_center + Vector2.from_angle(lerpf(end, begin, step / 4.0)) * inner)
			cells.append(cell)
	# Fill angular wedges across all rows instead of stripes along individual rings.
	angular.sort_custom(func(a: Dictionary, b: Dictionary): return int(a["row"]) < int(b["row"]) if is_equal_approx(a["angle"], b["angle"]) else float(a["angle"]) < float(b["angle"]))
	var cursor := 0
	for party: Dictionary in party_seats:
		var id := str(party["id"])
		group_shapes[id] = []
		group_colors[id] = party["color"]
		for i: int in int(party["seats"]):
			if cursor >= angular.size(): break
			var index := int(angular[cursor]["index"])
			seat_info[index] = party
			_merge_cell(id, cells[index])
			cursor += 1

func _merge_cell(id: String, cell: PackedVector2Array) -> void:
	var parts: Array = group_shapes[id]
	var index := 0
	while index < parts.size():
		var combined := Geometry2D.merge_polygons(cell, parts[index])
		if combined.size() == 1:
			cell = combined[0]
			parts.remove_at(index)
			index = 0
		else: index += 1
	parts.append(cell)

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
			if next >= 0 and next < seat_info.size() and not seat_info[next].is_empty():
				var party: Dictionary = seat_info[next]
				tooltip_text = "%s\n%s · %.2f%% support · %d seats" % [party["name"], party["outlook"], party["support"], party["seats"]]
				if not str(party.get("government_status", "")).is_empty(): tooltip_text += "\n" + str(party["government_status"])
			else: tooltip_text = "Open government" if can_activate else "Parliament · unassigned seats"
			queue_redraw()
