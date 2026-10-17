extends RefCounted
const Icons = preload("res://scripts/ui_icons.gd")
const Demographics = preload("res://scripts/demography.gd")
const Pie = preload("res://scripts/pie_chart.gd")
var host: Control
var demographics := Demographics.new()
var indicators: Dictionary = {}
var demographic_button: Button
var toolbar: HBoxContainer
var globe: Button
var globe_value: Label
var ledger_dialog: AcceptDialog
var ledger_search: LineEdit
var ledger_table: VBoxContainer
var ledger_sort := "population"
var ledger_descending := true
var ledger_rows: Array[Dictionary] = []
var ledger_header_buttons: Dictionary = {}
var demo_dialog: AcceptDialog
var demo_scope: OptionButton
var demo_content: VBoxContainer
var demo_tag := ""
var demo_states: Array[int] = []
var tension_dialog: AcceptDialog
var feature_buttons: Dictionary = {}
const COLUMNS := ["name", "population", "gdp", "gdp_per_capita", "stability", "war_support", "states", "outlook", "debt", "treasury"]
const CAPTIONS := ["Country", "Population", "GDP", "GDP / capita", "Stability", "War support", "States", "Outlook", "Debt", "Treasury"]
const WIDTHS := [220, 120, 115, 105, 95, 125, 80, 160, 110, 110]

func number(value: int) -> String:
	return host._number(value)
func money(value: Variant) -> String:
	if value == null: return "—"
	var amount := float(value)
	if absf(amount) >= 1e12: return "$%.2fT" % (amount/1e12)
	if absf(amount) >= 1e9: return "$%.2fB" % (amount/1e9)
	if absf(amount) >= 1e6: return "$%.2fM" % (amount/1e6)
	return "$" + number(int(amount))
func compact_number(value: int) -> String:
	if abs(value) >= 1000000000: return "%.2fB" % (value / 1000000000.0)
	if abs(value) >= 1000000: return "%.1fM" % (value / 1000000.0)
	if abs(value) >= 1000: return "%.1fK" % (value / 1000.0)
	return str(value)
func compact_money(value: Variant) -> String:
	return "—" if value == null else "$" + compact_number(int(value))

func icon_button(id: String, caption: String, action: Callable, disabled: bool = false) -> Button:
	var b: Button = host._icon_button(caption + (" · Planned" if disabled else ""), Icons.icon(id), action, Vector2(38,36))
	b.disabled = disabled
	if disabled: b.modulate = Color(1,1,1,.4)
	return b
