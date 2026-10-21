extends VBoxContainer
const Rules = preload("res://scripts/government_rules.gd")
const Summary = preload("res://scripts/political_summary.gd")
const LawIcons = preload("res://scripts/law_icons.gd")
var world: RefCounted
var country := ""
var on_change: Callable
var property_buttons: Dictionary = {}
var choice_buttons: Dictionary = {}
var choice_dialog: AcceptDialog
var choice_content: VBoxContainer
var active_property: Dictionary = {}
var balance_label: Label
var government_type: Label

func configure(state: RefCounted, tag: String, changed: Callable) -> void:
	world = state
	country = tag
	on_change = changed
	name = "PoliticalPanel"
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	add_theme_constant_override("separation", 10)
	var summary := Summary.new()
	summary.configure(false)
	add_child(summary)
	var center: VBoxContainer = summary.parliament.get_parent()
	government_type = _label("", 12, Color("e1cf9e"))
	government_type.name = "GovernmentType"
	government_type.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	government_type.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	center.add_child(government_type)
	center.move_child(government_type, 0)
	add_child(HSeparator.new())
	add_child(_label("CONSTITUTION & LAWS", 13, Color("76c6bc")))
	for category: Dictionary in Rules.CATEGORIES:
		var group := VBoxContainer.new()
		group.name = str(category["title"]).replace(" ", "")
		group.add_theme_constant_override("separation", 5)
		add_child(group)
		group.add_child(_label(category["title"], 12, Color("b5c9ce")))
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation", 9)
		group.add_child(row)
		for property: Dictionary in Rules.PROPERTIES:
			if property["key"] not in category["keys"]: continue
			var button := Button.new()
			button.name = "Property_" + str(property["key"])
			button.custom_minimum_size = Vector2(56, 56)
			button.expand_icon = true
			button.add_theme_constant_override("icon_max_width", 42)
			button.add_theme_stylebox_override("normal", _button_style(Color("152c38"), Color("37515b")))
			button.add_theme_stylebox_override("hover", _button_style(Color("25434c"), Color("80bfb5")))
			button.add_theme_stylebox_override("focus", _button_style(Color("25434c", 0.3), Color("e1cf9e")))
			button.add_theme_stylebox_override("pressed", _button_style(Color("10232d"), Color("e1cf9e")))
			button.pressed.connect(func(): open_property(property))
			property_buttons[property["key"]] = button
			row.add_child(button)
	choice_dialog = AcceptDialog.new()
	choice_dialog.name = "GovernmentPropertyChoice"
	choice_dialog.exclusive = true
	choice_dialog.ok_button_text = "Close"
	add_child(choice_dialog)
	choice_content = VBoxContainer.new()
	choice_content.add_theme_constant_override("separation", 8)
	choice_dialog.add_child(choice_content)
	refresh()

func refresh() -> void:
	government_type.text = Rules.government_title(world.government_properties.get(country, {}))
	for property: Dictionary in Rules.PROPERTIES:
		var current: String = world.government_property(country, property["key"])
		var button: Button = property_buttons[property["key"]]
		button.icon = LawIcons.icon(property["key"], maxi(0, property["options"].find(current)))
		button.tooltip_text = "%s\n%s\nChange: %d Political Power" % [property["title"], current, int(Rules.CHANGE_COST)]
	if choice_dialog.visible: _refresh_choices()

func open_property(property: Dictionary) -> void:
	active_property = property
	choice_dialog.hide()
	choice_dialog.title = property["title"]
	for child: Node in choice_content.get_children():
		choice_content.remove_child(child)
		child.queue_free()
	choice_buttons.clear()
	var explanation := _label(property["help"], 12, Color("b5c9ce"))
	explanation.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	explanation.custom_minimum_size.x = 310
	choice_content.add_child(explanation)
	balance_label = _label("", 12, Color("e1cf9e"))
	choice_content.add_child(balance_label)
	for option: String in property["options"]:
		var button := Button.new()
		button.custom_minimum_size = Vector2(310, 40)
		button.add_theme_font_size_override("font_size", 12)
		button.icon = LawIcons.icon(property["key"], property["options"].find(option))
		button.expand_icon = true
		button.add_theme_constant_override("icon_max_width", 30)
		button.pressed.connect(func(): apply_choice(option))
		choice_buttons[option] = button
		choice_content.add_child(button)
	_refresh_choices()
	choice_dialog.reset_size()
	# Use viewport coordinates so embedded dialogs also work with stretched windows.
	var button: Button = property_buttons[property["key"]]
	var anchor: Rect2 = button.get_global_rect()
	var bounds := get_viewport_rect().size
	var popup_size := Vector2(choice_dialog.size)
	var origin := Vector2(anchor.end.x + 8, anchor.position.y)
	if origin.x + popup_size.x > bounds.x - 12:
		origin.x = anchor.position.x - popup_size.x - 8
	origin.x = clampf(origin.x, 12, maxf(12, bounds.x - popup_size.x - 12))
	origin.y = clampf(origin.y, 12, maxf(12, bounds.y - popup_size.y - 12))
	choice_dialog.popup(Rect2i(Vector2i(origin), choice_dialog.size))

func _refresh_choices() -> void:
	var balance: float = world.political_power(country)
	balance_label.text = "Change: %d PP  ·  Available: %.1f PP" % [int(Rules.CHANGE_COST), balance]
	for option: String in choice_buttons:
		var current: bool = world.government_property(country, active_property["key"]) == option
		var button: Button = choice_buttons[option]
		button.text = option + ("  ·  Current" if current else "  ·  %d PP" % int(Rules.CHANGE_COST))
		button.disabled = current or balance < Rules.CHANGE_COST or country != world.player_country
		button.tooltip_text = "Current law" if current else ("Requires %d Political Power" % int(Rules.CHANGE_COST) if button.disabled else "Apply for %d Political Power" % int(Rules.CHANGE_COST))

func apply_choice(value: String) -> void:
	if world.change_government_property(country, active_property["key"], value):
		choice_dialog.hide()
		refresh()
		if on_change.is_valid(): on_change.call()
	else:
		_refresh_choices()

func _label(text: String, font_size: int, color: Color) -> Label:
	var label := Label.new()
	label.text = text
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	return label

func _button_style(background: Color, border: Color) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = background
	style.border_color = border
	style.set_border_width_all(1)
	style.set_corner_radius_all(3)
	style.set_content_margin_all(5)
	return style
