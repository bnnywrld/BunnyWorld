shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never, depth_test_disabled;
uniform sampler2D owners : filter_nearest;
uniform sampler2D province_index : filter_nearest;
uniform sampler2D relief_data : filter_linear, repeat_enable;
#include "res://scripts/border_surface.gdshaderinc"
uniform float selected_country=0.0;
uniform float selected_province=0.0;
uniform float selected_region=0.0;
uniform bool inspection_active=false;
uniform bool physical_mode=false;
uniform float camera_distance=3.65;
varying flat float parent_owner;
varying flat float parent_region;
varying flat float selected;
varying flat float extent;
varying float facing;
vec3 record(float pid){return floor(texture(province_index,vec2((mod(pid,256.0)+.5)/256.0,(floor(pid/256.0)+.5)/256.0)).rgb*255.0+.5);}
void vertex(){
 vec3 radial=normalize(VERTEX);vec2 geo=vec2(fract(atan(radial.x,radial.z)/6.28318530718+.5),acos(clamp(radial.y,-1.0,1.0))/3.14159265359);VERTEX=radial*(1.000004+border_relief(geo));
 vec3 a=record(UV2.x);float region=a.r+a.g*256.0;parent_region=region;vec3 own=floor(texture(owners,vec2((region+.5)/8192.0,.5)).rgb*255.0+.5);parent_owner=own.r+own.g*256.0;selected=(selected_province>0.0&&(UV2.x==selected_province||UV2.y==selected_province))?1.0:0.0;
 vec3 eye=(MODELVIEW_MATRIX*vec4(VERTEX,1.0)).xyz;facing=dot(normalize(mat3(MODELVIEW_MATRIX)*radial),normalize(-eye));vec3 an=normalize(radial+normalize(TANGENT)*.0001);vec2 au=vec2(fract(atan(an.x,an.z)/6.28318530718+.5),acos(clamp(an.y,-1.0,1.0))/3.14159265359);vec3 ahead=an*(1.000004+border_relief(au));
 extent=selected>.5?2.6:1.35;vec4 p=PROJECTION_MATRIX*MODELVIEW_MATRIX*vec4(VERTEX,1.0),q=PROJECTION_MATRIX*MODELVIEW_MATRIX*vec4(ahead,1.0);vec2 line=normalize(q.xy/max(q.w,.00001)-p.xy/max(p.w,.00001));POSITION=p;POSITION.xy+=vec2(-line.y,line.x)*UV.x*extent*2.0/VIEWPORT_SIZE*p.w;
}
void fragment(){
 float fade=1.0-smoothstep(1.18,1.35,camera_distance);
 if(inspection_active&&parent_region==selected_region)fade=max(fade,1.0-smoothstep(1.36,1.52,camera_distance));if(selected>.5)discard;
 if(facing<.012||fade<=0.0||parent_owner<.5||(inspection_active&&parent_owner!=selected_country))discard;
 float px=abs(UV.x)*extent,aa=max(fwidth(px)*.65,.4),hw=selected>.5?1.0:.58;float outer=1.0-smoothstep(hw-aa,hw+aa,px);float inner=1.0-smoothstep(max(.1,hw-.45)-aa,max(.1,hw-.45)+aa,px);
 vec3 color=mix(vec3(.045,.075,.08),physical_mode?vec3(.30,.35,.31):vec3(.45,.48,.43),inner);if(selected>.5)color=mix(vec3(.10,.24,.25),vec3(.75,.87,.81),inner);ALBEDO=color;ALPHA=outer*fade*(parent_region==selected_region?.52:.32)*smoothstep(.012,.08,facing);
}
