extends RefCounted
const CHANGE_COST := 100.0
const PROPERTIES := [
	{"key":"constitution", "title":"Constitution", "icon":"politics", "help":"The constitutional form of the state.", "options":["Republic", "Constitutional monarchy", "Absolute monarchy"]},
	{"key":"executive", "title":"Executive system", "icon":"organizations", "help":"How executive leadership is organized.", "options":["Parliamentary", "Presidential", "Semi-presidential", "Single rule"]},
	{"key":"competition", "title":"Political competition", "icon":"population", "help":"The framework for political participation.", "options":["Competitive democracy", "Restricted competition", "One-party rule", "Closed authoritarian rule"]},
	{"key":"selection", "title":"Selection rules", "icon":"ledger", "help":"How the head of state is selected.", "options":["Direct election", "Indirect election", "Parliamentary appointment", "Hereditary succession"]},
	{"key":"power", "title":"Distribution of power", "icon":"stability", "help":"The balance of authority among governing institutions.", "options":["Legislature-led", "Balanced powers", "Executive-led", "Concentrated authority"]}
]

static func valid_choice(key: String, value: String) -> bool:
	for property: Dictionary in PROPERTIES:
		if property["key"] == key: return value in property["options"]
	return false
