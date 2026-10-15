shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never, depth_test_disabled;
uniform sampler2D relief_data : filter_linear, repeat_enable;
uniform bool physical_mode=true;
uniform float camera_distance=3.0;
varying float facing;
varying flat float rank;
varying flat float passage;
varying float bank_start;
void vertex(){
	vec3 radial=normalize(VERTEX);
	vec2 uv=vec2(fract(atan(radial.x,radial.z)/6.28318530718+.5),acos(clamp(radial.y,-1.0,1.0))/3.14159265359);
	vec2 d=textureLod(relief_data,uv,0.0).rg;
	VERTEX=radial*(1.000008+dot(d,vec2(255.0,65280.0))/65535.0*.016);
	vec3 eye=(MODELVIEW_MATRIX*vec4(VERTEX,1.0)).xyz;
	facing=dot(normalize(mat3(MODELVIEW_MATRIX)*radial),normalize(-eye));
	rank=UV2.x;passage=UV2.y;
	vec3 ahead=normalize(radial+TANGENT*.00001);
	vec4 p=PROJECTION_MATRIX*MODELVIEW_MATRIX*vec4(VERTEX,1.0);
	vec4 q=PROJECTION_MATRIX*MODELVIEW_MATRIX*vec4(ahead*(length(VERTEX)),1.0);
	vec2 direction=normalize(q.xy/max(q.w,.00001)-p.xy/max(p.w,.00001));
	float close=1.0-smoothstep(1.05,1.7,camera_distance);
	// Geographic channel width grows naturally under zoom. Minimum screen
	// coverage keeps tributaries readable; banks have their own outer strip.
	float half_km=rank<1.5?1.35:(rank<3.5?.85:.38);
	vec3 side=normalize(cross(radial,TANGENT));
	vec3 edge=normalize(radial+side*(half_km/6371.0));
	vec4 ep=PROJECTION_MATRIX*MODELVIEW_MATRIX*vec4(edge*length(VERTEX),1.0);
	float geographic=length((ep.xy/ep.w-p.xy/p.w)*VIEWPORT_SIZE*.5);
	float minimum=rank<1.5?mix(1.4,7.5,close):mix(.7,3.8,close);
	float water_width=max(geographic,minimum);
	float width=passage>.5?mix(2.5,5.0,close):water_width+max(1.0,water_width*.22)*close;
	bank_start=passage>.5?1.0:water_width/width;
	POSITION=p;
	POSITION.xy+=vec2(-direction.y,direction.x)*UV.x*(width+.5)*2.0/VIEWPORT_SIZE*p.w;
}
void fragment(){
	if(facing<.012)discard;
	float visibility=1.0-smoothstep(rank<1.5?2.5:(rank<4.5?1.65:1.2),rank<1.5?3.5:(rank<4.5?2.4:1.65),camera_distance);
	if(passage>.5)visibility=1.0-smoothstep(2.2,3.5,camera_distance);
	float bank=smoothstep(bank_start-.045,bank_start+.045,abs(UV.x));
	float centre=1.0-smoothstep(.0,.65,abs(UV.x));
	vec3 water=mix(vec3(.075,.31,.39),vec3(.025,.16,.23),centre*.65);
	ALBEDO=physical_mode?mix(water,vec3(.23,.25,.17),bank):vec3(.10,.34,.43);
	ALPHA=(1.0-smoothstep(.88,1.0,abs(UV.x)))*visibility*(physical_mode?.96:.70);
}
