extends VBoxContainer
const Demographics = preload("res://scripts/demography.gd")
const Pie = preload("res://scripts/pie_chart.gd")
const Format = preload("res://scripts/display_format.gd")
const FloatingPanel = preload("res://scripts/styled_popup.gd")
const Style = preload("res://scripts/ui_style.gd")
var world: RefCounted
var country := ""
var host: Control
var selected := "Population"
var tabs: HBoxContainer
var page: VBoxContainer
var party_popup: FloatingPanel
var demographics := Demographics.new()

func configure(state: RefCounted, tag: String, owner_ui: Control) -> void:
	world = state
	country = tag
	host = owner_ui
	name = "SocietyPanel"
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	add_theme_constant_override("separation", 8)
	tabs = HBoxContainer.new()
	tabs.add_theme_constant_override("separation", 3)
	add_child(tabs)
	for caption: String in ["Population", "Public Attitudes", "Political Support", "Migration"]:
		var button := Button.new()
		button.name = caption.replace(" ", "")
		button.text = caption
		button.toggle_mode = true
		button.add_theme_font_size_override("font_size", 11)
		button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		button.pressed.connect(func(): selected = caption; refresh())
		tabs.add_child(button)
	page = VBoxContainer.new()
	page.add_theme_constant_override("separation", 8)
	add_child(page)
	party_popup = FloatingPanel.new()
	party_popup.name = "SocietyPartyDetails"
	host.add_child(party_popup)
	refresh()

func _exit_tree() -> void:
	if is_instance_valid(party_popup): party_popup.queue_free()

func refresh() -> void:
	party_popup.hide()
	for button: Button in tabs.get_children(): button.set_pressed_no_signal(button.text == selected)
	for child: Node in page.get_children(): page.remove_child(child); child.queue_free()
	match selected:
		"Population": _population()
		"Public Attitudes": _attitudes()
		"Political Support": _politics()
		"Migration": _migration()

func _label(text: String, color: Color = Style.HEADING_COLOR, font_size: int = 12) -> Label:
	var label := Label.new()
	label.text = text
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	return label

func _line(key: String, value: String, tip: String = "") -> void:
	var row := HBoxContainer.new()
	row.tooltip_text = tip
	row.add_child(_label(key, Style.MUTED_COLOR))
	var amount := _label(value)
	amount.autowrap_mode = TextServer.AUTOWRAP_OFF
	amount.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	amount.size_flags_horizontal = Control.SIZE_SHRINK_END
	row.add_child(amount)
	page.add_child(row)

func _heading(text: String) -> void:
	page.add_child(_label(text, Color("76c6bc"), 13))

func _planned(text: String) -> void:
	page.add_child(_label(text + " · Planned", Style.MUTED_COLOR, 11))

func _disabled(caption: String, parent: Control = null) -> void:
	if parent == null: parent = page
	var button := Button.new()
	button.text = caption
	button.disabled = true
	button.add_theme_font_size_override("font_size", 11)
	button.tooltip_text = "Planned · no cost or effect"
	parent.add_child(button)

