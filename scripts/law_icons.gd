extends RefCounted
# Small vector pictograms, rasterized once per displayed option; no frame processing.
const MARKS := {
	"form_of_government": '<path d="M9 30V18l15-8 15 8v12M8 32h32M11 36h26M15 21v8m9-8v8m9-8v8M8 18h32"/>',
	"executive": '<path d="M17 36V25h14v11M10 36h28M18 12h12v8H18zM12 27l12-7 12 7"/>',
	"competition": '<circle cx="16" cy="17" r="5"/><circle cx="32" cy="17" r="5"/><path d="M7 34v-6q9-10 18 0v6m0-10q12-5 16 4v6"/>',
	"election_rules": '<path d="M12 23h24l3 14H9zM18 24h12M16 10h16v17H16zM20 17l3 3 5-6"/>',
	"power": '<path d="M24 10v26M11 36h26M10 17h28M14 17l-6 12h12zm20 0-6 12h12z"/>',
	"speech_press": '<path d="M8 12h32v19H23l-9 7v-7H8zM14 18h20M14 24h14"/>',
	"religion": '<path d="M9 36h30M14 36V22q10-23 20 0v14M20 36v-9h8v9M24 7v8m-4-4h8"/>',
	"marriage": '<circle cx="19" cy="26" r="10"/><circle cx="30" cy="26" r="10"/><path d="m13 9 4-3 4 3-4 6zm14 0 4-3 4 3-4 6z"/>',
	"abortion": '<path d="M11 30q-4-11 7-15 5-3 10 1 12 0 10 12-1 12-14 10-9 0-13-8zM24 21v11m-5-5h10"/>',
	"gender": '<circle cx="17" cy="18" r="7"/><circle cx="31" cy="18" r="7"/><path d="M17 25v13m-5-5h10M31 25l7 10m-1-6 3 8-8-3"/>',
	"capital_punishment": '<path d="M10 37h28M15 37V10h20v6M30 16v6m-4 0h8v8h-8zM12 15l7-5"/>',
	"economic_model": '<path d="M8 36V21l10 5V15l10 7V10h10v26zM13 31h4m7 0h4m5-6h1m-1 6h1"/>',
	"taxation": '<path d="M14 8h20v31l-5-3-5 3-5-3-5 3zM20 15h9M19 22h10M19 28h7"/>',
	"labor": '<path d="m10 36 19-19m-8-8q10-5 17 4l-9 5-4-4-4-5zM10 29l7 7M26 27l10 10m-8-12 8-7"/>',
	"trade": '<path d="M7 16h31m-7-7 7 7-7 7M41 32H10m7-7-7 7 7 7"/>',
	"minimum_wage": '<circle cx="24" cy="25" r="13"/><path d="M29 18h-8v6h6v7h-8m5-17v21M9 10h30"/>',
	"healthcare": '<path d="M17 9h14v10h10v13H31v10H17V32H7V19h10z"/>',
	"education": '<path d="m6 17 18-8 18 8-18 8zM13 21v11q11 9 22 0V21m7-4v15"/>',
	"welfare": '<path d="M9 31h9l7-6q5-3 6 2l-6 6m-7-2 10 5 13-9M9 26v12M17 15q0-9 7-4 7-5 7 4 0 5-7 9-7-4-7-9z"/>',
	"retirement": '<circle cx="24" cy="23" r="15"/><path d="M24 13v11l8 5M12 38h24"/>',
	"military_posture": '<path d="m24 8 15 5v12q-3 10-15 16Q12 35 9 25V13zM24 15v18m-7-11h14"/>',
	"conscription": '<path d="M12 22q0-13 12-13t12 13M9 22h30M16 26q8 9 16 0M10 39v-4q14-11 28 0v4"/>',
	"intervention": '<path d="m8 35 28-23m-12 0h12v12M9 12h10M9 12v10M29 36h10V26M19 30l8-7"/>',
	"alliance": '<path d="m8 21 9-9 8 5 7-5 9 9-13 15-6-2L8 21zm10-2 8 7 7-6M12 28l9 10 6-3"/>',
	"nuclear": '<circle cx="24" cy="24" r="3"/><ellipse cx="24" cy="24" rx="18" ry="7"/><ellipse cx="24" cy="24" rx="18" ry="7" transform="rotate(60 24 24)"/><ellipse cx="24" cy="24" rx="18" ry="7" transform="rotate(120 24 24)"/>',
	"immigration": '<path d="M28 8h11v32H28M8 24h24m-8-8 8 8-8 8M14 10h6M14 38h6"/>',
	"environment": '<path d="M11 33Q5 10 38 9q3 27-21 28M11 40l20-23M19 31v-9m5 4h8"/>',
	"policing": '<path d="m24 8 15 6-3 17-12 10-12-10-3-17zM24 17l3 5 6 1-4 4 1 6-6-3-6 3 1-6-4-4 6-1z"/>'
}
static var cache: Dictionary = {}

static func icon(key: String, option: int) -> Texture2D:
	var id := key + str(option)
	if cache.has(id): return cache[id]
	var accents := ["#89cfc2", "#b7cce6", "#dfc38d", "#d99e99"]
	var bars := ""
	for i: int in option + 1:
		bars += '<rect x="%d" y="44" width="5" height="2" rx="1" fill="%s"/>' % [11 + i * 7, accents[option % 4]]
	var svg := '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 48 48"><g fill="none" stroke="%s" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">%s</g>%s</svg>' % [accents[option % 4], MARKS.get(key, ""), bars]
	var image := Image.new()
	image.load_svg_from_string(svg, 2.0)
	var texture := ImageTexture.create_from_image(image)
	cache[id] = texture
	return texture
