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
	vec2 delta_dir = q.xy/max(q.w, .00001) - p.xy/max(p.w, .00001);
	vec2 direction = length(delta_dir) > 0.00001 ? normalize(delta_dir) : vec2(0.0, 1.0);
	// Channel width is anchored to geographic scale (like HOI4) with a clean minimum
	float half_km = rank < 1.5 ? 2.4 : (rank < 3.5 ? 1.5 : 0.9);
	vec3 side = normalize(cross(radial, TANGENT));
	vec3 edge = normalize(radial + side * (half_km / 6371.0));
	vec4 ep = PROJECTION_MATRIX * MODELVIEW_MATRIX * vec4(edge * length(VERTEX), 1.0);
	float geographic = length((ep.xy / ep.w - p.xy / p.w) * VIEWPORT_SIZE * 0.5);
	float width = passage > 0.5 ? clamp(geographic, 2.0, 5.0) : clamp(geographic, 1.2, 5.5);
	bank_start = passage > 0.5 ? 1.0 : 0.72;
	POSITION = p;
	POSITION.xy += vec2(-direction.y, direction.x) * UV.x * (width + 0.3) * 2.0 / VIEWPORT_SIZE * p.w;
}
void fragment(){
	if(facing<.012)discard;
	float visibility=1.0-smoothstep(rank<1.5?2.5:(rank<4.5?1.65:1.2),rank<1.5?3.5:(rank<4.5?2.4:1.65),camera_distance);
	if(passage>.5)visibility=1.0-smoothstep(2.2,3.5,camera_distance);
	float bank=smoothstep(bank_start-.045,bank_start+.045,abs(UV.x));
	float centre=1.0-smoothstep(.0,.65,abs(UV.x));
	vec3 water_deep=vec3(.035,.14,.22);
	vec3 water_shallow=vec3(.075,.26,.34);
	vec3 bank_color=vec3(.22,.25,.18);
	vec3 water=mix(water_shallow,water_deep,centre*.75);
	ALBEDO=physical_mode?mix(water,bank_color,bank*.85):vec3(.10,.34,.43);
	ALPHA=(1.0-smoothstep(.75,1.0,abs(UV.x)))*visibility*(physical_mode?.94:.70);
}
