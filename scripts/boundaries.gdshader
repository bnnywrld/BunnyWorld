shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never, depth_test_disabled;
uniform sampler2D owners : filter_nearest;
uniform sampler2D region_map_0 : filter_nearest;
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
	vec3 radial = normalize(VERTEX);
	vec2 geo = vec2(fract(atan(radial.x, radial.z) / 6.28318530718 + 0.5), acos(clamp(radial.y, -1.0, 1.0)) / 3.14159265359);
	float r = border_relief(geo);
	VERTEX = radial * (1.000004 + r);
	sphere_point = VERTEX;
	vec3 eye = (MODELVIEW_MATRIX * vec4(VERTEX, 1.0)).xyz;
	facing = dot(normalize(mat3(MODELVIEW_MATRIX) * radial), normalize(-eye));
	kind = UV.y;
	float left = floor(UV2.x + 0.5), right = floor(UV2.y + 0.5);
	float lo = 0.0, ro = 0.0;
	bool national = false;
	bool coast = left < 0.5 || right < 0.5;
	if (kind < 0.5) {
		lo = owner(left);
		ro = owner(right);
		national = lo != ro;
	}
	selected = (inspection_active && selected_country > 0.0 && national && (lo == selected_country || ro == selected_country)) ? 1.0 : 0.0;
	if (kind > 0.5) selected = (selected_sea > 0.0 && (left == selected_sea || right == selected_sea)) ? 2.0 : 0.0;
	else if (show_regions && selected_region > 0.0 && (left == selected_region || right == selected_region)) selected = 2.0;
	float nearby = 1.0 - smoothstep(1.3, 3.1, camera_distance);
	float width = national ? mix(1.35, 2.0, nearby) : 1.25;
	opacity = national ? 1.0 : (1.0 - smoothstep(1.42, 1.72, camera_distance)) * 0.52;
	if (!national && (!show_regions || (inspection_active && lo != selected_country))) opacity = 0.0;
	if (kind > 0.5) { width = 0.85; opacity = (1.0 - smoothstep(1.9, 2.8, camera_distance)) * 0.22; }
	if (selected > 0.5) { width = selected > 1.5 ? 2.0 : mix(1.6, 2.2, nearby); opacity = 1.0; }
	if (kind < 0.5) {
		if (left == right || coast) opacity = 0.0;
	} else {
		if (left < 0.5 || right < 0.5) opacity = 0.0;
	}
	half_width = width * 0.5;
	extent = half_width + (selected > 0.5 ? 1.5 : 0.85);
	vec3 ahead_n = normalize(radial + normalize(TANGENT) * 0.0001);
	vec3 ahead = ahead_n * (1.000004 + r);
	vec4 p = PROJECTION_MATRIX * MODELVIEW_MATRIX * vec4(VERTEX, 1.0), q = PROJECTION_MATRIX * MODELVIEW_MATRIX * vec4(ahead, 1.0);
	vec2 line = normalize(q.xy / max(q.w, 0.00001) - p.xy / max(p.w, 0.00001));
	POSITION = p;
	POSITION.xy += vec2(-line.y, line.x) * UV.x * extent * 2.0 / VIEWPORT_SIZE * p.w;
}
void fragment(){
	if (facing < 0.012 || opacity < 0.001) discard;
	if (kind > 0.5) {
		vec3 p = normalize(sphere_point);
		vec2 uv = vec2(fract(atan(p.x, p.z) / 6.28318530718 + 0.5), acos(clamp(p.y, -1.0, 1.0)) / 3.14159265359);
		vec3 d = texture(region_map_0, uv).rgb;
		if (d.r + d.g > 0.0) discard;
	}
	float px = abs(UV.x) * extent;
	float aa = max(fwidth(px) * 0.65, 0.45);
	float casing = 1.0 - smoothstep(half_width - aa, half_width + aa, px);
	float inner = 1.0 - smoothstep(max(0.1, half_width - 0.65) - aa, max(0.1, half_width - 0.65) + aa, px);

	vec3 dark = vec3(0.025, 0.045, 0.055);
	vec3 ink = physical_mode ? vec3(0.28, 0.32, 0.30) : vec3(0.44, 0.48, 0.46);
	if (kind > 0.5) { ink = vec3(0.36, 0.54, 0.60); dark = ink; }
	if (selected > 0.5) {
		ink = selected > 1.5 ? vec3(0.93, 0.85, 0.30) : vec3(0.96, 0.94, 0.88);
		dark = selected > 1.5 ? vec3(0.24, 0.20, 0.05) : vec3(0.04, 0.05, 0.05);
	}
	vec3 core_color = mix(dark, ink, max(inner, selected > 0.5 ? 1.0 - casing : 0.0));

	ALBEDO = core_color;
	ALPHA = casing * opacity * smoothstep(0.012, 0.08, facing);
}
