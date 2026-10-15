extends Control
var markers: Array[Dictionary] = []
func _draw() -> void:
	var font := ThemeDB.fallback_font
	for marker: Dictionary in markers:
		var p: Vector2 = marker["point"]
		if marker.get("landmark", false):
			draw_colored_polygon(PackedVector2Array([p + Vector2(0,-4),p + Vector2(4,0),p + Vector2(0,4),p + Vector2(-4,0)]),Color("edcf92"))
		elif marker["capital"]:
			var star := PackedVector2Array()
			for i: int in 10:
				var angle := -PI / 2.0 + i * PI / 5.0
				star.append(p + Vector2(cos(angle), sin(angle)) * (6.0 if i % 2 == 0 else 2.7))
			draw_colored_polygon(star, Color("ffdc80"))
		else:
			draw_circle(p, 3.6, Color("091421"))
			draw_circle(p, 2.1, Color("edf4f6"))
		var at := p + Vector2(9, 5)
		draw_string_outline(font, at, marker["name"], HORIZONTAL_ALIGNMENT_LEFT, -1, 13, 4, Color("081421"))
		draw_string(font, at, marker["name"], HORIZONTAL_ALIGNMENT_LEFT, -1, 13, Color("ffdc80") if marker["capital"] or marker.get("landmark", false) else Color("e4eef1"))