func _population() -> void:
	var entry := demographics.country_metrics(world, country)
	var population := int(entry["population"])
	var population_box := preload("res://scripts/population_tooltip.gd").new()
	population_box.world=world;population_box.country=country;population_box.tooltip_text="Population"
	population_box.add_child(_label("Population · " + Format.people(population)))
	page.add_child(population_box)
	_line("Annual growth", "%+.2f%%" % (100 * world.society.annual_growth_rate(country)), "Base growth plus healthcare and sustained food-shortage modifiers; compounded monthly.")
	_line("Last monthly change", ("+" if int(world.society.nations[country]["last_growth"])>=0 else "") + Format.people(int(world.society.nations[country]["last_growth"])), "Recorded at the last monthly boundary.")
	_line("Births / deaths", "— / —", "Separate birth and death accounting is planned; current growth is a single net increase.")
	var qualities: Dictionary = world.economy.nations[country]
	_line("Education quality", "%.1f / 100 · %+.2f / month" % [qualities["education_quality"],qualities["education_trend"]], "Sustained funding supports research speed and productivity.")
	_line("Healthcare quality", "%.1f / 100 · %+.2f / month" % [qualities["healthcare_quality"],qualities["healthcare_trend"]], "Sustained healthcare funding affects monthly population growth.")
	page.add_child(_label("Demographic proportions stay constant as population grows. Aging and changes in attainment or affiliation are planned.", Style.MUTED_COLOR, 11))
	var grid := GridContainer.new()
	grid.columns = 2
	grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	grid.add_theme_constant_override("h_separation", 8)
	grid.add_theme_constant_override("v_separation", 8)
	page.add_child(grid)
	for key: String in ["age", "religion", "education"]:
		var metric: Dictionary = entry["metrics"][key]
		_chart(grid, key.capitalize(), key, metric["counts"], int(metric["denominator"]), "Adults 25+" if key == "education" else "All residents")
	var workforce: Dictionary = entry["workforce"]
	_chart(grid, "Employment", "employment", {"Employed":workforce["employed"], "Unemployed":workforce["unemployed"], "Inactive":workforce["outside_labour_force"]}, int(workforce["working_age"]), "Working-age residents")
	_line("Labor force", Format.people(int(workforce["labour_force"])))
	_line("Unemployment", "%.1f%%" % (100 * float(workforce["unemployment_rate"])), "Unemployed / labor force. The employment chart uses all working-age residents.")
	page.add_child(_label("Underage: below 18 · Working age: 18 to retirement · Retired: retirement age and above. Education records completed attainment among adults 25+; missing and below-primary categories remain separate.", Style.MUTED_COLOR, 11))
	_heading("RELIGION & STATE")
	_line(world.government_property(country, "religion"), str(world.society.nations[country]["affiliation"]) if not str(world.society.nations[country]["affiliation"]).is_empty() else "—")
	var laws := Button.new()
	laws.text = "Open Religion & State law"
	laws.pressed.connect(func():
		host._show_feature("Government")
		var panel: Node = host.control_details.get_node_or_null("PoliticalPanel")
		if panel != null:
			for property: Dictionary in preload("res://scripts/government_rules.gd").PROPERTIES:
				if property["key"] == "religion": panel.open_property(property))
	page.add_child(laws)
	_disabled("Religious institutions funding · Planned")

func _chart(parent: Control, title: String, key: String, counts: Dictionary, denominator: int, basis: String) -> void:
	var card := VBoxContainer.new()
	card.name = "Chart_" + key
	card.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	card.add_child(_label(title, Color("e1cf9e"), 13))
	card.add_child(_label(basis + " · " + Format.people(denominator), Style.MUTED_COLOR, 10))
	var row := HBoxContainer.new()
	card.add_child(row)
	var pie := Pie.new()
	pie.configure(counts, key)
	pie.custom_minimum_size = Vector2(76, 76)
	row.add_child(pie)
	var legend := VBoxContainer.new()
	legend.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(legend)
	var categories := counts.keys()
	categories.sort_custom(func(a: String, b: String): return int(counts[a]) > int(counts[b]))
	var tips: PackedStringArray = []
	var shown := 0
	for category: String in categories:
		var amount := int(counts[category])
		if amount <= 0: continue
		var text := "%s · %s · %.1f%%" % [category, Format.people(amount), 100.0 * amount / maxi(1, denominator)]
		tips.append(text)
		if shown >= 5: continue
		shown += 1
		var line := HBoxContainer.new()
		var swatch := ColorRect.new()
		swatch.color = pie.colors[category]
		swatch.custom_minimum_size = Vector2(7, 7)
		swatch.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		line.add_child(swatch)
		line.add_child(_label(category + " · " + Format.people(amount), Style.HEADING_COLOR, 10))
		legend.add_child(line)
	if categories.size() > 5: legend.add_child(_label("Hover chart for all groups", Style.MUTED_COLOR, 10))
	card.tooltip_text = "\n".join(tips)
	parent.add_child(card)

func _attitudes() -> void:
	_heading("PUBLIC ATTITUDES")
	for text: String in ["Social conservatism ↔ social liberalism", "Religious influence ↔ secularism", "National identity ↔ international integration"]:
		_line(text, "—")
		var bar := ProgressBar.new()
		bar.custom_minimum_size.y = 5
		bar.show_percentage = false
		bar.modulate = Color(1, 1, 1, .3)
		bar.tooltip_text = "Planned · no starting score or trend"
		page.add_child(bar)
	_planned("Trends and causes")
	_heading("MAIN CONCERNS")
	_line("Current concerns", "—")
	page.add_child(_label("Concerns will use government approval modifiers as those systems become available. Laws and party outlook do not reset public attitudes.", Style.MUTED_COLOR))

