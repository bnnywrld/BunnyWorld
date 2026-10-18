extends HBoxContainer
const Art = preload("res://scripts/political_art.gd")
var parliament: Control

func configure(compact: bool, open_government: Callable = Callable()) -> void:
	name = "PoliticalSummary"
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	add_theme_constant_override("separation", 6 if compact else 12)
	add_child(_office("Head of state", compact))
	var center := VBoxContainer.new()
	center.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	center.add_theme_constant_override("separation", 2)
	add_child(center)
	center.add_child(_label("PARLIAMENT", 9 if compact else 12, Color("a6c5c7")))
	parliament = Art.new()
	parliament.name = "ParliamentSeats"
	parliament.custom_minimum_size = Vector2(138, 88) if compact else Vector2(230, 132)
	parliament.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	parliament.can_activate = not open_government.is_null()
	if parliament.can_activate: parliament.activated.connect(open_government)
	parliament.tooltip_text = "Open government" if parliament.can_activate else "Parliament · 100 unassigned seats"
	center.add_child(parliament)
	center.add_child(_label("100 seats · unassigned", 9 if compact else 11, Color("93a8b1")))
	center.add_child(_label("Election · —", 9 if compact else 11, Color("93a8b1")))
	add_child(_office("Head of government", compact))

func _office(title: String, compact: bool) -> Control:
	var box := VBoxContainer.new()
	var width := 64 if compact else 94
	box.custom_minimum_size.x = width
	box.add_theme_constant_override("separation", 3 if compact else 6)
	var role := _label(title, 9 if compact else 10, Color("9eb5bb"))
	role.custom_minimum_size = Vector2(width, 26)
	role.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	box.add_child(role)
	var portrait := Art.new()
	portrait.portrait = true
	portrait.custom_minimum_size = Vector2(46, 58) if compact else Vector2(72, 90)
	portrait.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	box.add_child(portrait)
	box.add_child(_label("—", 12 if compact else 16, Color("e5e9e6")))
	return box

func _label(text: String, font_size: int, color: Color) -> Label:
	var label := Label.new()
	label.text = text
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return label
