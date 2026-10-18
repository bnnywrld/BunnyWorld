extends PanelContainer
var world: RefCounted
var country := ""

static func value_color(value: float) -> String:
	return "76d9a1" if value > 0 else ("ef8585" if value < 0 else "aab8bf")

func breakdown_bbcode() -> String:
	var total: float = world.daily_political_power(country)
	var text := "[b]Political power[/b]  %.1f\n\nDaily gain: [color=#%s]%+.2f PP[/color]\n" % [world.political_power(country), value_color(total), total]
	for row: Dictionary in world.political_power_breakdown(country):
		var value := float(row["value"])
		text += "\n%s: [color=#%s]%+.2f[/color]" % [str(row["name"]).replace("[", "[lb]"), value_color(value), value]
	return text

func _make_custom_tooltip(_for_text: String) -> Object:
	var panel := PanelContainer.new()
	var style := StyleBoxFlat.new()
	style.bg_color = Color("102534")
	style.border_color = Color("41616c")
	style.set_border_width_all(1)
	style.set_corner_radius_all(5)
	panel.add_theme_stylebox_override("panel", style)
	var margin := MarginContainer.new()
	for side: String in ["left", "right", "top", "bottom"]: margin.add_theme_constant_override("margin_" + side, 10)
	panel.add_child(margin)
	var label := RichTextLabel.new()
	label.bbcode_enabled = true
	label.fit_content = true
	label.scroll_active = false
	label.custom_minimum_size.x = 270
	label.add_theme_font_size_override("normal_font_size", 13)
	label.text = breakdown_bbcode()
	margin.add_child(label)
	return panel
