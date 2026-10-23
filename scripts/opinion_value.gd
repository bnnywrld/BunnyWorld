extends Label
var world: RefCounted
var from_tag := ""
var toward_tag := ""

func breakdown_bbcode() -> String:
	var text := "[b]%s → %s[/b]\n" % [world.countries[from_tag]["name"], world.countries[toward_tag]["name"]]
	for row: Dictionary in world.opinion_breakdown(from_tag, toward_tag):
		var value := float(row["value"])
		text += "\n%s: [color=#%s]%+.1f[/color]" % [str(row["name"]).replace("[", "[lb]"), "76d9a1" if value > 0 else ("ef8585" if value < 0 else "aab8bf"), value]
	return text

func _make_custom_tooltip(_text: String) -> Object:
	var panel := PanelContainer.new()
	panel.add_theme_stylebox_override("panel", preload("res://scripts/ui_style.gd").panel())
	var label := RichTextLabel.new()
	label.bbcode_enabled = true
	label.fit_content = true
	label.scroll_active = false
	label.custom_minimum_size.x = 260
	label.add_theme_font_size_override("normal_font_size", 12)
	label.text = breakdown_bbcode()
	panel.add_child(label)
	return panel
