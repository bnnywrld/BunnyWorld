extends RefCounted
const ORDER := ["oil","steel","aluminium","tungsten","chromium","rubber","microchips","composites","food","manufactured_goods"]
const NAMES := {"oil":"Fossil fuels","steel":"Steel","aluminium":"Light metals","tungsten":"Technology metals","chromium":"Precious metals","rubber":"Rubber","microchips":"Microchips","composites":"Advanced Composites","food":"Food","manufactured_goods":"Manufactured Goods"}
const SYMBOLS := {"oil":"F","steel":"Fe","aluminium":"Al","tungsten":"Si","chromium":"Au","rubber":"R","microchips":"IC","composites":"C","food":"Fd","manufactured_goods":"MG"}
static var cache := {}
static func amount(value: float) -> String:
	if value > 0 and value < .01: return "<0.01 RU"
	return ("%.2f" % value).trim_suffix("0").trim_suffix("0").trim_suffix(".") + " RU"
static func tooltip(key: String, value: float = -1) -> String:
	return str(NAMES[key]) + (" · %.6f RU" % value if value >= 0 else "") + "\nResource units (RU): 1 RU = 1 MD source capacity point.\nCapacity is not tonnes, a stockpile or current extraction."
static func icon(key: String) -> Texture2D:
	if cache.has(key): return cache[key]
	var paths := {"food":"M32 58V9M32 24C10 24 12 7 12 7c18 1 20 17 20 17ZM32 41c20-1 20-18 20-18-19 0-20 18-20 18Z","manufactured_goods":"M7 58V27l17-9v13l16-9v10l17-8v34ZM45 25V6h9v18M16 43h7m9 0h7m8 0h5","oil":"M32 5C23 20 12 31 12 40a20 20 0 0 0 40 0C52 31 41 20 32 5Z","steel":"M8 12h48v10H40v20h16v10H8V42h16V22H8Z","aluminium":"M8 43l9-24h30l9 24-10 9H18ZM8 43h48","tungsten":"M8 45l9-28h30l9 28-24 13ZM17 17l15 41 15-41M8 45h48","chromium":"M8 43l11-23h26l11 23-10 9H18ZM8 43h48","rubber":"M10 32a22 22 0 1 0 44 0 22 22 0 1 0-44 0M21 32a11 11 0 1 0 22 0 11 11 0 1 0-22 0","microchips":"M14 14h36v36H14ZM6 20h8m-8 12h8m-8 12h8M50 20h8m-8 12h8m-8 12h8M20 6v8m12-8v8m12-8v8M20 50v8m12-8v8m12-8v8","composites":"M10 13h44v38H10ZM10 25h44M10 38h44M24 13v38M40 13v38"}
	var picture := Image.new()
	picture.load_svg_from_string('<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64"><path d="%s" stroke="#dbc998" stroke-width="3" fill="none" stroke-linejoin="round"/></svg>' % paths.get(key,paths["steel"]))
	cache[key] = ImageTexture.create_from_image(picture)
	return cache[key]
