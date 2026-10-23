extends Control
# One static graph per selected category. Layout/drawing changes only on rebuild.
var edges: Array = []

func _draw() -> void:
	for edge: Array in edges:
		var from: Vector2 = edge[0]
		var to: Vector2 = edge[1]
		var color := Color("536777")
		if is_equal_approx(from.x, to.x):
			draw_line(from, to, color, 2, true)
		else:
			# Cross-branch links travel in the gutter, clear of technology cards.
			var gutter := from.x + 88
			draw_polyline(PackedVector2Array([from, from + Vector2(0, 12), Vector2(gutter, from.y + 12), Vector2(gutter, to.y - 14), Vector2(to.x, to.y - 14), to]), color, 2, true)
		draw_colored_polygon(PackedVector2Array([to, to + Vector2(-5, -7), to + Vector2(5, -7)]), color)
