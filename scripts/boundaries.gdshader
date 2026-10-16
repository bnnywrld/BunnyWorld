shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never, depth_test_disabled;
uniform sampler2D owners : filter_nearest;
uniform sampler2D region_map_0 : filter_nearest;
uniform sampler2D region_map_1 : filter_nearest;
uniform sampler2D region_map_2 : filter_nearest;
uniform sampler2D region_map_3 : filter_nearest;
uniform sampler2D relief_data : filter_linear, repeat_enable;
#include "res://scripts/border_surface.gdshaderinc"
uniform float palette_width=8192.0;
uniform float selected_country=0.0;
uniform float selected_region=0.0;
uniform float selected_sea=0.0;
uniform bool inspection_active=false;
uniform bool show_regions=false;
uniform bool physical_mode=false;
uniform float camera_distance=3.65;
varying flat float kind;
varying flat float selected;
varying flat float half_width;
varying flat float extent;
varying flat float opacity;
varying vec3 sphere_point;
varying float facing;
float owner(float id){vec3 d=texture(owners,vec2((id+.5)/palette_width,.5)).rgb;return floor(d.r*255.0+.5)+floor(d.g*255.0+.5)*256.0;}
void vertex(){
 vec3 radial=normalize(VERTEX);vec2 geo=vec2(fract(atan(radial.x,radial.z)/6.28318530718+.5),acos(clamp(radial.y,-1.0,1.0))/3.14159265359);VERTEX=radial*(1.000004+border_relief(geo));sphere_point=VERTEX;
 vec3 eye=(MODELVIEW_MATRIX*vec4(VERTEX,1.0)).xyz;facing=dot(normalize(mat3(MODELVIEW_MATRIX)*radial),normalize(-eye));
 kind=UV.y;float left=floor(UV2.x+.5),right=floor(UV2.y+.5);float lo=owner(left),ro=owner(right);bool national=lo!=ro;bool coast=left<.5||right<.5;
 selected=(inspection_active&&selected_country>0.0&&national&&(lo==selected_country||ro==selected_country))?1.0:0.0;
 if(kind>.5)selected=(selected_sea>0.0&&(left==selected_sea||right==selected_sea))?2.0:0.0;
 else if(show_regions&&selected_region>0.0&&(left==selected_region||right==selected_region))selected=2.0;
 float nearby=1.0-smoothstep(1.3,3.1,camera_distance);float width=national?mix(1.45,3.2,nearby):1.75;opacity=national?1.0:(1.0-smoothstep(1.42,1.72,camera_distance))*.52;
 if(!national&&(!show_regions||(inspection_active&&lo!=selected_country)))opacity=0.0;
 if(coast)opacity*=physical_mode?.68:.82;
 if(kind>.5){width=.85;opacity=(1.0-smoothstep(1.9,2.8,camera_distance))*.22;}
 if(selected>.5){width=selected>1.5?2.0:mix(1.8,2.6,nearby);opacity=1.0;}
 float analytic=1.0-smoothstep(1.45,1.65,camera_distance);
 if(kind<.5){
  if(left==right)opacity=0.0;
  if(coast||(inspection_active&&selected_region>0.0&&(left==selected_region||right==selected_region)))opacity*=1.0-analytic;
 }else{
  if(left<.5||right<.5)opacity=0.0;
  if(selected_sea>0.0&&(left==selected_sea||right==selected_sea))opacity*=1.0-analytic;
 }
 half_width=width*.5;extent=half_width+(selected>.5?2.8:1.0);
 vec3 ahead_n=normalize(radial+normalize(TANGENT)*.0001);vec2 uv=vec2(fract(atan(ahead_n.x,ahead_n.z)/6.28318530718+.5),acos(clamp(ahead_n.y,-1.0,1.0))/3.14159265359);vec3 ahead=ahead_n*(1.000004+border_relief(uv));
 vec4 p=PROJECTION_MATRIX*MODELVIEW_MATRIX*vec4(VERTEX,1.0),q=PROJECTION_MATRIX*MODELVIEW_MATRIX*vec4(ahead,1.0);vec2 line=normalize(q.xy/max(q.w,.00001)-p.xy/max(p.w,.00001));POSITION=p;POSITION.xy+=vec2(-line.y,line.x)*UV.x*extent*2.0/VIEWPORT_SIZE*p.w;
}
void fragment(){
 if(facing<.012||opacity<.001)discard;
 if(kind>.5){vec3 p=normalize(sphere_point);vec2 uv=vec2(fract(atan(p.x,p.z)/6.28318530718+.5),acos(clamp(p.y,-1.0,1.0))/3.14159265359);vec2 at=fract(uv*2.0);vec3 d;if(uv.y<.5)d=uv.x<.5?texture(region_map_0,at).rgb:texture(region_map_1,at).rgb;else d=uv.x<.5?texture(region_map_2,at).rgb:texture(region_map_3,at).rgb;if(d.r+d.g>0.0)discard;}
 float px=abs(UV.x)*extent;float aa=max(fwidth(px)*.65,.45);float casing=1.0-smoothstep(half_width-aa,half_width+aa,px);float inner=1.0-smoothstep(max(.1,half_width-.65)-aa,max(.1,half_width-.65)+aa,px);
 vec3 dark=vec3(.025,.045,.055);vec3 ink=physical_mode?vec3(.34,.39,.36):vec3(.44,.48,.46);if(kind>.5){ink=vec3(.36,.54,.60);dark=ink;}
 float glow=0.0;if(selected>.5){ink=selected>1.5?vec3(.70,.82,.79):vec3(.90,.81,.58);dark=selected>1.5?vec3(.11,.25,.27):vec3(.21,.18,.11);glow=exp(-max(px-half_width,0.0)*1.15)*.18*(.88+.12*sin(TIME*1.7));}
 ALBEDO=mix(dark,ink,max(inner,selected>.5?1.0-casing:0.0));ALPHA=max(casing,glow)*opacity*smoothstep(.012,.08,facing);
}
