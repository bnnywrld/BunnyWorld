extends RefCounted
const NAMES := ["political_power", "stability", "war_support", "treasury", "debt", "population", "politics", "economy", "diplomacy", "research", "military", "construction", "organizations", "demographics", "ledger", "globe"]
static var atlas: Texture2D
static func icon(id: String) -> Texture2D:
	if atlas == null: atlas = load("res://assets/ui/icons_020.png")
	var index := NAMES.find(id)
	if index < 0: index = 0
	var texture := AtlasTexture.new()
	texture.atlas = atlas
	texture.region = Rect2(Vector2(index % 4, floori(float(index) / 4.0)) * Vector2(atlas.get_size()) / 4.0, Vector2(atlas.get_size()) / 4.0)
	texture.filter_clip = true
	return texture