func build(main: Control) -> void:
	host = main
	toolbar = HBoxContainer.new()
	toolbar.add_theme_constant_override("separation", 3)
	host.navigation_row.add_child(toolbar)
	host.navigation_row.move_child(toolbar, 1)
	toolbar.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	for row: Array in [["politics", "Government"], ["stability", "National policies"], ["economy", "Economy"], ["research", "Research"], ["construction", "Construction"]]:
		var caption: String = row[1]
		var button := icon_button(row[0], caption, func(): host._show_feature(caption))
		button.name = "Feature_" + str(row[0])
		button.toggle_mode = true
		feature_buttons[caption] = button
		button.custom_minimum_size = Vector2(44,44)
		toolbar.add_child(button)
	var demographic_shortcut := icon_button("demographics", "Demographics · National profile", open_country_demographics)
	demographic_button = demographic_shortcut
	demographic_shortcut.toggle_mode = true
	demographic_shortcut.name = "NationalDemographicsShortcut"
	demographic_shortcut.custom_minimum_size = Vector2(44,44)
	toolbar.add_child(demographic_shortcut)
	for entry: Array in [["production", "Production"], ["diplomacy", "Diplomacy"], ["trade", "Trade"], ["military", "Military"], ["intelligence", "Intelligence"], ["space", "Space Exploration"]]:
		var texture: Texture2D = load("res://assets/ui/" + entry[0] + ".svg") if entry[0] in ["production", "trade", "intelligence", "space"] else Icons.icon(entry[0])
		var caption: String = entry[1]
		var button: Button = host._icon_button(caption, texture, func(): host._show_feature(caption), Vector2(44, 44))
		button.name = "Feature_" + str(entry[0])
		button.toggle_mode = true
		feature_buttons[caption] = button
		toolbar.add_child(button)
	toolbar.hide()
	globe = icon_button("globe", "World Tension · open wars and event history", open_tension)
	globe.custom_minimum_size = Vector2(36,34)
	host.session_controls.add_child(globe)
	host.session_controls.move_child(globe, host.session_controls.get_child_count()-2)
	var overlay := Label.new()
	globe_value = overlay
	overlay.text = "0"
	overlay.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	overlay.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	overlay.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	overlay.add_theme_color_override("font_color",Color.WHITE)
	overlay.add_theme_color_override("font_outline_color",Color("07151f"))
	overlay.add_theme_constant_override("outline_size",6)
	overlay.add_theme_font_size_override("font_size",18)
	overlay.mouse_filter = Control.MOUSE_FILTER_IGNORE
	globe.add_child(overlay)
	host.session_controls.add_child(icon_button("ledger","World Ledger",open_ledger))
	var bar: HFlowContainer = host.stats_row
	bar.add_theme_constant_override("h_separation",3)
	for entry: Array in [["political_power","Political power"],["stability","Stability"],["war_support","War support"],["treasury","Treasury"],["debt","Debt"],["population","Population"],["economy","GDP"],["economy","GDP per capita"]]:
		if entry[1] in ["Treasury", "Population"]:
			var divider := VSeparator.new()
			divider.custom_minimum_size = Vector2(4, 22)
			bar.add_child(divider)
		var cell := HBoxContainer.new()
		cell.add_theme_constant_override("separation", 4)
		cell.alignment = BoxContainer.ALIGNMENT_CENTER
		var box := PanelContainer.new()
		var style: StyleBoxFlat = host._button_style(Color("102332"), 5)
		style.content_margin_left = 4
		style.content_margin_right = 4
		style.content_margin_top = 2
		style.content_margin_bottom = 2
		box.add_theme_stylebox_override("panel", style)
		box.add_child(cell)
		var icon := TextureRect.new()
		icon.texture = Icons.icon(entry[0])
		icon.custom_minimum_size = Vector2(15,15)
		icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		cell.add_child(icon)
		var label: Label = host._label("—",13)
		label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		cell.add_child(label)
		bar.add_child(box)
		indicators[entry[1]] = {"cell": box, "label": label, "icon": icon}
	_build_ledger()
	_build_demographics()
	_build_tension()
	host._configure_overlay_layout()

func refresh_active_section() -> void:
	for caption: String in feature_buttons:
		feature_buttons[caption].set_pressed_no_signal(host.control_panel.visible and host.active_feature == caption)
	if demographic_button == null: return
	var chart: Node = host.control_details.get_node_or_null("NationalDemographics")
	demographic_button.set_pressed_no_signal(host.control_panel.visible and host.state.selected_country==host.state.player_country and chart != null and chart.visible)

func open_country_demographics() -> void:
	host.national_profile_expanded = true
	host._show_country(host.state.player_country, false)
	await host.get_tree().process_frame
	host.control_details.get_parent().ensure_control_visible(host.control_details.get_node("NationalDemographics"))

func update_bar() -> void:
	toolbar.visible = host.screen == "playing"
	host.stats_label.hide() # Retained text for existing diagnostic checks; rendered values use icons.
	var tag: String = host.state.player_country
	var c: Dictionary = host.state.countries[tag]
	var stats: Dictionary = c.get("starting_stats",{})
	var population: int = host.state.country_metrics(tag)["population"]
	var pc: Variant = stats.get("gdp_per_capita_usd")
	var gdp: Variant = null if pc == null else float(pc)*population
	var values := {"Political power":str(int(stats["political_power"])) if stats.has("political_power") else "—","Stability":"%.0f%%" % (float(stats.get("stability",.65))*100),"War support":"%.0f%%" % (float(stats.get("war_support",.5))*100),"Treasury":money(stats.get("treasury_usd")),"Debt":money(stats.get("debt_usd")),"Population":number(population),"GDP":money(gdp),"GDP per capita":money(pc)}
	for caption: String in indicators:
		var record: Dictionary = indicators[caption]
		record["label"].text = compact_number(population) if caption == "Population" else (compact_money(pc) if caption == "GDP per capita" else str(values[caption]))
		var tip: String = caption + ": " + str(values[caption])
		if caption in ["GDP", "GDP per capita"] and pc != null: tip += "\nExact: $" + number(int(gdp if caption == "GDP" else pc)) + " USD"
		if caption in ["Treasury","Debt"]:
			var key := "treasury_usd" if caption == "Treasury" else "debt_usd"
			tip += "\n" + ("$%s USD\nMD 2000 starting declaration; budget simulation comes later." % number(int(stats[key])) if stats.has(key) else "No supported starting declaration. Unknown is not zero.")
		elif caption in ["GDP","GDP per capita"]: tip += "\nMD starting GDP per capita × current resident population. USD; not a live economy."
		elif caption == "Population": tip += "\nSum of currently owned State populations. Provinces are movement tiles and unique-building sites; population belongs to States."
		else: tip += "\nStarting scenario value. Political simulation follows in later patches."
		record["cell"].tooltip_text = tip
		record["icon"].tooltip_text = tip
		record["label"].tooltip_text = tip
	globe_value.text = str(int(host.state.world_tension))

