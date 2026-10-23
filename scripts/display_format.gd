extends RefCounted
static func people(value: int) -> String:
	var divisor := 1.0
	var suffix := ""
	if absi(value) >= 1000000000: divisor = 1e9; suffix = "B"
	elif absi(value) >= 1000000: divisor = 1e6; suffix = "M"
	elif absi(value) >= 1000: divisor = 1e3; suffix = "K"
	return ("%.2f" % (value/divisor)).trim_suffix("0").trim_suffix("0").trim_suffix(".") + suffix if divisor > 1 else str(value)
