extends SceneTree
func _initialize() -> void:
	var icons = load("res://scripts/ui_icons.gd")
	for id: String in icons.NAMES:
		var texture = icons.icon(id)
		print(id," ",texture.region," size ",texture.get_size()," atlas ",texture.atlas.get_size())
	quit()
