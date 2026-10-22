extends VBoxContainer
const Style = preload("res://scripts/ui_style.gd")
const Rules = preload("res://scripts/organization_rules.gd")
var world: RefCounted
var host: Control
var country_tag := ""
var selected_organization := ""
var card_buttons: Dictionary = {}
var member_buttons: Dictionary = {}
var detail_tabs: TabContainer
var directory := false

func configure(state: RefCounted, tag: String, main: Control) -> void:
	name = "OrganizationsPanel"
	world = state
	host = main
	country_tag = tag
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	add_theme_constant_override("separation", 10)
	show_list()

func _clear() -> void:
	for child: Node in get_children(): remove_child(child); child.queue_free()
	card_buttons.clear()
	member_buttons.clear()
	detail_tabs = null

func _text(text: String, font_size: int = 13, color: Color = Style.MUTED_COLOR) -> Label:
	var label := Style.label(text, font_size, color)
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return label

func show_list() -> void:
	_clear()
	selected_organization = ""
	var navigation := HBoxContainer.new()
	add_child(navigation)
	for title: String in ["My memberships", "Organization directory"]:
		var button := Button.new()
		button.text = title
		button.toggle_mode = true
		button.button_pressed = directory == (title == "Organization directory")
		button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		button.pressed.connect(func(): directory = title == "Organization directory"; show_list())
		navigation.add_child(button)
	var ids: Array = Rules.definitions().keys() if directory else world.memberships(country_tag)
	ids.sort_custom(func(a: String, b: String): return _org_name(a).naturalnocasecmp_to(_org_name(b)) < 0)
	add_child(_text("%d organizations" % ids.size() if directory else "%d memberships · %s" % [ids.size(), world.countries[country_tag]["name"]]))
	if ids.is_empty(): add_child(_text("Your country has no organization memberships."))
	for oid: String in ids: _add_card(oid)

func _org(oid: String) -> Dictionary:
	if world.organizations.has(oid): return world.organizations[oid]
	var definition: Dictionary = Rules.definitions()[oid].duplicate(true)
	definition["id"] = oid
	definition["members"] = []
	return definition

func _org_name(oid: String) -> String:
	return Rules.display_name(_org(oid), world.date_dictionary())

func _add_card(oid: String) -> void:
	var org := _org(oid)
	var button := Button.new()
	button.name = "Organization_" + oid
	button.custom_minimum_size = Vector2(0, 136 if org["type"] == "regional" else 118)
	button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	button.tooltip_text = _org_name(oid) + "\nOpen members and features"
	button.pressed.connect(func(): open_organization(oid))
	add_child(button)
	card_buttons[oid] = button
	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for edge: String in ["left", "right", "top", "bottom"]: margin.add_theme_constant_override("margin_" + edge, 12)
	margin.mouse_filter = Control.MOUSE_FILTER_IGNORE
	button.add_child(margin)
	var line := HBoxContainer.new()
	line.mouse_filter = Control.MOUSE_FILTER_IGNORE
	line.add_theme_constant_override("separation", 12)
	margin.add_child(line)
	if world.organizations.has(oid):
		var image := TextureRect.new()
		image.texture = host._organization_texture(oid, true)
		image.custom_minimum_size = Vector2(56, 56)
		image.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		image.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		image.mouse_filter = Control.MOUSE_FILTER_IGNORE
		line.add_child(image)
	var text := VBoxContainer.new()
	text.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	text.mouse_filter = Control.MOUSE_FILTER_IGNORE
	line.add_child(text)
	var title := Style.label(_org_name(oid), 16, Style.HEADING_COLOR)
	title.clip_text = true
	title.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	title.mouse_filter = Control.MOUSE_FILTER_IGNORE
	text.add_child(title)
	var summary: String = Rules.TYPES[str(org["type"])]
	var member_status := Rules.status(org, country_tag)
	if not member_status.is_empty(): summary += " · " + member_status.capitalize()
	text.add_child(_text(summary, 12, Style.ACCENT_COLOR))
	text.add_child(_text("%d full members · %s" % [Rules.full_members(org).size(), Rules.hq_label(org, world.countries)] if world.organizations.has(oid) else "Inactive definition · membership review pending", 12))
	if org["type"] == "regional": text.add_child(_text(Rules.LEVELS[int(org["integration_level"])], 12, Style.GOLD_COLOR))

