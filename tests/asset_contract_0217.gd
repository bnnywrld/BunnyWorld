extends SceneTree
func _initialize() -> void:
 var main_script=load("res://scripts/main.gd");assert(main_script!=null)
 var marker_script=load("res://scripts/tiny_state_markers.gd");assert(marker_script!=null)
 var shader:=ShaderMaterial.new();shader.shader=load("res://scripts/planet.gdshader")
 var coverage=load("res://scripts/display_coverage.gd").new();coverage.initialize(shader)
 for pair: Array in [[1813,4686],[1569,5469],[253,3096],[1811,4656]]:coverage.select(pair[0],pair[1]);assert(bool(shader.get_shader_parameter("state_coverage_enabled")))
 assert(coverage.pack.get_path().ends_with("selection_distance_0217.bwd"))
 for kind: String in ["land","province"]:
  var mesh: ArrayMesh=load("res://assets/"+kind+"_boundaries.res");assert(mesh.get_meta("geography_version")=="0.2.0.17");assert(mesh.get_meta("province_sha256")==FileAccess.get_sha256("res://data/provinces.json"))
 print("ASSET_CONTRACT_0217_PASS");quit()
