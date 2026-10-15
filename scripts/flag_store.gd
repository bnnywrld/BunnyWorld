extends RefCounted
var catalog: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/flags.json"))
var pages: Dictionary = {}
var order: Array[int] = []
var hover_page: Texture2D
func resolve_hover(tag: String, cosmetic: String, outlook: String) -> Texture2D:
	var suffix: String = {"Western Outlook":"democratic", "Emerging Outlook":"communism", "Non-Aligned Outlook":"neutrality", "Salafist Outlook":"fascism", "Nationalist Outlook":"nationalist"}.get(outlook,"neutrality")
	var candidates: Array[String] = []
	if not cosmetic.is_empty(): candidates.append_array([cosmetic+"_"+suffix,cosmetic])
	candidates.append_array([tag+"_"+suffix,tag])
	for key: String in candidates:
		if not catalog.has(key): continue
		if hover_page==null: hover_page=load("res://assets/flags/hover.png")
		var rect: Array = catalog[key]["hover_rect"]
		var result := AtlasTexture.new()
		result.atlas=hover_page;result.region=Rect2(rect[0],rect[1],rect[2],rect[3]);result.filter_clip=true
		return result
	return null
func resolve(tag: String, cosmetic: String, outlook: String) -> Texture2D:
	var suffix: String = {"Western Outlook":"democratic", "Emerging Outlook":"communism", "Non-Aligned Outlook":"neutrality", "Salafist Outlook":"fascism", "Nationalist Outlook":"nationalist"}.get(outlook, "neutrality")
	var candidates: Array[String] = []
	if not cosmetic.is_empty(): candidates.append_array([cosmetic + "_" + suffix, cosmetic])
	candidates.append_array([tag + "_" + suffix, tag])
	for key: String in candidates:
		if not catalog.has(key): continue
		var entry: Dictionary = catalog[key]
		var page := int(entry["page"])
		if not pages.has(page):
			pages[page] = load("res://assets/flags/page_%d.png" % page)
			order.append(page)
			if order.size() > 4: pages.erase(order.pop_front())
		var result := AtlasTexture.new()
		result.atlas = pages[page]
		var rect: Array = entry["rect"]
		result.region = Rect2(rect[0], rect[1], rect[2], rect[3])
		return result
	return null
