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
var world: RefCounted
var country := ""
var category_tabs: TabBar
var tree_scroll: ScrollContainer
var graph: Control
var tech_buttons: Dictionary = {}
var selected_category := ""
var education_quality: Label

func configure(world: RefCounted, tag: String, host: Control) -> void:
	self.world = world
	country = tag
	name = "ResearchPanel"
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	add_theme_constant_override("separation", 10)
	institutions = Institutions.for_country(world, tag)
	education_quality = Style.label("",13,Style.GOLD_COLOR)
	education_quality.name = "EducationQuality"
	education_quality.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	add_child(education_quality)
	world.economy.changed.connect(refresh)
	add_child(Style.label("RESEARCH INSTITUTIONS", 13, Style.ACCENT_COLOR))
	add_child(Style.label("%d available institutions" % institutions.size(), 12, Style.MUTED_COLOR))
	add_child(HSeparator.new())
	for institution: String in institutions:
		var button := preload("res://scripts/progress_button.gd").new()
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
	tree_canvas.name = "TechnologyTreeCanvas"
	tree_canvas.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	tree_canvas.size_flags_vertical = Control.SIZE_EXPAND_FILL
	tree_canvas.custom_minimum_size = Vector2(0, 0)
	tree_canvas.add_theme_stylebox_override("panel", Style.panel(Color("0b1c2b"), 3))
	category_tabs = TabBar.new()
	category_tabs.clip_tabs = true
	category_tabs.scrolling_enabled = true
	category_tabs.add_theme_stylebox_override("tab_selected", Style.button(Color("213b4b"), 4, Style.GOLD_COLOR))
	category_tabs.add_theme_stylebox_override("tab_unselected", Style.button(Color("102332"), 4))
	category_tabs.add_theme_stylebox_override("tab_hovered", Style.button(Color("294657"), 4))
	category_tabs.add_theme_color_override("font_selected_color", Style.GOLD_COLOR)
	category_tabs.add_theme_color_override("font_unselected_color", Style.MUTED_COLOR)
	for category: String in world.research.categories: category_tabs.add_tab(category)
	tech_window.content.add_child(category_tabs)
	category_tabs.tab_changed.connect(func(index: int): show_category(str(world.research.categories[index])))
	tech_window.content.add_child(Style.label("Oldest → newest: follow the arrows down · Scroll to explore · Hover for requirements", 12, Style.MUTED_COLOR))
	tech_window.content.add_child(tree_canvas)
	tree_scroll = ScrollContainer.new()
	tree_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	tree_scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	tree_canvas.add_child(tree_scroll)
	world.research.changed.connect(refresh)
	show_category(str(world.research.categories[0]))
	refresh()

func open_tree(institution: String) -> void:
	if institution not in institutions: return
	active_institution = institution
	institution_label.text = institution
	institution_label.tooltip_text = institution
	tech_window.show_centered(get_viewport_rect().size * Vector2(.92, .86))
	refresh()

func show_category(category: String) -> void:
	selected_category = category
	if graph != null:
		tree_scroll.remove_child(graph)
		graph.queue_free()
	graph = preload("res://scripts/technology_canvas.gd").new()
	graph.mouse_filter = Control.MOUSE_FILTER_PASS
	tree_scroll.add_child(graph)
	tech_buttons.clear()
	var techs: Dictionary = world.research.catalog
	var ids: Array = techs.keys().filter(func(key: String): return techs[key]["category"] == category)
	ids.sort_custom(func(a: String, b: String): return float(techs[a]["row"]) < float(techs[b]["row"]))
	var rows: Array = []
	for key: String in ids:
		if not rows.has(techs[key]["row"]): rows.append(techs[key]["row"])
	# MD mixes horizontal and vertical source trees. Choose the coordinate
	# least correlated with year for the branch lanes; time always runs down.
	var lane_axis := "x" if absf(_year_correlation(ids, "y")) > absf(_year_correlation(ids, "x")) else "y"
	var lanes: Array = []
	for key: String in ids:
		if not lanes.has(techs[key][lane_axis]): lanes.append(techs[key][lane_axis])
	lanes.sort()
	var occupied := {}
	var positions := {}
	var max_lane := lanes.size()
	for key: String in ids:
		var row := rows.find(techs[key]["row"])
		var lane := lanes.find(techs[key][lane_axis])
		while occupied.has(Vector2i(lane, row)): lane += 1
		occupied[Vector2i(lane, row)] = true
		max_lane = maxi(max_lane, lane + 1)
		var point := Vector2(52 + lane * 176, 16 + row * 80)
		positions[key] = point
		var button := Button.new()
		button.name = key
		button.position = point
		button.size = Vector2(160, 58)
		button.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		button.add_theme_font_size_override("font_size", 11)
		button.pressed.connect(func(): select_technology(key))
		graph.add_child(button)
		tech_buttons[key] = button
	for row: int in rows.size():
		var row_years: Array = []
		for key: String in ids:
			if techs[key]["row"] == rows[row] and not row_years.has(int(techs[key]["year"])): row_years.append(int(techs[key]["year"]))
		row_years.sort()
		var year := Style.label(str(row_years[0]), 12, Style.GOLD_COLOR)
		year.position = Vector2(6, 16 + row * 80)
		graph.add_child(year)
	for key: String in ids:
		for parent: String in techs[key]["parents"] + techs[key]["dependencies"]:
			if positions.has(parent): graph.edges.append([positions[parent] + Vector2(80, 58), positions[key] + Vector2(80, 0)])
	graph.custom_minimum_size = Vector2(60 + max_lane * 176, 24 + rows.size() * 80)
	graph.queue_redraw()
	tree_scroll.scroll_horizontal = 0
	tree_scroll.scroll_vertical = 0
	refresh()

