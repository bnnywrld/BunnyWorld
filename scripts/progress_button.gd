extends Button
## Native themed button with a fill below its foreground content.
var progress := 0.0
var fill: ColorRect
var caption: Label
var picture: TextureRect

func set_progress(value: float) -> void:
	progress = clampf(value, 0, 1)
	if fill == null:
		clip_contents = true
		for state: String in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color", "font_disabled_color", "icon_normal_color", "icon_hover_color", "icon_pressed_color", "icon_focus_color", "icon_disabled_color"]:
			add_theme_color_override(state, Color.TRANSPARENT)
		fill = ColorRect.new()
		fill.name = "ProgressFill"
		fill.color = Color(0.35, 0.65, 0.86, 0.48)
		fill.mouse_filter = Control.MOUSE_FILTER_IGNORE
		add_child(fill)
		var row := HBoxContainer.new()
		row.name = "Foreground"
		row.mouse_filter = Control.MOUSE_FILTER_IGNORE
		row.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		row.offset_left = 10
		row.offset_right = -10
		row.offset_top = 4
		row.offset_bottom = -4
		add_child(row)
		picture = TextureRect.new()
		picture.mouse_filter = Control.MOUSE_FILTER_IGNORE
		picture.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		picture.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		row.add_child(picture)
		caption = Label.new()
		caption.mouse_filter = Control.MOUSE_FILTER_IGNORE
		caption.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		caption.text_overrun_behavior = TextServer.OVERRUN_TRIM_ELLIPSIS
		caption.add_theme_color_override("font_color", Color("f3f6f7"))
		caption.add_theme_color_override("font_shadow_color", Color("0b1925"))
		caption.add_theme_constant_override("shadow_offset_y", 1)
		row.add_child(caption)
	fill.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	fill.anchor_right = progress
	fill.offset_left = 2
	fill.offset_right = -2 if progress > 0 else 0
	fill.offset_top = 2
	fill.offset_bottom = -2
	fill.visible = progress > 0
	caption.text = text
	caption.add_theme_font_size_override("font_size", get_theme_font_size("font_size"))
	picture.texture = icon
	picture.visible = icon != null
	picture.custom_minimum_size.x = get_theme_constant("icon_max_width") if icon != null else 0
