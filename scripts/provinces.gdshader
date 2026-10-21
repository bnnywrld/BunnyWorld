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
	vec3 radial = normalize(VERTEX);
	vec2 geo = vec2(fract(atan(radial.x, radial.z) / 6.28318530718 + 0.5), acos(clamp(radial.y, -1.0, 1.0)) / 3.14159265359);
	float r = border_relief(geo);
	VERTEX = radial * (1.000004 + r);
	vec3 a = record(UV2.x);
	float region = a.r + a.g * 256.0;
	parent_region = region;
	vec3 own = floor(texture(owners, vec2((region + 0.5) / 8192.0, 0.5)).rgb * 255.0 + 0.5);
	parent_owner = own.r + own.g * 256.0;
	selected = (selected_province > 0.0 && (UV2.x == selected_province || UV2.y == selected_province)) ? 1.0 : 0.0;
	vec3 eye = (MODELVIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	facing = dot(normalize(mat3(MODELVIEW_MATRIX) * radial), normalize(-eye));
	vec3 an = normalize(radial + normalize(TANGENT) * 0.0001);
	vec3 ahead = an * (1.000004 + r);
	extent = selected > 0.5 ? 2.8 : 1.35;
	vec4 p = PROJECTION_MATRIX * MODELVIEW_MATRIX * vec4(VERTEX, 1.0), q = PROJECTION_MATRIX * MODELVIEW_MATRIX * vec4(ahead, 1.0);
	vec2 line = normalize(q.xy / max(q.w, 0.00001) - p.xy / max(p.w, 0.00001));
	POSITION = p;
	POSITION.xy += vec2(-line.y, line.x) * UV.x * extent * 2.0 / VIEWPORT_SIZE * p.w;
}
void fragment(){
	float fade = 1.0 - smoothstep(1.18, 1.35, camera_distance);
	if (inspection_active && parent_region == selected_region) fade = max(fade, 1.0 - smoothstep(1.36, 1.52, camera_distance));
	if (selected > 0.5) fade = 1.0;
	if (facing < 0.012 || fade <= 0.0 || parent_owner < 0.5 || (inspection_active && parent_owner != selected_country)) discard;
	float px = abs(UV.x) * extent, aa = max(fwidth(px) * 0.65, 0.4), hw = selected > 0.5 ? 1.0 : 0.58;
	float outer = 1.0 - smoothstep(hw - aa, hw + aa, px);
	float inner = 1.0 - smoothstep(max(0.1, hw - 0.45) - aa, max(0.1, hw - 0.45) + aa, px);
	vec3 color = mix(vec3(0.045, 0.075, 0.08), physical_mode ? vec3(0.30, 0.35, 0.31) : vec3(0.45, 0.48, 0.43), inner);
	vec3 sel_gold = vec3(0.93, 0.85, 0.30);
	if (selected > 0.5) color = mix(vec3(0.24, 0.20, 0.05), sel_gold, inner);
	float pwing_alpha = 0.0;
	if (selected > 0.5) {
		float pwing = clamp((extent - px) / max(extent - hw, 0.001), 0.0, 1.0);
		pwing_alpha = smoothstep(0.0, 1.0, pwing) * 0.45;
	}
	ALBEDO = mix(sel_gold, color, outer);
	ALPHA = max(outer, pwing_alpha) * fade * (selected > 0.5 ? 1.0 : (parent_region == selected_region ? 0.52 : 0.32)) * smoothstep(0.012, 0.08, facing);
}
