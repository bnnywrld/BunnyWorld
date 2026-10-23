extends VBoxContainer
const FloatingPanel = preload("res://scripts/styled_popup.gd")
const Rules = preload("res://scripts/government_rules.gd")
const Summary = preload("res://scripts/political_summary.gd")
const LawIcons = preload("res://scripts/law_icons.gd")
var world: RefCounted
var country := ""
var on_change: Callable
var property_buttons: Dictionary = {}
var choice_buttons: Dictionary = {}
var choice_dialog: FloatingPanel
var choice_content: VBoxContainer
var active_property: Dictionary = {}
var balance_label: Label
var government_type: Label
var affiliation_picker: OptionButton
var affiliations: Array = []
var agenda_button: Button

func configure(state: RefCounted, tag: String, changed: Callable, host: Control) -> void:
	world = state
	country = tag
	on_change = changed
	name = "PoliticalPanel"
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	add_theme_constant_override("separation", 10)
	var summary := Summary.new()
	summary.configure(false)
	summary.configure_parties(world, country)
	add_child(summary)
	government_type = summary.government_type
	add_child(HSeparator.new())
	agenda_button = preload("res://scripts/progress_button.gd").new()
	agenda_button.name = "Agenda"
	agenda_button.custom_minimum_size.y = 56
	agenda_button.alignment = HORIZONTAL_ALIGNMENT_LEFT
	agenda_button.add_theme_font_size_override("font_size", 13)
	agenda_button.pressed.connect(func(): host._show_feature("Agenda"))
	add_child(agenda_button)
	world.agenda.changed.connect(refresh)
	add_child(_label("CONSTITUTION & LAWS", 13, Color("76c6bc")))
	for category: Dictionary in Rules.CATEGORIES:
		var group := VBoxContainer.new()
		group.name = str(category["title"]).replace(" ", "")
		group.add_theme_constant_override("separation", 5)
		add_child(group)
		group.add_child(_label(category["title"], 12, Color("b5c9ce")))
		var row := GridContainer.new()
		row.columns = 2
		row.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_theme_constant_override("h_separation", 6)
		row.add_theme_constant_override("v_separation", 4)
		group.add_child(row)
		for property: Dictionary in Rules.PROPERTIES:
			if property["key"] not in category["keys"]: continue
			var button := Button.new()
			button.name = "Property_" + str(property["key"])
			button.custom_minimum_size = Vector2(0, 44)
			button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
			button.alignment = HORIZONTAL_ALIGNMENT_LEFT
			button.clip_text = true
			button.add_theme_font_size_override("font_size", 12)
			button.expand_icon = true
			button.add_theme_constant_override("icon_max_width", 28)
			button.add_theme_stylebox_override("normal", _button_style(Color("152c38"), Color("37515b")))
			button.add_theme_stylebox_override("hover", _button_style(Color("25434c"), Color("80bfb5")))
			button.add_theme_stylebox_override("focus", _button_style(Color("25434c", 0.3), Color("e1cf9e")))
			button.add_theme_stylebox_override("pressed", _button_style(Color("10232d"), Color("e1cf9e")))
			button.pressed.connect(func(): open_property(property))
			property_buttons[property["key"]] = button
			row.add_child(button)
	choice_dialog = FloatingPanel.new()
	choice_dialog.name = "GovernmentPropertyChoice"
	host.add_child(choice_dialog)
	choice_content = choice_dialog.content

	refresh()

func refresh() -> void:
	government_type.text = Rules.government_title(world.government_properties.get(country, {}))
	agenda_button.text = "Agenda"
	agenda_button.tooltip_text = "Open agenda"
	var progress := 0.0
	if country == world.player_country and not world.agenda.queue.is_empty():
		var item: Dictionary = world.agenda.queue[0]
		agenda_button.text += " · %s\n%s · %d days remaining" % [world.agenda.title(item), item["value"], item["days"] - item["elapsed"]]
		progress = float(item["elapsed"]) / item["days"]
		agenda_button.tooltip_text = "%d reform(s) · Click to open agenda" % world.agenda.queue.size()
	agenda_button.set_progress(progress)
	for property: Dictionary in Rules.PROPERTIES:
		var current: String = world.government_property(country, property["key"])
		var button: Button = property_buttons[property["key"]]
		button.icon = LawIcons.icon(property["key"], maxi(0, property["options"].find(current)))
		button.text = str(property["title"]) + "\n" + current
		button.tooltip_text = "%s\n%s\n%s\nBase change: 100 PP; ordered jumps: 100 × steps²." % [property["title"], current, property["help"]]
		if property["key"] == "religion" and current in world.society.AFFILIATED:
			var faith := str(world.society.nations[country]["affiliation"])
			button.text += " · " + (faith if not faith.is_empty() else "—")
			button.tooltip_text += "\nAssociated religion: " + (faith if not faith.is_empty() else "Unspecified in starting data; select explicitly")
	if choice_dialog.visible: _refresh_choices()

