extends VBoxContainer
func number(value: int) -> String:
 if value>=1000000000:return "%.2fB"%(value/1000000000.)
 if value>=1000000:return "%.2fM"%(value/1000000.)
 if value>=1000:return "%.1fK"%(value/1000.)
 return str(value)
func configure(values: Dictionary,is_state: bool=false) -> void:
 name="StateWorkforce" if is_state else "NationalWorkforce"
 add_theme_constant_override("separation",3)
 var heading:=Label.new();heading.text="WORKFORCE";heading.add_theme_font_size_override("font_size",11);heading.modulate=Color("76bfb2");add_child(heading)
 var grid:=GridContainer.new();grid.columns=2;grid.size_flags_horizontal=Control.SIZE_EXPAND_FILL;grid.add_theme_constant_override("h_separation",8);grid.add_theme_constant_override("v_separation",3);add_child(grid)
 var rows: Array=[["Participation","%.1f%%"%(float(values.get("participation_rate",0))*100),"Labour force / working-age residents"],["Unemployment","%.1f%%"%(float(values.get("unemployment_rate",0))*100),"Unemployed / labour force; excludes people not seeking work"],["Labour force",number(int(values.get("labour_force",0))),"Employed or seeking work"],["Employed",number(int(values.get("employed",0))),"Modeled formal and informal employment"],["Unemployed",number(int(values.get("unemployed",0))),"Seeking work"],["Outside labour force",number(int(values.get("outside_labour_force",0))),"Working-age residents not employed or seeking work"]]
 var fields: Dictionary={"Labour force":"labour_force","Employed":"employed","Unemployed":"unemployed","Outside labour force":"outside_labour_force"}
 for row: Array in rows:
  var label:=Label.new();label.text=str(row[0])+"  "+str(row[1]);label.add_theme_font_size_override("font_size",11);label.size_flags_horizontal=Control.SIZE_EXPAND_FILL;label.text_overrun_behavior=TextServer.OVERRUN_TRIM_ELLIPSIS;label.tooltip_text=str(row[2]);grid.add_child(label)
  if fields.has(row[0]):label.tooltip_text+="\n"+str(int(values.get(fields[row[0]],0)))+" people"
 var context:=Label.new();context.name="WorkforceContext";context.text="Working age: "+number(int(values.get("working_age",0)))+" · 2000 baseline estimate";context.add_theme_font_size_override("font_size",10);context.text_overrun_behavior=TextServer.OVERRUN_TRIM_ELLIPSIS;context.tooltip_text="Ages 18–"+str(int(values.get("retirement_age",65))-1)+". "+str(values.get("source",""))+"\n"+str(values.get("status",""));add_child(context)
