extends VBoxContainer
const Pie = preload("res://scripts/pie_chart.gd")
const Format = preload("res://scripts/display_format.gd")
const KEYS := ["age", "religion", "education"]
const CAPTIONS := ["Age", "Religion", "Education"]
var entry: Dictionary = {}
var selected := "age"
var changed: Callable
var state_scope := false
var page: VBoxContainer
var selectors: HBoxContainer
func configure(profile: Dictionary, initial: String, callback: Callable, is_state: bool) -> void:
	entry = profile
	selected = initial if initial in KEYS else "age"
	changed = callback
	state_scope = is_state
	add_theme_constant_override("separation", 4)
	name = "StateDemographics" if state_scope else "NationalDemographics"
	set_meta("scope", "state" if state_scope else "national")
	set_meta("population", int(entry.get("population", 0)))
	selectors = HBoxContainer.new()
	selectors.add_theme_constant_override("separation", 2)
	add_child(selectors)
	for i: int in KEYS.size():
		var key: String = KEYS[i]
		var button := Button.new()
		button.text = CAPTIONS[i]
		button.name = key
		button.add_theme_font_size_override("font_size", 11)
		button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		button.toggle_mode = true
		button.focus_mode = Control.FOCUS_NONE
		button.tooltip_text = ("State" if state_scope else "National") + " demographics · " + CAPTIONS[i]
		button.pressed.connect(func(): select_metric(key))
		selectors.add_child(button)
	page = VBoxContainer.new()
	page.add_theme_constant_override("separation", 3)
	add_child(page)
	select_metric(selected)
func label(text: String, font_size: int = 11) -> Label:
	var item := Label.new()
	item.text = text
	item.add_theme_font_size_override("font_size", font_size)
	return item
func select_metric(key: String) -> void:
	if key not in KEYS: return
	selected = key
	if changed.is_valid(): changed.call(key)
	for button: Button in selectors.get_children(): button.set_pressed_no_signal(button.name == key)
	for child: Node in page.get_children(): page.remove_child(child); child.queue_free()
	var metric: Dictionary = entry.get("metrics", {}).get(key, {"counts": {}, "denominator": 0})
	var denominator := int(metric.get("denominator", 0))
	var denom := "All residents" if key in ["age", "religion"] else ("Adults 25+" if key == "education" else "Working-age residents")
	var context := label(("State" if state_scope else "National") + " · " + denom)
	context.tooltip_text = "%s · %s people" % [entry.get("scope", ""), Format.people(denominator)]
	page.add_child(context)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 5)
	page.add_child(row)
	var pie := Control.new()
	pie.set_script(Pie)
	pie.name = "Pie"
	pie.configure(metric.get("counts", {}), key)
	pie.custom_minimum_size = Vector2(86, 86)
	pie.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(pie)
	var legend := VBoxContainer.new()
	legend.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	legend.add_theme_constant_override("separation", 2)
	row.add_child(legend)
	var counts: Dictionary = metric.get("counts", {})
	var categories: Array = counts.keys()
	categories.sort_custom(func(a: String, b: String): return int(counts[a]) > int(counts[b]))
	var descriptions: PackedStringArray = []
	var displayed := 0
	for category: String in categories:
		var count := int(counts[category])
		if count <= 0: continue
		var description := "%s: %.1f%% · %s people" % [category, float(count) / maxi(denominator, 1) * 100, Format.people(count)]
		descriptions.append(description)
		if displayed >= 5: continue
		displayed += 1
		var line := HBoxContainer.new()
		line.add_theme_constant_override("separation", 4)
		var swatch := ColorRect.new()
		swatch.color = pie.colors[category]
		swatch.custom_minimum_size = Vector2(6, 6)
		swatch.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		line.add_child(swatch)
		var text := label("%s · %.1f%% · %s" % [category, float(count) / maxi(denominator, 1) * 100, Format.people(count)])
		text.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		text.clip_text = true
		text.tooltip_text = description
		line.add_child(text)
		legend.add_child(line)
	if categories.size() > 5: legend.add_child(label("More groups: hover chart"))
	if denominator == 0: legend.add_child(label("No residents in this group"))
	pie.tooltip_text = "\n".join(descriptions) if denominator > 0 else "No residents in this group"
