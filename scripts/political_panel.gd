extends VBoxContainer
const Rules = preload("res://scripts/government_rules.gd")
const Summary = preload("res://scripts/political_summary.gd")
const Icons = preload("res://scripts/ui_icons.gd")
var world: RefCounted
var country := ""
var on_change: Callable
var property_buttons: Dictionary = {}
var choice_buttons: Dictionary = {}
var choice_dialog: AcceptDialog
var choice_content: VBoxContainer
var active_property: Dictionary = {}
var balance_label: Label

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
	add_child(HSeparator.new())
	var heading := Label.new()
	heading.text = "GOVERNMENT PROPERTIES"
	heading.add_theme_font_size_override("font_size", 11)
	heading.add_theme_color_override("font_color", Color("76c6bc"))
	add_child(heading)
	var properties := HFlowContainer.new()
	properties.add_theme_constant_override("h_separation", 6)
	properties.add_theme_constant_override("v_separation", 6)
	add_child(properties)
	for property: Dictionary in Rules.PROPERTIES:
		var button := Button.new()
		button.name = "Property_" + str(property["key"])
		button.custom_minimum_size = Vector2(170, 58)
		button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		button.icon = Icons.icon(property["icon"])
		button.expand_icon = true
		button.add_theme_constant_override("icon_max_width", 20)
		button.add_theme_font_size_override("font_size", 11)
		button.clip_text = true
		button.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
		button.pressed.connect(func(): open_property(property))
		property_buttons[property["key"]] = button
		properties.add_child(button)
	choice_dialog = AcceptDialog.new()
	choice_dialog.name = "GovernmentPropertyChoice"
	choice_dialog.exclusive = true
	choice_dialog.ok_button_text = "Cancel"
	add_child(choice_dialog)
	choice_content = VBoxContainer.new()
	choice_content.add_theme_constant_override("separation", 8)
	choice_dialog.add_child(choice_content)
	refresh()

func refresh() -> void:
	for property: Dictionary in Rules.PROPERTIES:
		var current: String = world.government_property(country, property["key"])
		var button: Button = property_buttons[property["key"]]
		button.text = str(property["title"]) + "\n" + ("Not set" if current.is_empty() else current)
		button.tooltip_text = str(property["help"]) + "\nClick to change · 100 political power"
	if choice_dialog.visible: _refresh_choices()

func open_property(property: Dictionary) -> void:
	active_property = property
	choice_dialog.title = property["title"]
	for child: Node in choice_content.get_children():
		choice_content.remove_child(child)
		child.queue_free()
	choice_buttons.clear()
	var explanation := Label.new()
	explanation.text = property["help"]
	explanation.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	explanation.custom_minimum_size.x = 300
	choice_content.add_child(explanation)
	balance_label = Label.new()
	balance_label.add_theme_font_size_override("font_size", 12)
	choice_content.add_child(balance_label)
	for option: String in property["options"]:
		var button := Button.new()
		button.custom_minimum_size = Vector2(300, 36)
		button.add_theme_font_size_override("font_size", 13)
		button.pressed.connect(func(): apply_choice(option))
		choice_buttons[option] = button
		choice_content.add_child(button)
	_refresh_choices()
	choice_dialog.popup_centered(Vector2i(340, 0))

func _refresh_choices() -> void:
	var balance: float = world.political_power(country)
	balance_label.text = "Change: 100 PP  ·  Available: %.1f PP" % balance
	for option: String in choice_buttons:
		var current: bool = world.government_property(country, active_property["key"]) == option
		var button: Button = choice_buttons[option]
		button.text = option + ("  ·  Current" if current else "  ·  100 PP")
		button.disabled = current or balance < Rules.CHANGE_COST
		button.tooltip_text = "Current setting" if current else ("Requires 100 political power" if button.disabled else "Apply for 100 political power")

func apply_choice(value: String) -> void:
	if world.change_government_property(country, active_property["key"], value):
		choice_dialog.hide()
		refresh()
		if on_change.is_valid(): on_change.call()
	else:
		_refresh_choices()
