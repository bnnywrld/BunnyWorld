extends RefCounted
const LEVELS: Array[String]=["infrastructure","internet_station","air_base","radar_station","rail_terminal","anti_air_building","stronghold_network"]
static var cache: Dictionary={}
static func slots(region: Dictionary) -> Dictionary:
 var used:=0
 for id: String in region.get("buildings",{}):
  if id not in LEVELS:used+=int(region["buildings"][id])
 var demographic:=4+int(floor(4*sqrt(maxf(0,float(region["population"]))/100000)))
 return {"used":used,"capacity":maxi(used,demographic),"population_capacity":demographic}
static func caption(id: String) -> String:return id.replace("_"," ").capitalize()
static func icon(id: String) -> Texture2D:
 if cache.has(id):return cache[id]
 var paths: Dictionary={"infrastructure":"M7 16h50M7 48h50M23 4L13 60M41 4l10 56M27 16v32M37 16v32","internet_station":"M32 58V30M17 58h30M15 18a24 24 0 0 1 34 0M23 27a13 13 0 0 1 18 0","air_base":"M6 34l23-7V8h6v19l23 7v5l-23-2v14l9 6-12-3-12 3 9-6V37L6 39Z","radar_station":"M12 11l35 31M12 11a25 25 0 0 0 35 31M29 38l-4 20M16 58h28M44 9l12-5","rail_terminal":"M15 7h34v37H15ZM21 44l-9 15M43 44l9 15M20 20h24M20 32h24M17 53h30","stronghold_network":"M8 57V27h10v8h10V23h9v12h10v-8h9v30ZM27 57V43h10v14","offices":"M14 58V6h36v52ZM23 16h3m12 0h3M23 28h3m12 0h3M23 40h3m12 0h3M29 58V49h7v9","industrial_complex":"M7 57V28l16-8v11l16-9v10l15-8v33ZM45 26V7h8v18M15 43h4m10 0h4m10 0h4","agriculture_district":"M32 59V8M32 25C11 26 12 9 12 9c17 0 20 16 20 16ZM32 40c21 0 20-16 20-16-17 0-20 16-20 16ZM32 52C11 52 12 36 12 36c17 0 20 16 20 16Z","dockyard":"M8 38h47L45 54H20ZM29 38V8h7v30M11 58c7-6 14 6 21 0s14 6 21 0","fuel_silo":"M11 18a21 10 0 0 1 42 0v32a21 10 0 0 1-42 0ZM11 18a21 10 0 0 0 42 0","microchip_plant":"M17 17h30v30H17ZM24 24h16v16H24ZM10 21h7m-7 11h7m-7 11h7M47 21h7m-7 11h7m-7 11h7M21 10v7m11-7v7m11-7v7M21 47v7m11-7v7m11-7v7","resources":"M9 32l23-23 23 23-23 23ZM20 21l24 22M20 43l24-22","nuclear_reactor":"M10 57c6-18 6-32 0-46h18c-5 14-5 28 0 46ZM36 57c6-18 6-32 0-46h18c-5 14-5 28 0 46Z"}
 var path: String=paths.get(id,paths["industrial_complex"])
 var svg: String='<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64"><path d="'+path+'" fill="none" stroke="#dbc998" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/></svg>'
 var picture:=Image.new();picture.load_svg_from_string(svg);cache[id]=ImageTexture.create_from_image(picture);return cache[id]
