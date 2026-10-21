extends VBoxContainer
const Style = preload("res://scripts/ui_style.gd")
const FloatingPanel = preload("res://scripts/styled_popup.gd")
const Institutions = preload("res://scripts/research_institutions.gd")
const Icons = preload("res://scripts/ui_icons.gd")
var institution_buttons: Array[Button] = []
var tech_window: FloatingPanel
var tree_canvas: PanelContainer
var institution_label: Label
var active_institution := ""
var institutions: Array[String] = []

func configure(world: RefCounted, tag: String, host: Control) -> void:
	name = "ResearchPanel"
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	add_theme_constant_override("separation", 10)
	institutions = Institutions.for_country(world, tag)
	add_child(Style.label("RESEARCH INSTITUTIONS", 13, Style.ACCENT_COLOR))
	add_child(Style.label("%d available institutions" % institutions.size(), 12, Style.MUTED_COLOR))
	add_child(HSeparator.new())
	for institution: String in institutions:
		var button := Button.new()
		button.name = "Institution_%d" % institution_buttons.size()
		button.custom_minimum_size = Vector2(0, 68)
		button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		button.icon = Icons.icon("research")
		button.expand_icon = true
		button.add_theme_constant_override("icon_max_width", 36)
		button.add_theme_font_size_override("font_size", 14)
		button.alignment = HORIZONTAL_ALIGNMENT_LEFT
		button.text = institution + "\nNo research selected"
		button.clip_text = true
		button.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
		button.tooltip_text = institution + "\nOpen technology tree"
		button.pressed.connect(func(): open_tree(institution))
		add_child(button)
		institution_buttons.append(button)
	tech_window = FloatingPanel.new()
	tech_window.name = "TechnologyTree"
	tech_window.title = "Technology tree"
	host.add_child(tech_window)
	institution_label = Style.label("", 14, Style.GOLD_COLOR)
	institution_label.clip_text = true
	institution_label.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	tech_window.content.add_child(institution_label)
	tree_canvas = PanelContainer.new()
	tree_canvas.name = "EmptyTechnologyTree"
	tree_canvas.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	tree_canvas.size_flags_vertical = Control.SIZE_EXPAND_FILL
	tree_canvas.custom_minimum_size = Vector2(480, 280)
	tree_canvas.add_theme_stylebox_override("panel", Style.panel(Color("0b1c2b"), 3))
	tech_window.content.add_child(tree_canvas)

func open_tree(institution: String) -> void:
	if institution not in institutions: return
	active_institution = institution
	institution_label.text = institution
	institution_label.tooltip_text = institution
	tech_window.show_centered(Vector2(900, 570))

func _exit_tree() -> void:
	if is_instance_valid(tech_window): tech_window.queue_free()
