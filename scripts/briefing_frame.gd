extends PanelContainer
func _draw() -> void:
 draw_rect(Rect2(Vector2(3,3),size-Vector2(6,6)),Color(.38,.45,.47,.24),false,1)
 draw_line(Vector2(12,3),Vector2(minf(size.x-12,88),3),Color("b8a375"),2,true)
 draw_line(Vector2(12,7),Vector2(size.x-12,7),Color(.65,.60,.45,.12),1,true)
 draw_line(Vector2(7,size.y-14),Vector2(7,size.y-7),Color(.65,.60,.45,.3),1,true)
 draw_line(Vector2(7,size.y-7),Vector2(30,size.y-7),Color(.65,.60,.45,.3),1,true)