func modals_visible() -> bool:
	return ledger_dialog.visible or demo_dialog.visible or tension_dialog.visible

func _modal(title: String) -> AcceptDialog:
	var d := AcceptDialog.new()
	d.title = title
	d.exclusive = true
	host.add_child(d)
	d.confirmed.connect(host._resume_after_dialog)
	d.canceled.connect(host._resume_after_dialog)
	return d
func _popup(dialog: AcceptDialog, preferred: Vector2i) -> void:
	host._pause_for_dialog()
	dialog.popup_centered(Vector2i(mini(preferred.x,DisplayServer.window_get_size().x-70),mini(preferred.y,DisplayServer.window_get_size().y-90)))

func _build_ledger() -> void:
	ledger_dialog = _modal("World Ledger")
	var root := VBoxContainer.new()
	ledger_dialog.add_child(root)
	ledger_search = LineEdit.new()
	ledger_search.placeholder_text = "Find a country…"
	ledger_search.text_changed.connect(func(_value: String): refresh_ledger())
	root.add_child(ledger_search)
	var note: Label = host._wrapped("2000 scenario figures · Click a heading to sort · Click a country to inspect · — = unavailable",12)
	root.add_child(note)
	var scroll := ScrollContainer.new()
	scroll.custom_minimum_size = Vector2(860,420)
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	root.add_child(scroll)
	var table := VBoxContainer.new()
	table.add_theme_constant_override("separation",2)
	scroll.add_child(table)
	var headings := HBoxContainer.new()
	headings.add_theme_constant_override("separation",4)
	table.add_child(headings)
	for i: int in COLUMNS.size():
		var column: String = COLUMNS[i]
		var button: Button = host._button(CAPTIONS[i],func():
			if ledger_sort == column: ledger_descending = not ledger_descending
			else: ledger_sort = column; ledger_descending = column != "name" and column != "outlook"
			refresh_ledger())
		button.custom_minimum_size = Vector2(WIDTHS[i],30)
		button.add_theme_font_size_override("font_size",12)
		headings.add_child(button)
		ledger_header_buttons[column] = button
	ledger_table = VBoxContainer.new()
	ledger_table.add_theme_constant_override("separation",2)
	table.add_child(ledger_table)
func open_ledger() -> void:
	refresh_ledger()
	_popup(ledger_dialog,Vector2i(1260,600))
