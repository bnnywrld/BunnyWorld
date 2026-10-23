extends VBoxContainer
const Style = preload("res://scripts/ui_style.gd")
const Progress = preload("res://scripts/progress_button.gd")
var world: RefCounted
func configure(state: RefCounted) -> void:
	world = state
	name = "AgendaPanel"
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	add_theme_constant_override("separation", 8)
	world.agenda.changed.connect(refresh)
	refresh()
func refresh() -> void:
	for child: Node in get_children():
		remove_child(child)
		child.queue_free()
	if world.agenda.queue.is_empty():
		add_child(Style.label("No reforms on the agenda", 14, Style.MUTED_COLOR))
		return
	add_child(Style.label("GOVERNMENT AGENDA", 13, Style.ACCENT_COLOR))
	for index: int in world.agenda.queue.size():
		var item: Dictionary = world.agenda.queue[index]
		var card := Progress.new()
		card.name = "Reform_%s" % item["key"]
		card.custom_minimum_size.y = 72
		card.alignment = HORIZONTAL_ALIGNMENT_LEFT
		card.add_theme_font_size_override("font_size", 13)
		card.text = "%s · %s\n%s → %s\n%d days %s" % [world.agenda.title(item), "In progress" if index == 0 else "Queued", item["from"], item["value"], item["days"] - item["elapsed"], "remaining" if index == 0 else "duration"]
		card.tooltip_text = "Political Power paid: %d PP\nReforms are completed sequentially." % item["cost"]
		add_child(card)
		card.set_progress(float(item["elapsed"]) / item["days"])
