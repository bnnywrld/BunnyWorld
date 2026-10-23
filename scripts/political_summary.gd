extends HBoxContainer
const Art = preload("res://scripts/political_art.gd")
var parliament: Control
var government_type: Label
var seat_caption: Label
var next_election: Label
var office_names := {}
var office_portraits := {}
var government_caption: Label

func configure(compact: bool, open_government: Callable = Callable(), title: String = "") -> void:
	name = "PoliticalSummary"
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	add_theme_constant_override("separation", 6 if compact else 12)
	add_child(_office("Head of state", compact))
	var center := VBoxContainer.new()
	center.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	center.add_theme_constant_override("separation", 2)
	add_child(center)
	government_type = _label(title, 12, Color("e1cf9e"))
	government_type.name = "GovernmentType"
	government_type.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	center.add_child(government_type)
	center.add_child(_label("PARLIAMENT", 9 if compact else 12, Color("a6c5c7")))
	parliament = Art.new()
	parliament.name = "ParliamentSeats"
	parliament.custom_minimum_size = Vector2(138, 64) if compact else Vector2(230, 132)
	parliament.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	parliament.can_activate = not open_government.is_null()
	if parliament.can_activate: parliament.activated.connect(open_government)
	parliament.tooltip_text = "Open government" if parliament.can_activate else "Parliament · 100 unassigned seats"
	center.add_child(parliament)
	if not compact:
		seat_caption = _label("100 seats", 11, Color("93a8b1"))
		center.add_child(seat_caption)
	next_election = _label("Next election · —", 9 if compact else 11, Color("93a8b1"))
	next_election.name = "NextElection"
	center.add_child(next_election)
	government_caption = _label("",9 if compact else 11,Color("e1cf9e"))
	government_caption.name = "GovernmentParties"
	government_caption.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	government_caption.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	center.add_child(government_caption)
	add_child(_office("Head of government", compact))

func configure_parties(world: RefCounted, tag: String) -> void:
	var roster: Dictionary = world.political_leaders.get("countries",{}).get(tag,{})
	for role: String in office_names:
		var person: Variant = roster.get(role)
		office_names[role].text = str(person["name"]) if person is Dictionary else "—"
		if person is Dictionary:
			office_names[role].tooltip_text = person["name"]
			office_portraits[role].tooltip_text = person["name"]
			var path := str(person.get("portrait",""))
			if not path.is_empty() and ResourceLoader.exists(path):
				var picture := TextureRect.new()
				picture.texture = load(path)
				picture.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
				picture.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
				picture.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
				office_portraits[role].add_child(picture)
	government_caption.text = preload("res://scripts/government_roster.gd").caption(world,tag)
	government_caption.tooltip_text = government_caption.text + "\nMD starting government metadata; no coalition or cabinet mechanics."
	parliament.party_seats = world.society.seat_parties(tag)
	var rows: PackedStringArray = ["Parliament · initial 2000 seat snapshot"]
	for party: Dictionary in parliament.party_seats:
		rows.append("%s · %d seats" % [party["name"], party["seats"]])
	parliament.tooltip_text = "\n".join(rows)
	if seat_caption != null:
		var total := 0
		for party: Dictionary in parliament.party_seats: total += int(party["seats"])
		seat_caption.text = "%d / 100 seats assigned" % total
	var election: Dictionary = world.state_economy.get("elections", {}).get(tag, {})
	if not election.get("allowed", false): next_election.text = "Next election · Not scheduled"
	elif not str(election.get("last", "")).is_empty() and int(election.get("frequency_months", 0)) > 0:
		var date: PackedStringArray = str(election["last"]).split(".")
		var month := int(date[0]) * 12 + int(date[1]) - 1 + int(election["frequency_months"])
		var year := month / 12
		var month_number := month % 12 + 1
		var day := mini(int(date[2]), _month_days(year, month_number))
		var timestamp := int(Time.get_unix_time_from_datetime_dict({"year":year, "month":month_number, "day":day, "hour":0, "minute":0, "second":0}))
		next_election.text = "Next election · %d %s %d" % [day, ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][month_number-1], year]
		if timestamp < world.scenario_epoch + world.hour * 3600: next_election.text += " · Due"
	next_election.tooltip_text = "MD starting election schedule. Elections are not simulated yet; this date does not imply a new election has occurred."
	parliament.queue_redraw()

static func _month_days(year: int, month: int) -> int:
	if month == 2: return 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28
	return 30 if month in [4,6,9,11] else 31

func _office(title: String, compact: bool) -> Control:
	var box := VBoxContainer.new()
	var width := 64 if compact else 94
	box.custom_minimum_size.x = width
	box.add_theme_constant_override("separation", 3 if compact else 6)
	var role := _label(title, 9 if compact else 10, Color("9eb5bb"))
	role.custom_minimum_size = Vector2(width, 26)
	role.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	box.add_child(role)
	var portrait := Art.new()
	portrait.portrait = true
	portrait.custom_minimum_size = Vector2(46, 58) if compact else Vector2(72, 90)
	portrait.size_flags_horizontal = Control.SIZE_SHRINK_CENTER
	box.add_child(portrait)
	var person := _label("—", 10 if compact else 12, Color("e5e9e6"))
	person.custom_minimum_size.x = width
	person.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	person.mouse_filter = Control.MOUSE_FILTER_PASS
	box.add_child(person)
	var key := "head_of_state" if title == "Head of state" else "head_of_government"
	office_names[key] = person
	office_portraits[key] = portrait
	return box

func _label(text: String, font_size: int, color: Color) -> Label:
	var label := Label.new()
	label.text = text
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	label.add_theme_font_size_override("font_size", font_size)
	label.add_theme_color_override("font_color", color)
	label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return label
