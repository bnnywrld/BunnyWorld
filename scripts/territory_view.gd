extends RefCounted
const Facilities=preload("res://scripts/facility_catalog.gd")
const ResourceIcons=preload("res://scripts/resource_icons.gd")
var host: Control
func clear(box: Control) -> void:
 for c: Node in box.get_children():box.remove_child(c);c.queue_free()
func text(value: String,size: int=12,color: Color=Color("b7cacf")) -> Label:
 var n: Label=host._label(value,size,color);n.size_flags_horizontal=Control.SIZE_EXPAND_FILL;n.text_overrun_behavior=TextServer.OVERRUN_TRIM_ELLIPSIS;return n
func section(title: String,key: String) -> VBoxContainer:
 var p:=PanelContainer.new();p.name=key;p.mouse_force_pass_scroll_events=false
 var style: StyleBoxFlat=host._button_style(Color("0c1c27"),3,Color("2b4149"));style.shadow_size=0;style.content_margin_left=7;style.content_margin_right=7;style.content_margin_top=5;style.content_margin_bottom=5;p.add_theme_stylebox_override("panel",style)
 var body:=VBoxContainer.new();body.add_theme_constant_override("separation",3);p.add_child(body);body.add_child(text(title.to_upper(),10,Color("76bfb2")));host.territory_details.add_child(p);return body
func inventory(body: VBoxContainer,records: Dictionary,levels: bool) -> void:
 var grid:=GridContainer.new();grid.name="FacilityGrid";grid.set_meta("levels",levels);grid.columns=maxi(4,int((host._territory_width()-34)/(81 if levels else 59)));grid.add_theme_constant_override("h_separation",3);grid.add_theme_constant_override("v_separation",3);body.add_child(grid)
 var ids: Array=records.keys();ids.sort()
 for id: String in ids:
  if (id in Facilities.LEVELS)!=levels or int(records[id])<=0:continue
  var tile:=PanelContainer.new();tile.custom_minimum_size=Vector2(78 if levels else 54,33);tile.mouse_force_pass_scroll_events=false;tile.add_theme_stylebox_override("panel",host._button_style(Color("142b37"),2,Color("29404a")))
  var row:=HBoxContainer.new();row.add_theme_constant_override("separation",3);tile.add_child(row)
  var icon:=TextureRect.new();icon.texture=Facilities.icon(id);icon.expand_mode=TextureRect.EXPAND_IGNORE_SIZE;icon.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED;icon.custom_minimum_size=Vector2(22,26);row.add_child(icon)
  var count:=text(str(int(records[id]))+("/10" if levels else ""),11,Color("eee4cd"));count.horizontal_alignment=HORIZONTAL_ALIGNMENT_RIGHT;row.add_child(count);tile.tooltip_text=Facilities.caption(id)+": "+str(int(records[id]))+(" / 10 levels" if levels else " buildings")
  var worker_count: int=int(host.state.state_economy["workers_per_level"].get(id,0))*int(records[id])
  if worker_count>0:
   var state_id:=str(host.state.selected_region);var actual:=int(host.state.employment.states[state_id]["workers"].get(id,0))
   tile.tooltip_text+="\nEmployees: "+host.foundation.compact_number(actual)+" / "+host.foundation.compact_number(worker_count)+"\nStaffed: %.1f%%" % (100.0*actual/worker_count)
  grid.add_child(tile)
 if grid.get_child_count()==0:body.add_child(text("No recorded facilities"))
