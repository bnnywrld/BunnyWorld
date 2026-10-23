extends RefCounted
# Deterministic institution identities used as national research assignment slots.
const KNOWN := {
	"USA": ["Massachusetts Institute of Technology", "Stanford University", "California Institute of Technology", "Harvard University", "University of California, Berkeley", "Princeton University"],
	"JAP": ["University of Tokyo", "Kyoto University", "Osaka University", "Tohoku University", "Tokyo Institute of Technology"],
	"GER": ["Technical University of Munich", "Heidelberg University", "RWTH Aachen University", "Humboldt University of Berlin", "Karlsruhe University"],
	"ENG": ["University of Oxford", "University of Cambridge", "Imperial College London", "University of Edinburgh", "University of Manchester"],
	"FRA": ["École Polytechnique", "École Normale Supérieure", "Pierre and Marie Curie University", "University of Paris-Sud", "University of Strasbourg"],
	"CHI": ["Tsinghua University", "Peking University", "Fudan University", "Zhejiang University", "University of Science and Technology of China"],
	"SOV": ["Moscow State University", "Saint Petersburg State University", "Moscow Institute of Physics and Technology", "Novosibirsk State University", "Bauman Moscow State Technical University"],
	"POL": ["University of Warsaw", "Jagiellonian University", "Warsaw University of Technology"],
	"RAJ": ["Indian Institute of Science", "Indian Institute of Technology Bombay", "Indian Institute of Technology Delhi", "University of Delhi"],
	"CAN": ["University of Toronto", "McGill University", "University of British Columbia", "University of Waterloo"],
	"AST": ["University of Melbourne", "Australian National University", "University of Sydney", "University of New South Wales"],
	"KOR": ["Seoul National University", "KAIST", "Pohang University of Science and Technology", "Yonsei University", "Korea University"],
	"TAI": ["National Taiwan University", "National Tsing Hua University", "National Chiao Tung University", "National Cheng Kung University"]
}

static func for_country(world: RefCounted, tag: String) -> Array[String]:
	var result: Array[String] = []
	if KNOWN.has(tag):
		result.assign(KNOWN[tag])
		return result
	var country: Dictionary = world.countries[tag]
	var per_capita := float(country.get("starting_stats", {}).get("gdp_per_capita_usd", 0))
	var count := 4 if per_capita >= 20000 else (3 if per_capita >= 5000 else 2)
	var capital: Dictionary = world.regions.get(str(country.get("capital", 0)), {})
	var place: String = capital.get("state_capital", country["name"])
	if place.is_empty(): place = country["name"]
	var candidates := ["University of " + place, place + " Technical University", "National Research Institute", "National Academy of Sciences"]
	for index: int in count: result.append(candidates[index])
	return result
