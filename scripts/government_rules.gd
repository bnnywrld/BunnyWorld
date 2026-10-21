extends RefCounted
const CHANGE_COST := 100.0
const CATEGORIES := [
  {
    "title": "Core Governance",
    "keys": [
      "form_of_government",
      "executive",
      "competition",
      "election_rules",
      "power"
    ]
  },
  {
    "title": "Civil Rights",
    "keys": [
      "speech_press",
      "religion",
      "marriage",
      "abortion",
      "gender",
      "capital_punishment"
    ]
  },
  {
    "title": "Economy & Labor",
    "keys": [
      "economic_model",
      "taxation",
      "labor",
      "trade",
      "minimum_wage"
    ]
  },
  {
    "title": "Public Services",
    "keys": [
      "healthcare",
      "education",
      "welfare",
      "retirement"
    ]
  },
  {
    "title": "Defense & Foreign Policy",
    "keys": [
      "military_posture",
      "conscription",
      "intervention",
      "alliance",
      "nuclear"
    ]
  },
  {
    "title": "State & Society",
    "keys": [
      "immigration",
      "environment",
      "policing"
    ]
  }
]
const PROPERTIES := [
  {
    "key": "form_of_government",
    "title": "Form of Government",
    "help": "The constitutional form of the state.",
    "options": [
      "Republic",
      "Constitutional Monarchy",
      "Absolute Monarchy"
    ]
  },
  {
    "key": "executive",
    "title": "Executive System",
    "help": "How executive leadership is organized.",
    "options": [
      "Parliamentary",
      "Presidential",
      "Semi-Presidential",
      "Single Rule"
    ]
  },
  {
    "key": "competition",
    "title": "Political Competition",
    "help": "The framework for political participation.",
    "options": [
      "Competitive Democracy",
      "Restricted Competition",
      "One-Party Rule",
      "Closed Authoritarian Rule"
    ]
  },
  {
    "key": "election_rules",
    "title": "Election Rules",
    "help": "How national representatives are elected.",
    "options": [
      "Proportional Representation",
      "Constituency Elections",
      "Mixed Electoral System",
      "Non-Competitive Elections"
    ]
  },
  {
    "key": "power",
    "title": "Distribution of Power",
    "help": "How authority is shared among governing institutions.",
    "options": [
      "Legislature-Led",
      "Balanced Powers",
      "Executive-Led",
      "Concentrated Authority"
    ]
  },
  {
    "key": "speech_press",
    "title": "Freedom of Speech & Press",
    "help": "Protections for expression and independent media.",
    "options": [
      "Free",
      "Regulated",
      "State-Controlled"
    ]
  },
  {
    "key": "religion",
    "title": "Religious Freedom",
    "help": "The legal position of religious belief and practice.",
    "options": [
      "Freedom of Religion",
      "State Religion",
      "Restricted Religion"
    ]
  },
  {
    "key": "marriage",
    "title": "Same-Sex Marriage",
    "help": "Legal recognition of marriages between same-sex partners.",
    "options": [
      "Illegal",
      "Legal"
    ]
  },
  {
    "key": "abortion",
    "title": "Abortion Rights",
    "help": "Legal access to abortion.",
    "options": [
      "Prohibited",
      "Limited Exceptions",
      "Broadly Legal"
    ]
  },
  {
    "key": "gender",
    "title": "Gender Equality",
    "help": "Legal equality and protections against discrimination.",
    "options": [
      "Equal Rights",
      "Partial Equality",
      "Restricted Rights"
    ]
  },
  {
    "key": "capital_punishment",
    "title": "Capital Punishment",
    "help": "Whether the state permits the death penalty.",
    "options": [
      "Abolished",
      "Moratorium",
      "Permitted"
    ]
  },
  {
    "key": "economic_model",
    "title": "Economic Model",
    "help": "The balance of state and private economic ownership.",
    "options": [
      "Market Economy",
      "Mixed Economy",
      "State-Led Economy",
      "Planned Economy"
    ]
  },
  {
    "key": "taxation",
    "title": "Taxation",
    "help": "The overall tax burden.",
    "options": [
      "Low Taxes",
      "Moderate Taxes",
      "High Taxes"
    ]
  },
  {
    "key": "labor",
    "title": "Labor Rights",
    "help": "Protection for workers and collective bargaining.",
    "options": [
      "Limited Protections",
      "Balanced Protections",
      "Strong Protections"
    ]
  },
  {
    "key": "trade",
    "title": "Trade Policy",
    "help": "The openness of international trade.",
    "options": [
      "Free Trade",
      "Managed Trade",
      "Protectionism",
      "Closed Economy"
    ]
  },
  {
    "key": "minimum_wage",
    "title": "Minimum Wage",
    "help": "How minimum pay is set.",
    "options": [
      "No National Minimum",
      "Sectoral Agreements",
      "National Minimum"
    ]
  },
  {
    "key": "healthcare",
    "title": "Healthcare",
    "help": "How healthcare is funded and provided.",
    "options": [
      "Private System",
      "Mixed System",
      "Universal Public System"
    ]
  },
  {
    "key": "education",
    "title": "Education",
    "help": "The reach of publicly funded education.",
    "options": [
      "Limited Public Education",
      "Universal Schooling",
      "Broad Public Higher Education"
    ]
  },
  {
    "key": "welfare",
    "title": "Social Welfare",
    "help": "The breadth of the social safety net.",
    "options": [
      "Minimal Support",
      "Basic Safety Net",
      "Comprehensive Welfare"
    ]
  },
  {
    "key": "retirement",
    "title": "Retirement Age",
    "help": "The standard pension retirement age.",
    "options": [
      "60 Years",
      "65 Years",
      "67 Years"
    ]
  },
  {
    "key": "military_posture",
    "title": "Military Posture",
    "help": "The national approach to military force.",
    "options": [
      "Pacifist",
      "Defensive",
      "Power Projection"
    ]
  },
  {
    "key": "conscription",
    "title": "Conscription",
    "help": "How the armed forces recruit personnel.",
    "options": [
      "Volunteer Force",
      "Selective Conscription",
      "General Conscription"
    ]
  },
  {
    "key": "intervention",
    "title": "Foreign Intervention",
    "help": "The policy on overseas military operations.",
    "options": [
      "Non-Intervention",
      "Limited Intervention",
      "Active Intervention"
    ]
  },
  {
    "key": "alliance",
    "title": "Alliance Policy",
    "help": "The national approach to military alliances.",
    "options": [
      "Neutrality",
      "Flexible Partnerships",
      "Collective Defense"
    ]
  },
  {
    "key": "nuclear",
    "title": "Nuclear Weapons Policy",
    "help": "The national position on nuclear weapons.",
    "options": [
      "Non-Nuclear",
      "Nuclear Ambiguity",
      "Nuclear Deterrent"
    ]
  },
  {
    "key": "immigration",
    "title": "Immigration Policy",
    "help": "The openness of entry and permanent settlement.",
    "options": [
      "Restrictive",
      "Selective",
      "Open"
    ]
  },
  {
    "key": "environment",
    "title": "Environmental Protection",
    "help": "The strength of environmental safeguards.",
    "options": [
      "Limited Regulation",
      "Balanced Regulation",
      "Strong Protection"
    ]
  },
  {
    "key": "policing",
    "title": "Policing & Surveillance",
    "help": "The balance between public security and personal privacy.",
    "options": [
      "Civil Liberties",
      "Balanced Policing",
      "Security State"
    ]
  }
]

static func valid_choice(key: String, value: String) -> bool:
	for property: Dictionary in PROPERTIES:
		if property["key"] == key: return value in property["options"]
	return false

static func government_title(laws: Dictionary) -> String:
	var form: String = laws.get("form_of_government", "Republic")
	if form != "Republic": return form
	var competition: String = laws.get("competition", "Competitive Democracy")
	if competition == "One-Party Rule": return "One-Party Republic"
	if competition == "Closed Authoritarian Rule": return "Authoritarian Republic"
	match laws.get("executive", "Presidential"):
		"Parliamentary": return "Parliamentary Democracy"
		"Semi-Presidential": return "Semi-Presidential Republic"
		"Single Rule": return "Authoritarian Republic"
	return "Presidential Republic"