func render(main: Control) -> void:
 host=main;clear(host.territory_heading);clear(host.territory_details);host.territory_details.size_flags_vertical=Control.SIZE_SHRINK_BEGIN;host.territory_scroll.vertical_scroll_mode=ScrollContainer.SCROLL_MODE_AUTO;host.territory_scroll.scroll_vertical=0
 if host.state.selected_region<=0:host._hide_panel(host.territory_panel);return
 var r: Dictionary=host.state.regions[str(host.state.selected_region)];var before: VBoxContainer=host.details;host.details=host.territory_heading;host._selection_breadcrumb(r);host.territory_heading.add_child(text(str(r["name"]),21,Color("f0eee2")));host.details=host.territory_details
 var summary:=HBoxContainer.new();summary.name="StateSummary"
 var population:=preload("res://scripts/population_tooltip.gd").new();population.world=host.state;population.country=r["owner"];population.state_id=str(int(r["id"]));population.tooltip_text="Population";population.add_child(text(host.foundation.compact_number(r["population"])+" residents",17,Color("eee4cd")));population.size_flags_horizontal=Control.SIZE_EXPAND_FILL;summary.add_child(population)
 summary.add_child(text(host.foundation.compact_number(int(r["area_km2"]))+" km²",14));host.territory_details.add_child(summary)
 var capital:=HBoxContainer.new();capital.name="StateCapital"
 var button: Button=host._button("◇ "+str(r["state_capital"]),func():host._focus_state_capital(int(r["id"])),str(r["capital_source"]));button.add_theme_font_size_override("font_size",12);button.clip_text=true;button.size_flags_horizontal=Control.SIZE_EXPAND_FILL;capital.add_child(button);capital.add_child(text(str(r["provinces"].size())+" provinces"));host.territory_details.add_child(capital)
 var slots:=Facilities.slots(r);var capacity:=text("Building slots   "+str(slots["used"])+" / "+str(slots["capacity"]),13,Color("e1cf9d"));capacity.name="BuildingSlots";capacity.tooltip_text="Shared construction capacity follows population and area, updated monthly. Existing headroom and occupied slots are retained; networks use separate levels.";host.territory_details.add_child(capacity)
 inventory(section("Buildings","StateBuildings"),r.get("buildings",{}),false);inventory(section("Infrastructure","StateInfrastructure"),r.get("buildings",{}),true)
 var staffing: Dictionary=host.state.employment.states[str(int(r["id"]))]
 var workers:=text("Building workers   "+host.foundation.compact_number(staffing["assigned"])+" / "+host.foundation.compact_number(staffing["required"]),12,Color("e1cf9d"));workers.name="BuildingWorkers";host.territory_details.add_child(workers)
 var other:=text("Other employment   "+host.foundation.compact_number(staffing["other_employment"]),11);other.tooltip_text="Services, baseline agriculture and other businesses outside explicit building jobs. Employment adjusts gradually each month; inactive residents are not automatically hired.";host.territory_details.add_child(other)
 var resources:=section("Resources","StateResources")
 var resource_grid:=GridContainer.new();resource_grid.columns=2;resources.add_child(resource_grid)
 for resource: String in r.get("resources",{}):
  var quantity:=float(r["resources"][resource])
  var item:=HBoxContainer.new();item.name="Resource_"+resource;item.tooltip_text=ResourceIcons.tooltip(resource,quantity);resource_grid.add_child(item)
  var symbol:=TextureRect.new();symbol.texture=ResourceIcons.icon(resource);symbol.expand_mode=TextureRect.EXPAND_IGNORE_SIZE;symbol.stretch_mode=TextureRect.STRETCH_KEEP_ASPECT_CENTERED;symbol.custom_minimum_size=Vector2(24,24);item.add_child(symbol)
  item.add_child(text(ResourceIcons.SYMBOLS[resource]+" · "+ResourceIcons.amount(quantity),11,Color("e1cf9d")))
 if resource_grid.get_child_count()==0:resources.add_child(text("No mapped resources",11))
 if host.state.selected_province>0 and host.distance<=1.2:
  var p: Dictionary=host.state.provinces[str(host.state.selected_province)];var label:=text("Province "+str(int(p["local_index"]))+" · "+str(p.get("kind","rural")).capitalize()+" · "+host._area_number(p["area_km2"])+" km²");label.name="SelectedProvince";label.tooltip_text=str(p.get("neighbors",[]).size())+" land connections";host.territory_details.add_child(label)
 var demographics:=preload("res://scripts/compact_demographics.gd").new()
 demographics.configure(host.foundation.demographics.state_metrics(host.state,int(r["id"])),host.territory_metric,func(key: String):host.territory_metric=key,true)
 section("Population profile","StatePopulationProfile").add_child(demographics)
 host._rights_row("Cores",r.get("cores",[]));host._rights_row("Claims",r.get("claims",[]))
 host.details=before;host._reveal_panel(host.territory_panel);host._position_panels()