func open_property(property: Dictionary) -> void:
	active_property = property
	choice_dialog.hide()
	choice_dialog.title = property["title"]
	for child: Node in choice_content.get_children():
		choice_content.remove_child(child)
		child.queue_free()
	choice_buttons.clear()
	affiliation_picker = null
	var explanation := _label(property["help"], 12, Color("b5c9ce"))
	explanation.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	explanation.custom_minimum_size.x = 310
	choice_content.add_child(explanation)
	balance_label = _label("", 12, Color("e1cf9e"))
	choice_content.add_child(balance_label)
	if property["key"] == "religion":
		choice_content.add_child(_label("Associated religion", 12, Color("e1cf9e")))
		affiliation_picker = OptionButton.new()
		affiliation_picker.name = "AssociatedReligion"
		affiliation_picker.add_item("Select affiliation")
		affiliations = preload("res://scripts/religion_catalog.gd").affiliations()
		var current_faith: String = world.society.nations[country]["affiliation"]
		for faith: String in affiliations: affiliation_picker.add_item(faith)
		affiliation_picker.select(affiliations.find(current_faith) + 1)
		affiliation_picker.disabled = country != world.player_country
		affiliation_picker.item_selected.connect(func(_index: int): _refresh_choices())
		choice_content.add_child(affiliation_picker)
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
	var button: Button = property_buttons[property["key"]]
	# Place to the right of the law grid so other law buttons remain exposed.
	var anchor := Rect2(Vector2(get_global_rect().end.x + 16, button.get_global_rect().position.y), Vector2.ZERO)
	choice_dialog.show_beside(anchor)

func _exit_tree() -> void:
	if is_instance_valid(choice_dialog): choice_dialog.queue_free()

func _refresh_choices() -> void:
	var balance: float = world.political_power(country)
	var current_value: String = world.government_property(country, active_property["key"])
	balance_label.text = "Current: %s\nAvailable: %.1f PP" % [current_value, balance]
	for option: String in choice_buttons:
		var current: bool = world.government_property(country, active_property["key"]) == option
		var button: Button = choice_buttons[option]
		var cost := Rules.change_cost(active_property["key"], current_value, option)
		var needs_faith: bool = active_property["key"] == "religion" and option in world.society.AFFILIATED
		var faith := _selected_affiliation() if needs_faith else ""
		if active_property["key"] == "religion":
			current = current and faith == str(world.society.nations[country]["affiliation"])
			cost = world.society.religion_cost(country, option, faith)
		var steps := Rules.steps(active_property["key"], current_value, option)
		button.text = option + ("  ·  Current" if current else "  ·  %d PP" % int(cost))
		button.disabled = current or balance < cost or country != world.player_country
		if world.agenda.pending(active_property["key"]): button.disabled = true
		if needs_faith and faith.is_empty(): button.disabled = true
		button.tooltip_text = "Current law" if current else "%s → %s\n%d step(s) · %d PP\n%s" % [current_value, option, steps, cost, "Insufficient Political Power" if balance < cost else "Click to add to agenda"]
		if needs_faith and faith.is_empty(): button.tooltip_text = "Select an associated religion first. No faith is chosen automatically."
		elif needs_faith: button.tooltip_text += "\nAssociated religion: " + faith
		button.tooltip_text += "\nAgenda duration: %d days; reforms run sequentially." % world.agenda.duration(active_property["key"], current_value, option)
		if world.agenda.pending(active_property["key"]): button.tooltip_text += "\nA reform of this law is already on the agenda."
		if active_property["key"] == "religion" and current_value == option and cost == 0: button.tooltip_text += "\nComplete the missing starting affiliation at no PP cost."

func _selected_affiliation() -> String:
	if affiliation_picker == null or affiliation_picker.selected <= 0: return ""
	return str(affiliations[affiliation_picker.selected - 1])

func apply_choice(value: String) -> void:
	if world.change_government_property(country, active_property["key"], value, _selected_affiliation()):
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