func refresh_ledger() -> void:
	ledger_rows.clear()
	var aggregates: Dictionary = {}
	for tag: String in host.state.countries: aggregates[tag] = {"population":0,"states":0}
	for region: Dictionary in host.state.regions.values():
		if aggregates.has(region["owner"]):
			aggregates[region["owner"]]["population"] += int(region["population"])
			aggregates[region["owner"]]["states"] += 1
	for tag: String in host.state.countries:
		var c: Dictionary = host.state.countries[tag]
		if not ledger_search.text.is_empty() and not ledger_search.text.to_lower() in (str(c["name"])+" "+tag).to_lower(): continue
		var stats: Dictionary = c.get("starting_stats",{})
		var pc: Variant = stats.get("gdp_per_capita_usd")
		var pop: int = aggregates[tag]["population"]
		ledger_rows.append({"tag":tag,"name":c["name"],"population":pop,"gdp":null if pc == null else float(pc)*pop,"gdp_per_capita":pc,"stability":stats.get("stability"),"war_support":stats.get("war_support"),"states":aggregates[tag]["states"],"outlook":c["outlook"],"debt":stats.get("debt_usd"),"treasury":stats.get("treasury_usd")})
	ledger_rows.sort_custom(func(a: Dictionary,b: Dictionary):
		var x: Variant = a[ledger_sort]; var y: Variant = b[ledger_sort]
		if x == null: return false if y != null else str(a["name"]) < str(b["name"])
		if y == null: return true
		if x == y: return str(a["name"]) < str(b["name"])
		if x is String: return str(x).nocasecmp_to(str(y)) > 0 if ledger_descending else str(x).nocasecmp_to(str(y)) < 0
		return float(x) > float(y) if ledger_descending else float(x) < float(y))
	for child: Node in ledger_table.get_children(): ledger_table.remove_child(child); child.queue_free()
	for i: int in COLUMNS.size(): ledger_header_buttons[COLUMNS[i]].text = CAPTIONS[i] + ((" ▼" if ledger_descending else " ▲") if ledger_sort == COLUMNS[i] else "")
	for row: Dictionary in ledger_rows:
		var line := HBoxContainer.new()
		line.add_theme_constant_override("separation",4)
		ledger_table.add_child(line)
		for i: int in COLUMNS.size():
			var key: String = COLUMNS[i]
			var value: Variant = row[key]
			if i == 0:
				var country: Dictionary = host.state.countries[row["tag"]]
				var b: Button = host._button(row["name"],func(): ledger_dialog.hide(); host._resume_after_dialog(); host._show_country(row["tag"],true))
				b.icon = host.flags.resolve(row["tag"],country.get("cosmetic",""),country["outlook"])
				b.expand_icon = true
				b.add_theme_constant_override("icon_max_width",28)
				b.add_theme_font_size_override("font_size",12)
				b.custom_minimum_size = Vector2(WIDTHS[i],28)
				b.clip_text = true
				b.tooltip_text = row["name"]+" · "+row["tag"]
				line.add_child(b)
			else:
				var caption := "—"
				if value != null:
					if key in ["gdp","gdp_per_capita","debt","treasury"]: caption = money(value)
					elif key in ["stability","war_support"]: caption = "%.0f%%" % (float(value)*100)
					elif value is String: caption = value
					else: caption = number(int(value))
				var label: Label = host._label(caption,12)
				label.custom_minimum_size = Vector2(WIDTHS[i],28)
				label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
				label.tooltip_text = CAPTIONS[i]+": "+str(value) if value != null else "Unavailable starting data"
				line.add_child(label)

func _build_demographics() -> void:
	demo_dialog = _modal("Demographics")
	var root := VBoxContainer.new()
	demo_dialog.add_child(root)
	demo_scope = OptionButton.new()
	demo_scope.item_selected.connect(func(_index: int): render_demographics())
	root.add_child(demo_scope)
	var scroll := ScrollContainer.new()
	scroll.custom_minimum_size = Vector2(940,490)
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	root.add_child(scroll)
	demo_content = VBoxContainer.new()
	demo_content.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.add_child(demo_content)
func open_demographics(tag: String, sid: int = 0) -> void:
	if not host.state.countries.has(tag): return
	demo_tag = tag
	demo_dialog.title = "Demographics · "+str(host.state.countries[tag]["name"])
	demo_scope.clear()
	demo_scope.add_item("National overview")
	demo_states.clear()
	for id: String in host.state.regions:
		if host.state.regions[id]["owner"] == tag: demo_states.append(int(id))
	demo_states.sort_custom(func(a: int,b: int): return str(host.state.regions[str(a)]["name"]) < str(host.state.regions[str(b)]["name"]))
	for id: int in demo_states: demo_scope.add_item(host.state.regions[str(id)]["name"])
	demo_scope.select(demo_states.find(sid)+1 if sid in demo_states else 0)
	render_demographics()
	_popup(demo_dialog,Vector2i(1040,720))