func sea(main: Control,id: int) -> void:
 host=main;clear(host.territory_heading);clear(host.territory_details);host.territory_scroll.vertical_scroll_mode=ScrollContainer.SCROLL_MODE_AUTO;var r: Dictionary=host.state.sea_regions[str(id)];host.territory_heading.add_child(text("SEA REGION",10,Color("76bfb2")));var title:=text(r["name"],21,Color("eee4cd"));title.name="SeaTitle";title.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART;title.custom_minimum_size.y=54;host.territory_heading.add_child(title);host.territory_details.add_child(text(str(r["naval_terrain"]).replace("_"," ").capitalize(),14))
 var grid:=GridContainer.new();grid.columns=2;grid.add_theme_constant_override("h_separation",5);grid.add_theme_constant_override("v_separation",5);section("Neighbouring waters","NeighboringWaters").add_child(grid)
 for n: int in r["neighbors"]:
  if not host.state.sea_regions.has(str(n)):continue
  var button: Button=host._button(host.state.sea_regions[str(n)]["name"],func():host._show_sea(n));button.add_theme_font_size_override("font_size",11);button.clip_text=true;button.custom_minimum_size.x=130;button.size_flags_horizontal=Control.SIZE_EXPAND_FILL;grid.add_child(button)
 host._reveal_panel(host.territory_panel);host._position_panels()

func country_states(main: Control,tag: String) -> void:
 host=main;clear(host.territory_heading);clear(host.territory_details);host.territory_details.size_flags_vertical=Control.SIZE_EXPAND_FILL;host.territory_scroll.vertical_scroll_mode=ScrollContainer.SCROLL_MODE_DISABLED;host.territory_scroll.scroll_vertical=0
 var country: Dictionary=host.state.countries[tag]
 host.territory_heading.add_child(text(str(country["name"]),21,Color("f0eee2")))
 var ids: Array=[]
 for r: Dictionary in host.state.regions.values():
  if r["owner"]==tag:ids.append(int(r["id"]))
 ids.sort_custom(func(a: int,b: int):return str(host.state.regions[str(a)]["name"]).naturalnocasecmp_to(str(host.state.regions[str(b)]["name"]))<0)
 var heading:=text(str(ids.size())+" States · select a State to inspect",12);heading.name="CountryStatesHeading";host.territory_heading.add_child(heading)
 var scroll:=ScrollContainer.new();scroll.name="CountryStatesList";scroll.horizontal_scroll_mode=ScrollContainer.SCROLL_MODE_DISABLED;scroll.size_flags_vertical=Control.SIZE_EXPAND_FILL;scroll.mouse_force_pass_scroll_events=false;host.territory_details.add_child(scroll)
 var list:=VBoxContainer.new();list.size_flags_horizontal=Control.SIZE_EXPAND_FILL;list.add_theme_constant_override("separation",4);scroll.add_child(list)
 for id: int in ids:
  var r: Dictionary=host.state.regions[str(id)]
  var button: Button=host._button(str(r["name"])+"   ·   "+host.foundation.compact_number(r["population"]),func():host._open_country_state(id),"Capital: "+str(r["state_capital"])+" · "+str(r["provinces"].size())+" provinces")
  button.name="State_"+str(id);button.alignment=HORIZONTAL_ALIGNMENT_LEFT;button.clip_text=true;button.custom_minimum_size.y=38;button.size_flags_horizontal=Control.SIZE_EXPAND_FILL;button.add_theme_font_size_override("font_size",13);list.add_child(button)
  button.mouse_entered.connect(func():host._preview_state(id))
  button.mouse_exited.connect(func():
   if host.state_preview==id:host._preview_state(0))
  button.tree_exiting.connect(func():
   if host.state_preview==id:host._preview_state(0))
 host._reveal_panel(host.territory_panel);host._position_panels()