func select_technology(tech: String) -> void:
	if world.research.start(country, active_institution, tech):
		tech_window.hide()

func _year_correlation(ids: Array, axis: String) -> float:
	var sum_year := 0.0
	var sum_axis := 0.0
	for key: String in ids:
		sum_year += float(world.research.catalog[key]["year"])
		sum_axis += float(world.research.catalog[key][axis])
	var mean_year := sum_year / maxf(1, ids.size())
	var mean_axis := sum_axis / maxf(1, ids.size())
	var covariance := 0.0
	var variance_year := 0.0
	var variance_axis := 0.0
	for key: String in ids:
		var year_delta := float(world.research.catalog[key]["year"]) - mean_year
		var axis_delta := float(world.research.catalog[key][axis]) - mean_axis
		covariance += year_delta * axis_delta
		variance_year += year_delta * year_delta
		variance_axis += axis_delta * axis_delta
	return covariance / maxf(0.00001, sqrt(variance_year * variance_axis))

func refresh() -> void:
	if world == null: return
	var n: Dictionary = world.economy.nations.get(country,{})
	if not n.is_empty():
		education_quality.text = "Education quality · %.1f / 100\nResearch speed · %.1f%% · %+.2f quality / month" % [n["education_quality"],world.economy.research_multiplier(country)*100,n["education_trend"]]
		education_quality.tooltip_text = "Education funding: %.2f%% of GDP\nFunding to sustain quality: %.2f%%\nR&D funding: %.2f%% of GDP\nChange funding in Economy → Budget. Quality adjusts gradually each month. Ahead-of-time penalties still apply." % [n["budget"]["education"],world.economy.maintenance("education",n["education_quality"]),n["budget"]["research"]]
	var research = world.research
	for i: int in institutions.size():
		var institution: String = institutions[i]
		var tech: String = research.assignments[country].get(institution, "")
		institution_buttons[i].text = institution + "\nNo research selected"
		if not tech.is_empty():
			institution_buttons[i].text = "%s\n%s · %d%% · %d days remaining" % [institution, research.catalog[tech]["name"], research.fraction(country, tech) * 100, research.remaining_days(country, tech)]
		institution_buttons[i].set_progress(0.0 if tech.is_empty() else research.fraction(country, tech))
	if not tech_window.visible: return
	for key: String in tech_buttons:
		var tech: Dictionary = research.catalog[key]
		var button: Button = tech_buttons[key]
		var reason: String = research.reason(country, key)
		var penalty: float = research.penalty(key)
		var percent: int = roundi(research.fraction(country, key) * 100)
		var status := reason if not reason.is_empty() else ("Resume · %d%%" % percent if percent > 0 else "Available")
		if status.begins_with("Researching"): status = "Researching · %d%%" % percent
		if status.begins_with("Requires"): status = "Locked"
		button.text = "%s\n%d · %s" % [tech["name"], tech["year"], status]
		button.disabled = not reason.is_empty()
		button.add_theme_stylebox_override("disabled", Style.button(Color("132c39"), 4, Style.GOLD_COLOR if reason.begins_with("Researching") else Color("294657")))
		button.add_theme_color_override("font_disabled_color", Style.GOLD_COLOR if reason.begins_with("Researching") else (Color("78b89b") if reason == "Researched" else Style.MUTED_COLOR))
		var requirements: Array[String] = []
		for parent: String in tech["parents"]: requirements.append(str(research.catalog[parent]["name"]))
		button.tooltip_text = "%s (%d)\n%s\nBase: %.0f days · Current ahead-of-time penalty: +%d%%\nRetained progress: %d%%\nNo technology effects yet." % [tech["name"], tech["year"], reason if not reason.is_empty() else "Click to research at " + active_institution, tech["days"], roundi((penalty - 1) * 100), percent]
		if not requirements.is_empty(): button.tooltip_text += "\nRequires any: " + ", ".join(requirements)
		for dependency: String in tech["dependencies"]: button.tooltip_text += "\nAlso requires: " + str(research.catalog[dependency]["name"])

func _exit_tree() -> void:
	if is_instance_valid(tech_window): tech_window.queue_free()