func render_demographics() -> void:
	for child: Node in demo_content.get_children(): demo_content.remove_child(child); child.queue_free()
	var entry: Dictionary = demographics.country_metrics(host.state,demo_tag) if demo_scope.selected == 0 else demographics.state_metrics(host.state,demo_states[demo_scope.selected-1])
	demo_content.add_child(host._label(str(entry["scope"]),20,Color("e5c888")))
	demo_content.add_child(host._label("Population: " + number(entry["population"]),14))
	var grid := GridContainer.new()
	grid.name = "DemographicCharts"
	grid.columns = 2
	grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	grid.add_theme_constant_override("h_separation",18)
	grid.add_theme_constant_override("v_separation",14)
	demo_content.add_child(grid)
	var captions := {"age":"Age", "religion":"Religion", "education":"Education"}
	for key: String in ["age","religion","education"]:
		var metric: Dictionary = entry["metrics"][key]
		var panel := PanelContainer.new()
		panel.name = key
		panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		panel.custom_minimum_size = Vector2(445,180)
		grid.add_child(panel)
		var margin := MarginContainer.new()
		for side: String in ["left","right","top","bottom"]: margin.add_theme_constant_override("margin_"+side,10)
		panel.add_child(margin)
		var page := VBoxContainer.new()
		margin.add_child(page)
		page.add_child(host._label(captions[key],17,Color("e5c888")))
		var denominator: int = metric["denominator"]
		var denom := "All residents" if key in ["age","religion"] else ("Adults 25+" if key == "education" else "Working-age residents")
		page.add_child(host._label("%s · %s" % [denom,number(denominator)],12))
		var row := HBoxContainer.new()
		row.add_theme_constant_override("separation",10)
		page.add_child(row)
		var pie := Control.new()
		pie.set_script(Pie)
		pie.configure(metric["counts"])
		pie.custom_minimum_size = Vector2(115,115)
		pie.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		row.add_child(pie)
		var legend := VBoxContainer.new()
		legend.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		legend.add_theme_constant_override("separation",3)
		row.add_child(legend)
		for category: String in metric["counts"]:
			var count: int = metric["counts"][category]
			if count == 0: continue
			var line := HBoxContainer.new()
			var swatch := ColorRect.new()
			swatch.color = pie.colors[category]
			swatch.custom_minimum_size = Vector2(8,8)
			swatch.size_flags_vertical = Control.SIZE_SHRINK_CENTER
			line.add_child(swatch)
			var label: Label = host._label("%s · %.1f%%" % [category,float(count)/maxi(denominator,1)*100],12)
			label.tooltip_text = number(count)+" people"
			line.add_child(label)
			legend.add_child(line)
		if denominator == 0: page.add_child(host._label("Population breakdown unavailable",12))

	var workforce_panel := PanelContainer.new()
	workforce_panel.name = "WorkforceFigures"
	workforce_panel.custom_minimum_size = Vector2(445,180)
	var workforce := preload("res://scripts/workforce_panel.gd").new()
	workforce.configure(entry["workforce"],demo_scope.selected>0)
	workforce_panel.add_child(workforce)
	grid.add_child(workforce_panel)

func _build_tension() -> void:
	tension_dialog = _modal("World Tension")
func open_tension() -> void:
	for child: Node in tension_dialog.get_children():
		if child is VBoxContainer: tension_dialog.remove_child(child); child.queue_free()
	var root := VBoxContainer.new()
	root.custom_minimum_size = Vector2(560,280)
	tension_dialog.add_child(root)
	root.add_child(host._label("World Tension: %d" % int(host.state.world_tension),24,Color("e5c888")))
	root.add_child(host._wrapped("0 is the gameplay starting baseline; historical tension is not reconstructed.",12))
	root.add_child(HSeparator.new())
	root.add_child(host._label("CURRENT WARS",13,Color("63c9b6")))
	root.add_child(host._wrapped("Starting wars are not modeled yet."))
	root.add_child(HSeparator.new())
	root.add_child(host._label("TENSION EVENTS",13,Color("63c9b6")))
	if host.state.tension_events.is_empty():root.add_child(host._wrapped("No tension-raising events recorded."))
	for event: Dictionary in host.state.tension_events:
		root.add_child(host._wrapped("%s · %s · +%s" % [event.get("date",""),event.get("description",""),str(event.get("increase",0))]))
	_popup(tension_dialog,Vector2i(620,420))
