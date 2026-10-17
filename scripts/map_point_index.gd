extends RefCounted
# Conservative broad phase for globe decorations only. Exact original
# visibility/projection tests still select every drawn city/building.
var buckets: Array[Dictionary] = []
func build(points: PackedVector3Array) -> void:
	var cells: Dictionary = {}
	for index: int in points.size():
		var n := points[index].normalized()
		var x := clampi(int((atan2(n.x,n.z)/TAU+.5)*16.0),0,15)
		var y := clampi(int(acos(clampf(n.y,-1,1))/PI*8.0),0,7)
		var cell := y*16+x
		if not cells.has(cell): cells[cell] = []
		cells[cell].append(index)
	buckets.clear()
	for indices: Array in cells.values():
		var center := Vector3.ZERO
		for index: int in indices: center += points[index].normalized()
		center = center.normalized()
		var minimum := 1.0
		for index: int in indices: minimum = minf(minimum,center.dot(points[index].normalized()))
		buckets.append({"center":center,"radius":acos(clampf(minimum,-1,1))+.00001,"indices":indices})
func candidates(local_eye: Vector3) -> Array[int]:
	var horizon := acos(clampf(1.0/maxf(local_eye.length(),1.000001),0.0,1.0))
	var direction := local_eye.normalized()
	var indices: Array[int] = []
	for bucket: Dictionary in buckets:
		if direction.dot(bucket["center"]) >= cos(minf(PI,horizon+float(bucket["radius"]))):
			for index: int in bucket["indices"]: indices.append(index)
	# Preserve original ordering, including collisions and distance-sort ties.
	indices.sort()
	return indices
