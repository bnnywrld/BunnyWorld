extends VBoxContainer
const Style = preload("res://scripts/ui_style.gd")
var host: Control
var model: RefCounted
var summary: Label
var selected_info: Label
var queue_rows: VBoxContainer
var building_buttons: Dictionary = {}
var page := 0
var page_label: Label
var selected_building: Label
var last_revision := -1
var manufactured_box: Label

func configure(main: Control) -> void:
	name = "ConstructionPanel"
	host = main
	model = host.state.construction
	add_theme_constant_override("separation", 8)
	summary = _label("", 13, Style.GOLD_COLOR)
	summary.tooltip_text = "Civilian industries provide construction work in proportion to their staffing."
	add_child(summary)
	add_child(_label("Select a building, then click one of your states. Yellow stripes mark queued construction.", 12))
	selected_info = _label("", 12)
	add_child(selected_info)
	add_child(HSeparator.new())
	var columns := HBoxContainer.new()
	columns.add_theme_constant_override("separation", 10)
	add_child(columns)
	var left := VBoxContainer.new()
	left.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	columns.add_child(left)
	var goods_frame := PanelContainer.new()
	goods_frame.name = "ManufacturedGoods"
	goods_frame.add_theme_stylebox_override("panel",Style.panel(Color("1d3947"),4,Style.GOLD_COLOR))
	left.add_child(goods_frame)
	manufactured_box = _label("",14,Style.GOLD_COLOR)
	goods_frame.add_child(manufactured_box)
	left.add_child(_label("CONSTRUCTION QUEUE", 13, Style.ACCENT_COLOR))
	var pager := HBoxContainer.new()
	left.add_child(pager)
	pager.add_child(_button("‹", func(): page = maxi(0, page-1); refresh()))
	page_label = _label("", 12)
	page_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	pager.add_child(page_label)
	pager.add_child(_button("›", func(): page = mini(maxi(0, (model.queue.size()-1)/30), page+1); refresh()))
	var scroll := ScrollContainer.new()
	scroll.custom_minimum_size.y = 320
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.mouse_force_pass_scroll_events = false
	left.add_child(scroll)
	queue_rows = VBoxContainer.new()
	queue_rows.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	queue_rows.add_theme_constant_override("separation", 3)
	scroll.add_child(queue_rows)
	var right := VBoxContainer.new()
	right.custom_minimum_size.x = 170
	columns.add_child(right)
	right.add_child(_label("BUILDINGS", 13, Style.ACCENT_COLOR))
	for category: String in ["Networks", "Economy", "State facilities"]:
		right.add_child(_label(category, 12, Style.GOLD_COLOR))
		var grid := GridContainer.new()
		grid.columns = 3
		right.add_child(grid)
		for key: String in model.catalog:
			var data: Dictionary = model.catalog[key]
			if data["category"] != category: continue
			var button := _button(abbreviation(key), func(): host._select_construction_building(key))
			button.name = "Build_" + key
			button.custom_minimum_size = Vector2(52, 40)
			button.toggle_mode = true
			button.tooltip_text = "%s\n%s · %s\nConstruction: %.0f points + %.0f per existing/queued level\nMaximum: %d per state%s\nAnnual GDP gain on completion: %s\nClick a state to queue one level." % [data["name"],money(data["money_usd"]),"Shared slot" if data["shared"] else "Separate slots",data["points"],data["extra_points"],data["max_level"]," · coastal only" if data["coastal"] else "",money(model.gdp_gain(host.state.player_country, key))]
			var workers := int(host.state.state_economy["workers_per_level"].get(key, 0))
			if workers > 0: button.tooltip_text += "\nEmployees required per level: " + preload("res://scripts/display_format.gd").people(workers) + "\nOutput scales with staffing. Existing unemployment is preserved."
			grid.add_child(button)
			building_buttons[key] = button
	selected_building = _label("", 12, Style.GOLD_COLOR)
	right.add_child(selected_building)
	right.add_child(_label("Networks use separate slots: Infrastructure, Internet and Railroads each allow 10 levels.", 11))
	refresh()

func abbreviation(key: String) -> String:
	return {"data_center":"DATA","industrial_complex":"CIV","arms_factory":"MIL","dockyard":"NAV","offices":"OFF","agriculture_district":"AGR","microchip_plant":"CHIP","composite_plant":"COMP","synthetic_refinery":"SYN","fossil_powerplant":"FOSS","nuclear_reactor":"NUC","renewable_energy_infra":"REN","infrastructure":"INF","internet_station":"NET","rail_terminal":"RAIL","air_base":"AIR","anti_air_building":"SAM","radar_station":"RAD","fuel_silo":"RES","rocket_site":"MSL","energy_infrastructure":"GRID","industrial_infrastructure":"CAP","enrichment_facility":"ENR"}.get(key, key.left(3).to_upper())

func _label(text: String, size: int = 12, color: Color = Style.MUTED_COLOR) -> Label:
	var label := Style.label(text, size, color)
	label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	return label

func _button(text: String, action: Callable) -> Button:
	var button := Button.new()
	button.text = text
	button.pressed.connect(action)
	return button

static func money(amount: float) -> String:
	if absf(amount) >= 1e9: return "$%.2fB" % (amount/1e9)
	if absf(amount) >= 1e6: return "$%.1fM" % (amount/1e6)
	return "$%.0f" % amount

