extends RefCounted
static func status(world: RefCounted, tag: String, party_id: String) -> String:
	var government: Dictionary = world.political_leaders.get("countries",{}).get(tag,{})
	if government.get("ruling_party","") == party_id: return "Ruling party"
	if party_id in government.get("coalition",[]): return "Government coalition"
	return ""
static func caption(world: RefCounted, tag: String) -> String:
	var names: PackedStringArray = []
	var leader := ""
	for party: Dictionary in world.society.parties(tag):
		var role := status(world,tag,party["id"])
		if role == "Ruling party": leader = party["name"]
		elif not role.is_empty(): names.append(party["name"])
	return "Government · " + (leader if not leader.is_empty() else "—") + ("\nCoalition · " + ", ".join(names) if not names.is_empty() else "")
