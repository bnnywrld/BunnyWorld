extends Control
var counts: Dictionary = {}
var colors: Dictionary = {}
var hovered := ""
const PALETTE := [Color("56c6b5"), Color("ddba72"), Color("729bd7"), Color("c784a9"), Color("91b875"), Color("bb906b"), Color("9386ca"), Color("d77e6c"), Color("738b99")]
func configure(values: Dictionary, kind: String = "") -> void:
	counts = values
	var index := 0
	for key: String in counts:
		colors[key] = Color("647681") if key == "Unknown" or key == "Other / unspecified" else PALETTE[index % PALETTE.size()]
		if kind == "religion": colors[key] = preload("res://scripts/religion_catalog.gd").color(key)
		index += 1
	custom_minimum_size = Vector2(86, 86)
	mouse_filter = Control.MOUSE_FILTER_STOP
	mouse_exited.connect(func(): hovered = ""; queue_redraw())
	queue_redraw()
func _draw() -> void:
	var center := size / 2
	var radius := minf(size.x, size.y) * .45
	if radius <= .1: return
	var total := 0
	for v: Variant in counts.values(): total += int(v)
	if total == 0:
		draw_circle(center, radius, Color("364a57"))
		return
	var angle := -PI / 2
	for key: String in counts:
		var fraction := float(counts[key]) / total
		if fraction <= 0: continue
		var end := angle + fraction * TAU
		if fraction >= .999999:
			draw_circle(center, radius, colors[key])
			angle = end
			continue
		if fraction < .000001:
			angle = end
			continue
		var points := PackedVector2Array([center])
		var segments := maxi(2, int(ceil(fraction * 90)))
		for i: int in segments + 1: points.append(center + Vector2.from_angle(lerpf(angle, end, float(i)/segments))*radius)
		var color: Color = colors[key]
		if not hovered.is_empty(): color = color.lightened(.2) if key == hovered else color.darkened(.25)
		draw_colored_polygon(points, color)
		angle = end
	draw_circle(center, radius*.47, Color("102332"))
func _gui_input(event: InputEvent) -> void:
	if not event is InputEventMouseMotion: return
	var offset: Vector2 = event.position - size/2
	var total := 0
	for v: Variant in counts.values(): total += int(v)
	hovered = ""
	if total > 0 and offset.length() < minf(size.x,size.y)*.45:
		var angle := fposmod(offset.angle()+PI/2, TAU)
		var cursor := 0.0
		for key: String in counts:
			cursor += float(counts[key])/total*TAU
			if angle <= cursor:
				hovered = key
				tooltip_text = "%s: %s people · %.1f%%" % [key, preload("res://scripts/display_format.gd").people(int(counts[key])), float(counts[key])/total*100]
				break
	queue_redraw()
