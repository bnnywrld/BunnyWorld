shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never, depth_test_disabled;
uniform sampler2D owners : filter_nearest;
uniform sampler2D region_map_0 : filter_nearest;
uniform sampler2D region_map_1 : filter_nearest;
uniform sampler2D region_map_2 : filter_nearest;
uniform sampler2D region_map_3 : filter_nearest;
uniform float palette_width=8192.0;
uniform float selected_country=0.0;
uniform float selected_region=0.0;
uniform float selected_sea=0.0;
uniform bool inspection_active=false;
uniform bool show_regions=false;
uniform bool physical_mode=false;
uniform float region_opacity=0.0;
uniform float strength=1.0;
uniform float sea_opacity=0.0;
// These are categorical IDs, constant on each ribbon. Interpolating them
// introduces rounding errors that make owner equality flicker across pixels.
varying flat float left_region;
varying flat float right_region;
varying flat float left_owner;
varying flat float right_owner;
varying flat float edge_type;
varying flat float selected_edge;
varying vec3 sphere_point;
varying float visible_facing;

float owner(float id){vec3 v=texture(owners,vec2((id+.5)/palette_width,.5)).rgb;return floor(v.r*255.0+.5)+floor(v.g*255.0+.5)*256.0;}
uniform sampler2D relief_data : filter_linear, repeat_enable;
void vertex(){
 vec3 radial=normalize(VERTEX);
 vec2 geo=vec2(fract(atan(radial.x,radial.z)/6.28318530718+.5),acos(clamp(radial.y,-1.0,1.0))/3.14159265359);
 vec2 d=textureLod(relief_data,geo,0.0).rg;
 VERTEX=radial*(1.000004+dot(d,vec2(255.0,65280.0))/65535.0*.016);

 sphere_point=VERTEX;
 vec3 eye_position=(MODELVIEW_MATRIX*vec4(VERTEX,1.0)).xyz;
 visible_facing=dot(normalize(mat3(MODELVIEW_MATRIX)*normalize(VERTEX)),normalize(-eye_position));
 left_region=floor(UV2.x+.5);
 right_region=floor(UV2.y+.5);
 left_owner=owner(left_region);right_owner=owner(right_region);
 edge_type=UV.y;
 bool country_edge=left_owner!=right_owner;
 selected_edge=(inspection_active&&selected_country>0.0&&country_edge&&(left_owner==selected_country||right_owner==selected_country))?1.0:0.0;
 if(edge_type>.5)selected_edge=(selected_sea>0.0&&(left_region==selected_sea||right_region==selected_sea))?2.0:0.0;
 else if(show_regions&&selected_region>0.0&&(left_region==selected_region||right_region==selected_region))selected_edge=2.0;
 vec3 ahead_n=normalize(radial+normalize(TANGENT)*.0001);
 vec2 ahead_uv=vec2(fract(atan(ahead_n.x,ahead_n.z)/6.28318530718+.5),acos(clamp(ahead_n.y,-1.0,1.0))/3.14159265359);
 vec2 ahead_data=textureLod(relief_data,ahead_uv,0.0).rg;
 vec3 ahead=ahead_n*(1.000004+dot(ahead_data,vec2(255.0,65280.0))/65535.0*.016);
 float width=selected_edge>0.0?2.3:(edge_type>.5?.7:(country_edge?(physical_mode?1.25:.72):(physical_mode?.70:.40)));
 vec4 p=PROJECTION_MATRIX*MODELVIEW_MATRIX*vec4(VERTEX,1.0);
 vec4 q=PROJECTION_MATRIX*MODELVIEW_MATRIX*vec4(ahead,1.0);
 vec2 line=normalize(q.xy/max(q.w,.00001)-p.xy/max(p.w,.00001));
 vec2 side=vec2(-line.y,line.x);
 POSITION=p;POSITION.xy+=side*UV.x*(width+.75)*2.0/VIEWPORT_SIZE*p.w;
}
void fragment(){
 float facing=visible_facing;
 if(facing<.012)discard;
 float alpha=1.0-smoothstep(.52,1.0,abs(UV.x));
 vec3 color=physical_mode?vec3(.12,.16,.16):vec3(.055,.09,.12);
 if(edge_type>.5){
  vec3 point=normalize(sphere_point);vec2 uv=vec2(fract(atan(point.x,point.z)/6.28318530718+.5),acos(clamp(point.y,-1.0,1.0))/3.14159265359);vec2 p=fract(uv*2.0);vec3 data;
  if(uv.y<.5){data=uv.x<.5?texture(region_map_0,p).rgb:texture(region_map_1,p).rgb;}
  else{data=uv.x<.5?texture(region_map_2,p).rgb:texture(region_map_3,p).rgb;}
  if(data.r+data.g>0.0)discard;
  color=selected_edge>0.0?vec3(.40,.84,.95):vec3(.37,.59,.69);alpha*=selected_edge>0.0?.95:sea_opacity;
 }
 else{
  bool coast=left_region<.5||right_region<.5;
  bool national=left_owner!=right_owner;
  if(!coast&&!national){
   if(!show_regions||(inspection_active&&left_owner!=selected_country))discard;
   alpha*=region_opacity*(physical_mode?.58:.66);
  }else{alpha*=strength*(coast?(physical_mode?.45:.76):.95);}
  if(selected_edge>.5){color=selected_edge>1.5?vec3(.35,.91,.98):vec3(1.0,.83,.24);alpha=max(alpha,.94)*(1.0-smoothstep(.52,1.0,abs(UV.x)));}
 }
 ALBEDO=color;ALPHA=alpha;
}
