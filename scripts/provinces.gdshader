shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never, depth_test_disabled;
uniform sampler2D owners : filter_nearest;
uniform sampler2D province_index : filter_nearest;
uniform float selected_country=0.0;
uniform float selected_province=0.0;
uniform bool inspection_active=false;
uniform bool physical_mode=false;
uniform float province_opacity=0.0;
varying flat float parent_owner;
varying flat float selected_edge;
varying float visible_facing;
vec3 record(float pid){return floor(texture(province_index,vec2((mod(pid,256.0)+.5)/256.0,(floor(pid/256.0)+.5)/256.0)).rgb*255.0+.5);}
uniform sampler2D relief_data : filter_linear, repeat_enable;
void vertex(){
 vec3 radial=normalize(VERTEX);
 vec2 geo=vec2(fract(atan(radial.x,radial.z)/6.28318530718+.5),acos(clamp(radial.y,-1.0,1.0))/3.14159265359);
 vec2 d=textureLod(relief_data,geo,0.0).rg;
 VERTEX=radial*(1.000004+dot(d,vec2(255.0,65280.0))/65535.0*.016);

 vec3 a=record(UV2.x),b=record(UV2.y);float region=a.r+a.g*256.0;
 vec3 own=floor(texture(owners,vec2((region+.5)/8192.0,.5)).rgb*255.0+.5);parent_owner=own.r+own.g*256.0;
 selected_edge=(selected_province>0.0&&(UV2.x==selected_province||UV2.y==selected_province))?1.0:0.0;
 vec3 eye_position=(MODELVIEW_MATRIX*vec4(VERTEX,1.0)).xyz;
 visible_facing=dot(normalize(mat3(MODELVIEW_MATRIX)*normalize(VERTEX)),normalize(-eye_position));
 vec3 ahead_n=normalize(radial+normalize(TANGENT)*.0001);
 vec2 ahead_uv=vec2(fract(atan(ahead_n.x,ahead_n.z)/6.28318530718+.5),acos(clamp(ahead_n.y,-1.0,1.0))/3.14159265359);
 vec2 ahead_data=textureLod(relief_data,ahead_uv,0.0).rg;
 vec3 ahead=ahead_n*(1.000004+dot(ahead_data,vec2(255.0,65280.0))/65535.0*.016);
 float width=selected_edge>.5?1.45:.36;
 vec4 p=PROJECTION_MATRIX*MODELVIEW_MATRIX*vec4(VERTEX,1.0),q=PROJECTION_MATRIX*MODELVIEW_MATRIX*vec4(ahead,1.0);
 vec2 line=normalize(q.xy/max(q.w,.00001)-p.xy/max(p.w,.00001));vec2 side=vec2(-line.y,line.x);
 POSITION=p;POSITION.xy+=side*UV.x*(width+.75)*2.0/VIEWPORT_SIZE*p.w;
}
void fragment(){
 if(visible_facing<.012||province_opacity<=0.0||parent_owner<.5||(inspection_active&&parent_owner!=selected_country))discard;
 float alpha=(1.0-smoothstep(.52,1.0,abs(UV.x)))*province_opacity;
 ALBEDO=selected_edge>.5?vec3(.65,.95,1.0):(physical_mode?vec3(.12,.16,.16):vec3(.055,.09,.12));
 ALPHA=alpha*(selected_edge>.5?.92:.46);
}
