extends VBoxContainer
## Interface-only choices, owned by main rather than WorldState or save data.
const Art = preload("res://scripts/political_art.gd")
const Icons = preload("res://scripts/ui_icons.gd")
const PROPERTIES := [
	{"key":"constitution", "title":"Constitution", "icon":"politics", "help":"The constitutional form of the state.", "options":["Republic", "Constitutional monarchy", "Absolute monarchy"]},
	{"key":"executive", "title":"Executive system", "icon":"organizations", "help":"How executive leadership is organized.", "options":["Parliamentary", "Presidential", "Semi-presidential", "Single rule"]},
	{"key":"competition", "title":"Political competition", "icon":"population", "help":"The framework for political participation.", "options":["Competitive democracy", "Restricted competition", "One-party rule", "Closed authoritarian rule"]},
	{"key":"selection", "title":"Selection rules", "icon":"ledger", "help":"How the head of state is selected.", "options":["Direct election", "Indirect election", "Parliamentary appointment", "Hereditary succession"]},
	{"key":"power", "title":"Distribution of power", "icon":"stability", "help":"The balance of authority among governing institutions.", "options":["Legislature-led", "Balanced powers", "Executive-led", "Concentrated authority"]}
]
var choices: Dictionary
var selectors: Dictionary = {}

func configure(values: Dictionary) -> void:
	choices = values
	name = "PoliticalPanel"
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	add_theme_constant_override("separation", 16)
	var institutions := PanelContainer.new()
	institutions.add_theme_stylebox_override("panel", _style(Color("0c1c27"), 14))
	add_child(institutions)
	var offices := HBoxContainer.new()
	offices.add_theme_constant_override("separation", 18)
	institutions.add_child(offices)
	offices.add_child(_office("HEAD OF STATE"))
	var legislature := VBoxContainer.new()
	legislature.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	legislature.add_theme_constant_override("separation", 4)
	offices.add_child(legislature)
	legislature.add_child(_label("PARLIAMENT", 13, Color("a6c5c7")))
	var arc := Art.new()
	arc.name = "ParliamentSeats"
	arc.custom_minimum_size = Vector2(260, 146)
	arc.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	arc.tooltip_text = "Parliament · 100 unassigned seats"
	legislature.add_child(arc)
	legislature.add_child(_label("100 seats · unassigned", 12, Color("93a8b1")))
	legislature.add_child(_label("Next election · —", 12, Color("93a8b1")))
	offices.add_child(_office("HEAD OF GOVERNMENT"))
	var heading := _label("GOVERNMENT PROPERTIES", 12, Color("76c6bc"))
	heading.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	add_child(heading)
	var properties := HFlowContainer.new()
	properties.add_theme_constant_override("h_separation", 8)
	properties.add_theme_constant_override("v_separation", 8)
	add_child(properties)
	for property: Dictionary in PROPERTIES:
		properties.add_child(_property(property))

func _office(title: String) -> Control:
	var box := VBoxContainer.new()
	box.custom_minimum_size.x = 116
	box.add_theme_constant_override("separation", 8)
	var role := _label(title, 10, Color("9eb5bb"))
	role.custom_minimum_size = Vector2(116, 30)
	role.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	box.add_child(role)
	var portrait := Art.new()
	portrait.portrait = true
	portrait.custom_minimum_size = Vector2(92, 112)
	portrait.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	box.add_child(portrait)
	box.add_child(_label("—", 18, Color("e5e9e6")))
	return box

func _property(property: Dictionary) -> Control:
	var plate := PanelContainer.new()
	plate.custom_minimum_size = Vector2(132, 102)
	plate.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	plate.add_theme_stylebox_override("panel", _style(Color("132732"), 9))
	plate.tooltip_text = property["help"]
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 6)
	plate.add_child(box)
	var heading := HBoxContainer.new()
	heading.add_theme_constant_override("separation", 6)
	box.add_child(heading)
	var icon := TextureRect.new()
	icon.texture = Icons.icon(property["icon"])
	icon.custom_minimum_size = Vector2(20, 20)
	icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	heading.add_child(icon)
	var title := _label(property["title"], 11, Color("9eb5bb"))
	title.custom_minimum_size = Vector2(76, 30)
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	title.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	heading.add_child(title)
	var picker := OptionButton.new()
	picker.name = "Property_" + str(property["key"])
	picker.custom_minimum_size = Vector2(112, 36)
	picker.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	picker.fit_to_longest_item = false
	picker.clip_text = true
	picker.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	picker.add_theme_font_size_override("font_size", 12)
	picker.add_item("Not set")
	for option: String in property["options"]:
		picker.add_item(option)
	var current: String = str(choices.get(property["key"], ""))
	picker.select(property["options"].find(current) + 1 if not current.is_empty() else 0)
	picker.tooltip_text = str(property["help"]) + "\nCurrent: " + (current if not current.is_empty() else "Not set")
	picker.item_selected.connect(func(index: int):
		var value := "" if index == 0 else str(property["options"][index - 1])
		if value.is_empty(): choices.erase(property["key"])
		else: choices[property["key"]] = value
		picker.tooltip_text = str(property["help"]) + "\nCurrent: " + (value if not value.is_empty() else "Not set"))
	selectors[property["key"]] = picker
	box.add_child(picker)
	return plate

func _label(text: String, font_size: int, color: Color) -> Label:
	var label := Label.new()
	label.text = text
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return label

func _style(color: Color, padding: int) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = color
	style.border_color = Color("2c4854")
	style.set_border_width_all(1)
	style.set_corner_radius_all(6)
	style.content_margin_left = padding
	style.content_margin_right = padding
	style.content_margin_top = padding
	style.content_margin_bottom = padding
	return style
