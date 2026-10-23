extends Control
const Style = preload("res://scripts/ui_style.gd")
var host: Control
var frame: PanelContainer
var arrow: Button
var collapsed := false
var action_rows: VBoxContainer
var action_filter: OptionButton
var entries: Dictionary = {}

func configure(game: Control) -> void:
	host = game
	name = "DiplomacyActions"
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	z_index = 4
	frame = preload("res://scripts/briefing_frame.gd").new()
	frame.add_theme_stylebox_override("panel", Style.panel())
	frame.mouse_force_pass_scroll_events = false
	add_child(frame)
	var content := VBoxContainer.new()
	content.add_theme_constant_override("separation", 4)
	frame.add_child(content)
	content.add_child(Style.label("DIPLOMATIC ACTIONS", 12, Style.GOLD_COLOR))
	entries = host.state.state_economy["diplomatic_actions"]
	action_filter = OptionButton.new()
	action_filter.name = "ActionCategory"
	for caption: String in ["All actions", "Relations", "Military", "Economy", "Space"]: action_filter.add_item(caption)
	action_filter.item_selected.connect(func(_index: int): _refresh_actions())
	content.add_child(action_filter)
	var scroll := ScrollContainer.new()
	scroll.name = "ActionScroll"
	scroll.custom_minimum_size = Vector2(190, 150)
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.mouse_force_pass_scroll_events = false
	content.add_child(scroll)
	action_rows = VBoxContainer.new()
	action_rows.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	action_rows.add_theme_constant_override("separation", 3)
	scroll.add_child(action_rows)
	_refresh_actions()
	arrow = Button.new()
	arrow.custom_minimum_size = Vector2(26,34)
	arrow.pressed.connect(func(): collapsed = not collapsed; layout())
	add_child(arrow)
	layout()

static func category(id: String) -> String:
	for token: String in ["gnss", "_com_", "_spy_"]:
		if token in id: return "Space"
	for token: String in ["trade", "investment", "subsid", "debt", "energy", "material", "embargo", "license", "economic_aid", "exploitation"]:
		if token in id: return "Economy"
	for token: String in ["war", "peace", "access", "docking", "faction", "force", "volunteer", "attache", "lease", "military"]:
		if token in id: return "Military"
	return "Relations"

func _refresh_actions() -> void:
	for child: Node in action_rows.get_children(): action_rows.remove_child(child); child.queue_free()
	var ids := entries.keys()
	ids.sort_custom(func(a: String, b: String): return str(entries[a]["name"]).naturalnocasecmp_to(str(entries[b]["name"])) < 0)
	var selected := action_filter.get_item_text(action_filter.selected)
	for id: String in ids:
		if selected != "All actions" and category(id) != selected: continue
		var button := Button.new()
		button.name = "Action_" + id
		button.text = entries[id]["name"]
		button.disabled = true
		button.clip_text = true
		button.tooltip_text = str(entries[id]["name"]) + "\nPlanned · no cost or effect"
		button.add_theme_font_size_override("font_size", 11)
		button.custom_minimum_size = Vector2(175, 28)
		action_rows.add_child(button)

func layout() -> void:
	if host == null: return
	visible = host.control_panel.visible and host.active_feature.is_empty() and host.state.selected_country == host.diplomacy_country
	position = Vector2(host.control_panel.get_rect().end.x + 4, host.control_panel.position.y + 66)
	frame.visible = not collapsed
	frame.size = Vector2(225, minf(480, host.get_viewport_rect().size.y - position.y - 16))
	arrow.position = Vector2(0 if collapsed else 228, 0)
	arrow.text = "›" if collapsed else "‹"
	arrow.tooltip_text = "Show diplomatic actions" if collapsed else "Hide diplomatic actions"
