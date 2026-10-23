extends VBoxContainer
const Style = preload("res://scripts/ui_style.gd")
const Resources = preload("res://scripts/resource_icons.gd")
const Format = preload("res://scripts/display_format.gd")
const EconomyUI = preload("res://scripts/economy_panel.gd")
var world: RefCounted
var country := ""
var resource := "oil"
var resource_buttons := {}
var capacity_labels := {}
var list: VBoxContainer
var search: LineEdit
func configure(state: RefCounted, tag: String) -> void:
	world=state;country=tag;name="TradePanel"
	add_theme_constant_override("separation",8)
	size_flags_horizontal=Control.SIZE_EXPAND_FILL
	add_child(Style.label(world.countries[tag]["name"],14,Style.MUTED_COLOR))
	add_child(Style.label("MONTHLY PRODUCTION & GLOBAL MARKETS",13,Style.ACCENT_COLOR))
	var columns := GridContainer.new();columns.columns=5;columns.add_theme_constant_override("h_separation",4);add_child(columns)
	for key: String in Resources.ORDER:
		var column := VBoxContainer.new();column.size_flags_horizontal=Control.SIZE_EXPAND_FILL;columns.add_child(column)
		var button := Button.new();button.name="Resource_"+key;button.text=Resources.SYMBOLS[key];button.icon=Resources.icon(key);button.expand_icon=true
		button.add_theme_constant_override("icon_max_width",24);button.add_theme_font_size_override("font_size",12);button.toggle_mode=true
		button.pressed.connect(func(): resource=key;refresh());column.add_child(button);resource_buttons[key]=button
		var label := Style.label("",10,Style.GOLD_COLOR);label.horizontal_alignment=HORIZONTAL_ALIGNMENT_CENTER;label.clip_text=true;column.add_child(label);capacity_labels[key]=label
	var note := Style.label("Automatic domestic allocation, imports and surplus exports. Quantities are MU per month; deposits remain RU capacity.",11,Style.MUTED_COLOR)
	note.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART;add_child(note)
	search=LineEdit.new();search.name="ResourceCountrySearch";search.placeholder_text="Filter trading partners";search.text_changed.connect(func(_text: String): refresh());add_child(search)
	list=VBoxContainer.new();list.name="ResourceLedger";add_child(list)
	world.economy.changed.connect(refresh)
	refresh()
func refresh() -> void:
	for child: Node in list.get_children(): list.remove_child(child);child.queue_free()
	var economy = world.economy
	for key: String in resource_buttons:
		resource_buttons[key].set_pressed_no_signal(key==resource)
		resource_buttons[key].tooltip_text=str(economy.rules["goods"][key]["name"])+"\nUnit: "+str(economy.rules["goods"][key]["unit"])+"\nGlobal price: "+EconomyUI.money(economy.prices[key])+" / MU"
		capacity_labels[key].text=Format.people(roundi(economy.ledger[country][key]["produced"]))+" MU"
	list.add_child(Style.label(economy.rules["goods"][resource]["name"],16,Style.GOLD_COLOR))
	_line("Global benchmark price",EconomyUI.money(economy.prices[resource])+" / MU")
	_line("Last settlement price",EconomyUI.money(economy.settlement_prices[resource])+" / MU")
	var row: Dictionary = economy.ledger[country][resource]
	for pair: Array in [["produced","Produced"],["demand","Demand"],["domestic","Domestic use"],["imports","Imported"],["exports","Exported"],["unmet","Unmet demand"]]:
		_line(pair[1],Format.people(roundi(row[pair[0]]))+" MU",pair[0]=="unmet" and float(row["unmet"])>.001)
	list.add_child(HSeparator.new())
	list.add_child(Style.label("AUTOMATIC TRADE PARTNERS",12,Style.ACCENT_COLOR))
	var count := 0
	for flow: Dictionary in economy.flows:
		if flow["good"] != resource or country not in [flow["buyer"],flow["seller"]]: continue
		var other: String = flow["seller"] if flow["buyer"]==country else flow["buyer"]
		var name: String = world.countries[other]["name"]
		if not search.text.is_empty() and not name.to_lower().contains(search.text.to_lower()): continue
		_line(("From " if flow["buyer"]==country else "To ")+name,Format.people(roundi(flow["quantity"]))+" MU · "+EconomyUI.money(flow["value"]))
		count+=1
	if count==0: list.add_child(Style.label("No matching trade flows",12,Style.MUTED_COLOR))
	var planned := Style.label("Manual deals, embargoes, transport and organization agreements · Planned",11,Style.MUTED_COLOR);planned.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART;list.add_child(planned)
func _line(key: String,value: String,negative: bool=false) -> void:
	var row := HBoxContainer.new();list.add_child(row)
	var label := Style.label(key,12,Style.MUTED_COLOR);label.size_flags_horizontal=Control.SIZE_EXPAND_FILL;label.clip_text=true;row.add_child(label)
	row.add_child(Style.label(value,12,Color("ef8585") if negative else Style.GOLD_COLOR))
