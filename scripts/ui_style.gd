extends RefCounted
# Shared visual language for existing panels and every new UI surface.
const PANEL_COLOR := Color("102332")
const HEADING_COLOR := Color("f0eee2")
const MUTED_COLOR := Color("93a8aa")
const ACCENT_COLOR := Color("76c6bc")
const GOLD_COLOR := Color("e1cf9e")

static func panel(color: Color = PANEL_COLOR, radius: int = 12, border: Color = Color("223b4c")) -> StyleBoxFlat:
	var style := StyleBoxFlat.new()
	style.bg_color = color.lerp(Color("101e27"), .28)
	style.border_color = border
	style.set_border_width_all(1)
	style.set_corner_radius_all(mini(radius, 4))
	style.shadow_color = Color(0.01, 0.02, 0.025, 0.34)
	style.shadow_size = 5
	style.shadow_offset = Vector2(0, 3)
	style.content_margin_left = 16
	style.content_margin_right = 16
	style.content_margin_top = 14
	style.content_margin_bottom = 14
	return style

static func button(color: Color, radius: int = 7, border: Color = Color("294657")) -> StyleBoxFlat:
	var style := panel(color, radius, border)
	style.content_margin_left = 9
	style.content_margin_right = 9
	style.content_margin_top = 6
	style.content_margin_bottom = 6
	return style

static func label(text: String, font_size: int = 14, color: Color = HEADING_COLOR) -> Label:
	var result := Label.new()
	result.text = text
	result.add_theme_font_size_override("font_size", font_size)
	result.add_theme_color_override("font_color", color)
	return result
