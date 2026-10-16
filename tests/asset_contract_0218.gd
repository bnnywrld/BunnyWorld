extends SceneTree
func _initialize() -> void:
 assert(load("res://scripts/main.gd")!=null)
 var ps: Dictionary=JSON.parse_string(FileAccess.get_file_as_string("res://data/provinces.json"))
 var source=load("res://scripts/map_rendering.gd").new();source.initialize(ps)
 assert(source.region_images.size()==4 and source.membership_uploads==1)
 var material:=ShaderMaterial.new();material.shader=load("res://scripts/planet.gdshader")
 var coverage=load("res://scripts/display_coverage.gd").new();coverage.initialize(material)
 assert(material.get_shader_parameter("boundary_pairs").get_image().get_format()==Image.FORMAT_RGBA8)
 assert(material.get_shader_parameter("boundary_distance").get_image().get_format()==Image.FORMAT_RH)
 assert(not FileAccess.get_file_as_string("res://scripts/display_coverage.gd").contains("country_border_shade.bwd"))
 for pair: Array in [[1813,4655],[253,3093],[1569,5469],[1811,4656]]:coverage.select(pair[0],pair[1]);assert(coverage.last_state==pair[0])
 for key: String in coverage.cache:assert(not key.begins_with("states:")and not key.begins_with("provinces:"))
 coverage.select(0,0,72);assert(coverage.last_sea==72)
 for kind: String in ["land","province"]:
  var mesh: ArrayMesh=load("res://assets/"+kind+"_boundaries.res");assert(mesh.get_meta("province_sha256")==FileAccess.get_sha256("res://data/provinces.json"))
 print("ASSET_CONTRACT_0218_PASS");quit()