func refresh() -> void:
	last_revision = model.revision
	var allocations: Dictionary = model.allocations()
	var factories: int = model.factory_count(host.state.player_country)
	var goods: int = model.manufactured_factories()
	summary.text = "Factories: %d total · %d construction · %d Manufactured Goods" % [factories, factories-goods, goods]
	summary.tooltip_text = "Maximum 10 factories per project. Construction is paid upfront. Factory work scales with staffing; output settles monthly."
	var output: float = host.state.economy.ledger.get(host.state.player_country,{}).get("manufactured_goods",{}).get("produced",0)
	manufactured_box.text = "MANUFACTURED GOODS\n%d civilian factories assigned\nLast settlement · %s MU" % [goods,preload("res://scripts/display_format.gd").people(roundi(output))]
	var key: String = host.construction_building
	for id: String in building_buttons: building_buttons[id].set_pressed_no_signal(id == key)
	selected_building.text = str(model.catalog[key]["name"]) + "\n" + money(model.catalog[key]["money_usd"])
	var sid: String = host.construction_state
	selected_info.text = "Light green: more free slots · Dark green: fewer · Blue: no shared slots"
	if key in ["infrastructure", "internet_station", "rail_terminal"]: selected_info.text = "Dark blue: level 0 → Gold: level 10 · Stripes: queued levels"
	if host.state.regions.has(sid):
		var r: Dictionary = host.state.regions[sid]
		selected_info.text = "%s · %d/%d shared slots free · %s %d + %d queued / %d" % [r["name"], model.free_slots(sid),r["construction_slots"],model.catalog[key]["name"],r["buildings"].get(key,0),model.pending(sid,key),model.limit(sid,key)]
	for child: Node in queue_rows.get_children(): queue_rows.remove_child(child); child.queue_free()
	page = clampi(page, 0, maxi(0, (model.queue.size()-1)/30))
	page_label.text = "%d projects · %d/%d" % [model.queue.size(),page+1,maxi(1,ceili(model.queue.size()/30.0))]
	if model.queue.is_empty(): queue_rows.add_child(_label("No construction queued.\nChoose a building on the right and click a state."))
	for i: int in range(page*30, mini(model.queue.size(), (page+1)*30)):
		var job: Dictionary = model.queue[i]
		var id := int(job["id"])
		var state_id := str(int(job["state"]))
		var frame := PanelContainer.new()
		frame.name = "Project_%d" % id
		var compact_style := Style.button(Color("132c3a"))
		compact_style.content_margin_top = 4
		compact_style.content_margin_bottom = 4
		frame.add_theme_stylebox_override("panel",compact_style)
		queue_rows.add_child(frame)
		var content := VBoxContainer.new()
		content.add_theme_constant_override("separation", 2)
		frame.add_child(content)
		var heading := Style.label("%s ×%d · %s" % [model.catalog[job["building"]]["name"], 1+job["next_levels"].size(), host.state.regions[state_id]["name"]], 12, Style.GOLD_COLOR)
		heading.clip_text = true
		heading.tooltip_text = heading.text
		content.add_child(heading)
		var bar := ProgressBar.new()
		bar.custom_minimum_size.y = 8
		bar.value = float(job["progress"]) / float(job["points"]) * 100
		bar.show_percentage = false
		content.add_child(bar)
		var rate: float = model.rate(job, allocations[id])
		var eta := "%d days" % ceili((float(job["points"])-float(job["progress"]))/rate) if rate>0 else "Waiting / paused"
		bar.tooltip_text = "%.0f / %.0f construction points\n%.1f points/day · %s\nPaid %s upfront · cancel refund %s" % [job["progress"],job["points"],rate,eta,money(float(job["cash"])+float(job["borrowed"])),money((float(job["cash"])+float(job["borrowed"]))*(1-float(job["progress"])/float(job["points"])))]
		var future_paid := 0.0
		for level: Dictionary in job["next_levels"]: future_paid += float(level["cash"]) + float(level["borrowed"])
		bar.tooltip_text += "\n%d more level(s), paid %s; fully refunded if cancelled.\nLevels finish sequentially; ETA is for the current level." % [job["next_levels"].size(), money(future_paid)]
		var actions := HBoxContainer.new()
		actions.add_theme_constant_override("separation", 2)
		content.add_child(actions)
		actions.add_child(_label(eta, 10))
		actions.add_child(_button("−",func(): model.set_factories(id,int(job["factories"])-1); host._construction_changed()))
		actions.add_child(_label("%d/%d" % [allocations[id],job["factories"]],12,Style.ACCENT_COLOR))
		actions.add_child(_button("+",func(): model.set_factories(id,int(job["factories"])+1); host._construction_changed()))
		actions.add_child(_button("↑",func(): model.move(id,-1); host._construction_changed()))
		actions.add_child(_button("↓",func(): model.move(id,1); host._construction_changed()))
		var cancel := _button("×",func(): model.cancel(id); host._construction_changed())
		cancel.tooltip_text = "Cancel this group: refund the unfinished current level and all waiting levels; reverse corresponding borrowing first."
		actions.add_child(cancel)
		for action: Node in actions.get_children():
			if action is Button:
				action.custom_minimum_size = Vector2(22,22)
				action.add_theme_font_size_override("font_size",11)
				action.add_theme_stylebox_override("normal", Style.button(Color("142c3a")))
