extends VBoxContainer
const Style = preload("res://scripts/ui_style.gd")
const Format = preload("res://scripts/display_format.gd")
var world: RefCounted
var country := ""
var selected := "Overview"
var body: VBoxContainer
var tabs: HBoxContainer
var controls := {}
var draft := {}
var status: Label
var has_edits := false
var submitting := false
func configure(state: RefCounted, tag: String, initial: String = "Overview") -> void:
	world = state;country = tag;selected = initial
	name = "EconomyPanel"
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	add_theme_constant_override("separation",8)
	tabs = HBoxContainer.new()
	add_child(tabs)
	for caption: String in ["Overview","Budget","Production","Energy"]:
		var button := Button.new()
		button.name = caption;button.text = caption;button.toggle_mode = true
		button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		button.add_theme_font_size_override("font_size",12)
		button.pressed.connect(func(): selected=caption;has_edits=false;refresh())
		tabs.add_child(button)
	body = VBoxContainer.new();body.add_theme_constant_override("separation",7);add_child(body)
	world.economy.changed.connect(_changed)
	refresh()
func _changed() -> void:
	if submitting: return
	if selected != "Budget" or not has_edits: refresh()
func refresh() -> void:
	for child: Node in body.get_children(): body.remove_child(child);child.queue_free()
	for button: Button in tabs.get_children(): button.set_pressed_no_signal(button.text==selected)
	controls.clear()
	var n: Dictionary = world.economy.nations[country]
	if selected == "Overview":
		_heading("NATIONAL ECONOMY")
		_line("GDP · current USD",money(world.gdp(country)))
		_line("GDP · constant 2000 USD",money(world.gdp(country)/float(n["price_index"])))
		_line("Real GDP change · last month","%+.2f%%" % (float(n["real_growth"])*100),true,float(n["real_growth"]))
		_line("Productivity growth / year","%+.2f%%" % (world.economy.productivity_growth_for(country)*100))
		_line("Inflation / year","%.2f%%" % (float(n["inflation"])*100))
		_line("Productivity index","%.2f" % (float(n["productivity"])*100))
		_line("Monthly revenue",money(n["revenue"]))
		_line("Recurring monthly spending",money(n["spending"]))
		_line("Recurring monthly balance",money(n["balance"]),true,float(n["balance"]))
		_line("Upfront construction · this month",money(n["construction_paid"]))
		_line("Upfront construction · last month",money(n["construction_last_month"]))
		_line("Treasury",money(world.countries[country]["starting_stats"].get("treasury_usd",0)))
		_line("Debt",money(world.countries[country]["starting_stats"].get("debt_usd",0)))
		_line("Interest rate / year","%.2f%%" % (float(n["interest_rate"])*100))
		_line("Food availability","%.1f%%" % (100*world.economy.fulfillment(country,"food")))
		_line("Education quality","%.1f / 100" % n["education_quality"])
		_line("Healthcare quality","%.1f / 100" % n["healthcare_quality"])
		var repay := Button.new();repay.name="RepayDebt";repay.text="Repay debt · up to 1% of GDP"
		repay.pressed.connect(func(): world.economy.repay_debt(country,world.gdp(country)*.01))
		body.add_child(repay)
		_note("Monthly production, consumption, automatic trade and public finances. Export proceeds go to businesses; government receives taxes. Economic cycles, monetary policy and crises can be connected later.")
	elif selected == "Budget":
		_heading("NEXT MONTH'S BUDGET")
		_note("Changes apply at the next monthly update. Taxes respect the active Taxation law. Spending is a share of annual GDP; the monthly budget pays one twelfth.")
		draft = n["budget"].duplicate();draft.merge(n["pending"],true)
		var apply := Button.new();apply.name="ApplyBudget";apply.text="Apply next month"
		apply.pressed.connect(_apply_budget)
		body.add_child(apply)
		status = Style.label("Pending next month" if not n["pending"].is_empty() else "Current budget",12,Style.GOLD_COLOR);body.add_child(status)
		for key: String in world.economy.rules["budget"]:
			var row := HBoxContainer.new();body.add_child(row)
			var title := Style.label(key.replace("_"," ").capitalize(),12,Style.MUTED_COLOR);title.size_flags_horizontal=Control.SIZE_EXPAND_FILL;row.add_child(title)
			var input := SpinBox.new();input.name=key;input.min_value=0;input.max_value=float(world.economy.rules["budget_limits"][key]);input.step=.25;input.suffix="%"
			if key.ends_with("_tax"): input.max_value=world.economy.tax_cap(country)
			input.value=float(draft[key]);input.custom_minimum_size.x=120
			input.get_line_edit().add_theme_font_size_override("font_size",12)
			input.get_line_edit().add_theme_stylebox_override("normal",Style.button(Color("0c1d2a"),4))
			input.custom_minimum_size.y=30
			input.value_changed.connect(func(value: float): draft[key]=value;has_edits=true)
			row.add_child(input);controls[key]=input
		for kind: String in ["education","healthcare"]:
			_line(kind.capitalize()+" quality","%.1f / 100 · %+.2f / month" % [n[kind+"_quality"],n[kind+"_trend"]],true,float(n[kind+"_trend"]))
			_line("Funding to sustain this quality","%.2f%% of GDP" % world.economy.maintenance(kind,float(n[kind+"_quality"])))
		_note("Quality changes gradually. Sustained funding above maintenance raises quality; cuts lower it. Education affects research speed; healthcare affects population growth. Welfare, education and health laws retain their Agenda workflow; broader policy effects are future connections.")
	elif selected == "Production":
		_heading("PRODUCTION & CONSUMPTION")
		for key: String in world.economy.rules["goods"]:
			var row: Dictionary = world.economy.ledger[country][key]
			_line(world.economy.rules["goods"][key]["name"],Format.people(roundi(row["produced"]))+" / "+Format.people(roundi(row["demand"]))+" MU")
		_note("Produced / demand each month. MU are standardized market bundles; Food uses one person's monthly food basket. Deposits remain RU capacity, with calibrated monthly extraction. Staffing and available inputs constrain production. Trade shows imports, exports and suppliers.")
	else:
		_heading("ELECTRICITY · PLANNED")
		for key: String in ["Generation","Consumption","Storage","Cross-border connections"]: _line(key,"—")
		_note("Electricity is an inactive framework. It imposes no costs, shortages or output penalties. Building energy requirements, grid sharing and computing allocation can attach later.")
func _apply_budget() -> void:
	submitting=true
	for key: String in draft: world.economy.set_budget(country,key,float(draft[key]))
	submitting=false;has_edits=false;refresh()
func _heading(text: String) -> void: body.add_child(Style.label(text,13,Style.ACCENT_COLOR))
func _note(text: String) -> void:
	var label := Style.label(text,11,Style.MUTED_COLOR);label.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART;body.add_child(label)
func _line(key: String,value: String,colored: bool=false,sign_value: float=0.) -> void:
	var row := HBoxContainer.new();body.add_child(row)
	var label := Style.label(key,12,Style.MUTED_COLOR);label.size_flags_horizontal=Control.SIZE_EXPAND_FILL;row.add_child(label)
	row.add_child(Style.label(value,12,Color("76d9a1") if colored and sign_value>0 else (Color("ef8585") if colored and sign_value<0 else Style.GOLD_COLOR)))
static func money(value: float) -> String:
	if absf(value)>=1e12: return ("−" if value<0 else "")+"$%.2fT" % (absf(value)/1e12)
	return ("−" if value<0 else "")+"$"+Format.people(roundi(absf(value)))