func _politics() -> void:
	_heading("CURRENT POLITICAL SUPPORT")
	_line("Government approval / next election", "— / —")
	var totals: Dictionary = world.society.outlook_totals(country)
	for outlook: String in totals: _line(outlook, "%.1f%%" % float(totals[outlook]))
	var missing: float = world.society.unrepresented(country)
	if missing > .00001: _line("Unrepresented support", "%.1f%%" % missing, "Excluded outlooks or missing source party declarations. No votes are assigned to replacement parties.")
	page.add_child(_label(preload("res://scripts/government_roster.gd").caption(world,country), Style.GOLD_COLOR, 12))
	page.add_child(_label("Parliament: initial 2000 seat snapshot. Parties below 1% receive no seats. Ruling parties and coalitions use MD's starting metadata; no elections or coalition changes yet.", Style.MUTED_COLOR, 11))
	var parties: Array = world.society.parties(country).duplicate()
	parties.sort_custom(func(a: Dictionary, b: Dictionary): return float(a["support"]) > float(b["support"]))
	for party: Dictionary in parties:
		var support := float(world.society.nations[country]["polls"][party["id"]])
		if support <= 0: continue
		var button := Button.new()
		button.name = "Party_" + str(party["id"])
		var seats := int(world.society.nations[country]["seats"].get(party["id"], 0))
		var prefix := "" if str(party["name"]).begins_with("(") else _initials(party["name"]) + " "
		button.text = "%s%s\n%.2f%% · %d seats" % [prefix, party["name"], support, seats]
		var government_status := preload("res://scripts/government_roster.gd").status(world,country,party["id"])
		if not government_status.is_empty(): button.text += " · " + government_status
		button.alignment = HORIZONTAL_ALIGNMENT_LEFT
		button.clip_text = true
		button.custom_minimum_size.y = 42
		button.add_theme_font_size_override("font_size", 11)
		if not str(party["logo"]).is_empty(): button.icon = load(party["logo"])
		else:
			var badge := Image.create(10, 10, false, Image.FORMAT_RGBA8)
			badge.fill(Color(party["color"]))
			button.icon = ImageTexture.create_from_image(badge)
		button.tooltip_text = "%s\n%s · %.2f%% · %d seats\n%s" % [party["name"], party["outlook"], support, seats, "Generic source name" if party["generic"] else "MD country party name"]
		button.pressed.connect(func(): _party_details(party, button))
		page.add_child(button)
	var controls := HBoxContainer.new()
	page.add_child(controls)
	for action: String in ["Boost party", "Undermine party", "Outlook propaganda"]: _disabled(action + " · Planned", controls)

static func _initials(value: String) -> String:
	if value.begins_with("(") and ")" in value: return value.substr(0, value.find(")") + 1)
	var text := ""
	for word: String in value.split(" ", false):
		if text.length() >= 4: break
		text += word.substr(0, 1).to_upper()
	return "[" + text + "]"

func _party_details(party: Dictionary, anchor: Control) -> void:
	party_popup.hide()
	party_popup.title = "Party details"
	for child: Node in party_popup.content.get_children(): party_popup.content.remove_child(child); child.queue_free()
	var label := _label("%s\n%s\nSupport: %.2f%%\nSeats: %d\n%s" % [party["name"], party["outlook"], float(world.society.nations[country]["polls"][party["id"]]), int(world.society.nations[country]["seats"].get(party["id"], 0)), "Logo unavailable in supplied archive; initials shown." if str(party["logo"]).is_empty() else "MD party logo"])
	label.custom_minimum_size.x = 280
	party_popup.content.add_child(label)
	party_popup.show_beside(anchor.get_global_rect())

func _migration() -> void:
	_heading("MIGRATION")
	for text: String in ["Attractiveness", "Immigration", "Emigration", "Net flow", "Arrival capacity"]: _line(text, "—")
	_line("Immigration policy", world.government_property(country, "immigration"))
	page.add_child(_label("Migration is planned. No residents leave a state or enter an off-map pool. Future flows will be matched between origins and destinations with departure and arrival limits.", Style.MUTED_COLOR))
	_disabled("Migration breakdown · Planned")
