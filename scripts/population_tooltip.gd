extends PanelContainer
var world: RefCounted
var country := ""
var state_id := ""
func breakdown_bbcode() -> String:
	if world == null or not world.society.nations.has(country): return "Population"
	var base := float(world.society.rules["annual_population_growth"])
	var running := base
	var monthly := pow(1+base,1./12)-1
	var rows: Array = [{"name":"Base population growth","value":monthly}]
	for key: String in world.economy.growth_modifiers(country):
		var modifier := float(world.economy.growth_modifiers(country)[key])
		var next := pow(1+clampf(running+modifier,-.08,.04),1./12)-1
		rows.append({"name":key,"value":next-monthly})
		running += modifier;monthly = next
	var count := 0
	var change := 0
	for sid: String in world.regions:
		var region: Dictionary = world.regions[sid]
		if (not state_id.is_empty() and sid != state_id) or (state_id.is_empty() and region["owner"] != country): continue
		count += int(region["population"])
		change += maxi(-int(region["population"]),floori(int(region["population"])*monthly+float(world.society.remainders[sid])))
	var text := "[b]Population · %s[/b]\nMonthly change: [color=#%s]%s · %+.4f%%[/color]" % [preload("res://scripts/display_format.gd").people(count),"76d9a1" if change>0 else ("ef8585" if change<0 else "aab8bf"),("+" if change>=0 else "")+preload("res://scripts/display_format.gd").people(change),monthly*100]
	for row: Dictionary in rows:
		var value := float(row["value"])
		text += "\n%s: [color=#%s]%+.4f pp / month[/color]" % [row["name"],"76d9a1" if value>0 else ("ef8585" if value<0 else "aab8bf"),value*100]
	text += "\nHealthcare quality: %.1f / 100" % world.economy.nations[country]["healthcare_quality"]
	if state_id.is_empty():
		var recorded := int(world.society.nations[country]["last_growth"])
		text += "\nLast completed month: [color=#%s]%s[/color]" % ["76d9a1" if recorded>0 else ("ef8585" if recorded<0 else "aab8bf"),("+" if recorded>=0 else "")+preload("res://scripts/display_format.gd").people(recorded)]
	return text
func _make_custom_tooltip(_text: String) -> Object:
	var panel := PanelContainer.new();panel.add_theme_stylebox_override("panel",preload("res://scripts/ui_style.gd").panel())
	var label := RichTextLabel.new();label.bbcode_enabled=true;label.fit_content=true;label.scroll_active=false;label.custom_minimum_size.x=320
	label.add_theme_font_size_override("normal_font_size",12);label.text=breakdown_bbcode();panel.add_child(label)
	label.add_theme_font_size_override("bold_font_size",12)
	return panel
