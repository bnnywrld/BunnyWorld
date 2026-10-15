extends RefCounted

static func relation(score: float) -> Color:
	var neutral := Color("f6d94d")
	var middle := Color("35965d") if score > 0.0 else Color("de383c")
	var extreme := Color("124b32") if score > 0.0 else Color("641621")
	var value := absf(score)
	return neutral.lerp(middle, value / 100.0) if value <= 100.0 else middle.lerp(extreme, clampf((value - 100.0) / 100.0, 0.0, 1.0))

static func economic(value: float, per_capita: bool) -> Color:
	if value <= 0.0: return Color("59636c")
	var t := clampf(log(1.0 + value / 1000.0) / log(101.0), 0.0, 1.0) if per_capita else clampf(log(maxf(value, 1e8) / 1e8) / log(1e5), 0.0, 1.0)
	var colors := [Color("fff2ce"), Color("edc16a"), Color("cc8f32"), Color("965b19"), Color("542d0c")]
	var index := mini(int(t * 4.0), 3)
	return colors[index].lerp(colors[index + 1], t * 4.0 - index)
