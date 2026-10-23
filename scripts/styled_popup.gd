extends "res://scripts/briefing_frame.gd"
const Style = preload("res://scripts/ui_style.gd")
var heading: Label
var content: VBoxContainer
var close_button: Button
var title: String:
	get: return heading.text
	set(value): heading.text = value

func _init() -> void:
	name = "StyledPopup"
	z_index = 80
	mouse_filter = Control.MOUSE_FILTER_STOP
	mouse_force_pass_scroll_events = false
	add_theme_stylebox_override("panel", Style.panel())
	var layout := VBoxContainer.new()
	layout.add_theme_constant_override("separation", 10)
	add_child(layout)
	var header := HBoxContainer.new()
	layout.add_child(header)
	heading = Style.label("", 18)
	heading.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	heading.clip_text = true
	heading.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
	header.add_child(heading)
	close_button = Button.new()
	close_button.name = "Close"
	close_button.text = "×"
	close_button.tooltip_text = "Close · Escape"
	close_button.custom_minimum_size = Vector2(30, 30)
	close_button.pressed.connect(hide)
	header.add_child(close_button)
	layout.add_child(HSeparator.new())
	content = VBoxContainer.new()
	content.size_flags_vertical = Control.SIZE_EXPAND_FILL
	content.add_theme_constant_override("separation", 8)
	layout.add_child(content)
	hide()

func _ready() -> void:
	add_to_group("floating_ui")
	get_viewport().size_changed.connect(_clamp_to_viewport)

func show_beside(anchor: Rect2, preferred_size: Vector2 = Vector2(370, 0)) -> void:
	_fit(preferred_size)
	position = Vector2(anchor.end.x + 10, anchor.position.y)
	if position.x + size.x > get_viewport_rect().end.x - 12:
		position.x = anchor.position.x - size.x - 10
	show()
	_clamp_to_viewport()

func show_centered(preferred_size: Vector2) -> void:
	_fit(preferred_size)
	position = (get_viewport_rect().size - size) / 2.0
	show()
	_clamp_to_viewport()

func _fit(preferred_size: Vector2) -> void:
	reset_size()
	size = preferred_size.max(get_combined_minimum_size()).min(get_viewport_rect().size - Vector2(24, 24))

func _clamp_to_viewport() -> void:
	if not visible: return
	var bounds := get_viewport_rect().size
	size = size.min(bounds - Vector2(24,24))
	position = position.clamp(Vector2(12, 12), (bounds - size - Vector2(12, 12)).max(Vector2(12, 12)))

func _input(event: InputEvent) -> void:
	if not visible: return
	# Outside clicks dismiss without consuming the event, allowing a different
	# law/institution button to open its own content on the very same click.
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		if not get_global_rect().has_point(event.position): hide()
