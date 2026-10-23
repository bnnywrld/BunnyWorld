extends VBoxContainer
const Style = preload("res://scripts/ui_style.gd")
var host: Control
const LIFETIME_MS := 60000
var transient: Array = []
var seen := {}
var serial := 0

func configure(game: Control) -> void:
	host = game
	name = "ResearchNotifications"
	z_index = 65
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	set_anchors_and_offsets_preset(Control.PRESET_CENTER_TOP)
	offset_left = -220
	offset_right = 220
	offset_top = 86
	host.state.research.changed.connect(refresh)
	host.state.completion_notice.connect(add_notice)
	host.state.campaign_changed.connect(func(): transient.clear(); seen.clear(); refresh())
	var timer := Timer.new()
	timer.wait_time = 1
	timer.timeout.connect(expire)
	add_child(timer)
	timer.start()
	refresh()

func add_notice(kind: String, text: String) -> void:
	serial += 1
	transient.append({"id":serial,"text":kind + "\n" + text,"expires":Time.get_ticks_msec()+LIFETIME_MS})
	refresh()

func research_key(notice: Dictionary) -> String: return "%s:%s:%s" % [notice["tag"],notice["tech"],notice["hour"]]

func expire(now: int = -1) -> void:
	if now < 0: now = Time.get_ticks_msec()
	var changed := false
	for index: int in range(transient.size()-1,-1,-1):
		if int(transient[index]["expires"]) <= now: transient.remove_at(index); changed = true
	var expired: Array = []
	for notice: Dictionary in host.state.research.notifications:
		var key := research_key(notice)
		if seen.has(key) and int(seen[key]) <= now: expired.append(key)
	for key: String in expired:
		for index: int in host.state.research.notifications.size():
			if research_key(host.state.research.notifications[index]) == key:
				host.state.research.dismiss(index)
				changed = true
				break
	if changed: refresh()

func dismiss(notice: Dictionary) -> void:
	if notice.has("key"):
		for index: int in host.state.research.notifications.size():
			if research_key(host.state.research.notifications[index]) == notice["key"]:
				host.state.research.dismiss(index)
				return
	else:
		for index: int in transient.size():
			if transient[index]["id"] == notice["id"]: transient.remove_at(index); break
	refresh()

func refresh() -> void:
	for child: Node in get_children():
		if child is Timer: continue
		remove_child(child)
		child.queue_free()
	var notices: Array = []
	var active := {}
	for notice: Dictionary in host.state.research.notifications:
		var key := research_key(notice)
		active[key] = true
		if not seen.has(key): seen[key] = Time.get_ticks_msec()+LIFETIME_MS
		notices.append({"key":key,"text":"Research completed\n" + str(host.state.research.catalog[notice["tech"]]["name"]) + "\n" + str(notice["institution"])})
	for key: String in seen.keys():
		if not active.has(key): seen.erase(key)
	for notice: Dictionary in transient: notices.append({"id":notice["id"],"text":notice["text"]})
	for index: int in mini(3, notices.size()):
		var notice: Dictionary = notices[index]
		var frame := preload("res://scripts/briefing_frame.gd").new()
		frame.add_theme_stylebox_override("panel", Style.panel())
		frame.mouse_filter = Control.MOUSE_FILTER_STOP
		add_child(frame)
		var row := HBoxContainer.new()
		frame.add_child(row)
		var text := Style.label(notice["text"], 13, Style.GOLD_COLOR)
		text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		text.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_child(text)
		var close := Button.new()
		close.text = "×"
		close.tooltip_text = "Dismiss notification"
		close.pressed.connect(func(): dismiss(notice))
		row.add_child(close)
	if notices.size() > 3: add_child(Style.label("%d more completion notifications" % (notices.size() - 3), 12, Style.GOLD_COLOR))