func open_organization(oid: String, standalone: bool = false) -> void:
	if not Rules.definitions().has(oid): return
	_clear()
	selected_organization = oid
	var org := _org(oid)
	if not standalone:
		var back := Button.new()
		back.name = "BackToOrganizations"
		back.text = "‹ Back to organizations"
		back.pressed.connect(show_list)
		add_child(back)
	add_child(_text(_org_name(oid), 20, Style.HEADING_COLOR))
	add_child(_text(Rules.TYPES[str(org["type"])], 13, Style.ACCENT_COLOR))
	add_child(_text("Headquarters: " + Rules.hq_label(org, world.countries)))
	if not str(org.get("leader", "")).is_empty(): add_child(_text("Leader: " + str(world.countries.get(org["leader"], {}).get("name", org["leader"]))))
	if not str(org.get("outlook_affinity", "")).is_empty(): add_child(_text("Outlook affinity: " + str(org["outlook_affinity"]).replace("_", " ").capitalize()))
	if org.has("purpose"): add_child(_text(org["purpose"], 13, Style.GOLD_COLOR))
	if not world.organizations.has(oid):
		add_child(_text("Inactive definition. Starting memberships and statuses require review before this organization can operate.", 13, Style.GOLD_COLOR))
		if not str(org.get("founded", "")).is_empty(): add_child(_text("Founding / entry-into-force date: " + org["founded"]))
	else:
		var map_button := Button.new()
		map_button.name = "ShowOrganizationMap"
		map_button.text = "Show organization on map"
		map_button.pressed.connect(func(): host._open_organization(oid))
		add_child(map_button)
	detail_tabs = TabContainer.new()
	detail_tabs.name = "OrganizationDetails"
	detail_tabs.add_theme_stylebox_override("panel", Style.button(Style.PANEL_COLOR))
	var tab_bar := detail_tabs.get_tab_bar()
	tab_bar.add_theme_stylebox_override("tab_selected", Style.button(Color("294655")))
	tab_bar.add_theme_stylebox_override("tab_unselected", Style.button(Color("0e202e")))
	tab_bar.add_theme_color_override("font_selected_color", Style.GOLD_COLOR)
	# The outer country panel owns vertical scrolling; no nested wheel trap.
	detail_tabs.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	add_child(detail_tabs)
	var members := VBoxContainer.new()
	members.name = "Members"
	members.add_theme_constant_override("separation", 6)
	detail_tabs.add_child(members)
	var counts := Rules.full_members(org).size()
	members.add_child(_text("%d full members · %d other memberships" % [counts, org["members"].size() - counts]))
	if org.has("membership_note"): members.add_child(_text(org["membership_note"], 12))
	var tags: Array = org["members"].duplicate()
	tags.sort_custom(func(a: String, b: String): return world.countries[a]["name"].naturalnocasecmp_to(world.countries[b]["name"]) < 0)
	for tag: String in tags:
		var button := Button.new()
		button.name = "Member_" + tag
		var country: Dictionary = world.countries[tag]
		button.icon = host.flags.resolve(tag, str(country.get("cosmetic", "")), str(country["outlook"]))
		button.expand_icon = true
		button.add_theme_constant_override("icon_max_width", 28)
		button.custom_minimum_size.y = 34
		button.text = str(world.countries[tag]["name"]) + " · " + Rules.status(org, tag).capitalize()
		button.alignment = HORIZONTAL_ALIGNMENT_LEFT
		button.clip_text = true
		button.tooltip_text = button.text
		button.pressed.connect(func(): host._show_country(tag, true))
		members.add_child(button)
		member_buttons[tag] = button
	var features := VBoxContainer.new()
	features.name = "Features"
	features.add_theme_constant_override("separation", 10)
	detail_tabs.add_child(features)
	for feature: Dictionary in Rules.features(org):
		features.add_child(_text(str(feature["name"]) + (" · Planned" if feature["planned"] else ""), 14, Style.GOLD_COLOR))
		features.add_child(_text(feature["text"]))
	for action: String in ["Membership changes", "Proposals and votes"]:
		var button := Button.new()
		button.text = action + " · Planned"
		button.disabled = true
		button.tooltip_text = "Diplomatic actions and agreement rules are not implemented yet."
		features.add_child(button)
