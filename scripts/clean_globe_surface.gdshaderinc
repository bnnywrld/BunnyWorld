#include "res://scripts/water_passages.gdshaderinc"
// --- Uniforms: geography data ---
uniform sampler2D region_map_0 : filter_nearest, repeat_disable;
uniform sampler2D province_index : filter_nearest, repeat_disable;
uniform sampler2D relief_data : filter_linear, repeat_enable;
uniform sampler2DArray terrain_materials : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D far_terrain : filter_linear_mipmap, repeat_enable;
uniform bool far_terrain_enabled = true;
uniform sampler2D terrain_types : filter_nearest, repeat_enable;
uniform sampler2D terrain_color : source_color, filter_linear_mipmap, repeat_enable;
uniform sampler2D coast_distance : filter_linear, repeat_enable;
uniform sampler2D tiny_land_bits : filter_nearest, repeat_disable;
uniform sampler2D sea_map : filter_nearest, repeat_disable;
uniform vec2 map_resolution = vec2(8192.0, 4096.0);

// --- Uniforms: boundary SDF (loaded from .bwd by test harness) ---
uniform sampler2D boundary_hint : filter_linear, repeat_enable;
uniform sampler2D boundary_pairs : filter_nearest, repeat_enable;
uniform sampler2D boundary_distance : filter_linear, repeat_enable;

// --- Uniforms: dynamic palette ---
uniform sampler2D colors : source_color, filter_nearest;
uniform sampler2D owners : filter_nearest;
uniform float palette_width = 8192.0;

// --- Uniforms: selection / hover ---
uniform float selected_country = 0.0;
uniform float hovered_country = 0.0;
uniform float hover_amount = 0.0;
uniform float selected_region = 0.0;
uniform float selected_province = 0.0;
uniform float selected_sea = 0.0;
uniform bool inspection_active = false;
uniform float province_opacity = 0.0;

// --- Uniforms: map mode ---
uniform bool physical_mode = false;
uniform bool information_mode = false;
uniform bool show_regions = false;
uniform float region_opacity = 0.0;

// --- Uniforms: camera-driven ---
uniform float camera_distance = 3.65;
uniform float far_filter = 0.0;
uniform float border_width = 1.15;
uniform float border_strength = 1.0;
uniform float coast_strength = 1.0;
uniform float terrain_mix = 0.0;
uniform float city_detail = 0.0;

// --- Uniforms: urban ---
uniform sampler2D urban_density : filter_linear_mipmap, repeat_enable;
uniform sampler2D urban_material : source_color, filter_linear_mipmap, repeat_enable;

// --- Varyings ---
varying vec3 geographic_normal;
varying vec2 cartography_uv;
varying vec3 radial_world;
varying vec3 east_world;
varying vec3 north_world;

// ============================================================
// Helper functions
// ============================================================
vec3 map_data(vec2 uv) {
	uv = vec2(fract(uv.x), clamp(uv.y, 0.0, .999999));
	vec3 data = texture(region_map_0, uv).rgb;
	return floor(data * 255.0 + .5);
}
float province_at(vec2 uv) { vec3 d = map_data(uv); return d.r + d.g * 256.0; }
vec4 province_record(float pid) { return floor(texture(province_index, vec2((mod(pid, 256.0) + .5) / 256.0, (floor(pid / 256.0) + .5) / 256.0)) * 255.0 + .5); }
float province_region(float pid) { vec2 d = province_record(pid).rg; return d.r + d.g * 256.0; }
float region_at(vec2 uv) { return province_region(province_at(uv)); }
vec2 lookup(float id) { return vec2((id + .5) / palette_width, .5); }
float owner_at(float id) { vec3 d = texture(owners, lookup(id)).rgb; return floor(d.r * 255.0 + .5) + floor(d.g * 255.0 + .5) * 256.0; }
vec4 color_at(vec2 uv, vec3 water) { float id = region_at(uv); return id < .5 ? vec4(water, 0.0) : vec4(texture(colors, lookup(id)).rgb, 1.0); }

float relief(vec2 uv) {
	vec2 d = textureLod(relief_data, vec2(fract(uv.x), clamp(uv.y, 0.0, 1.0)), 0.0).rg;
	return (dot(d, vec2(255.0, 65280.0)) / 65535.0) * .016;
}

float coverage_alpha(float d) { float aa = max(fwidth(d) * .65, 1.0 / 255.0); return smoothstep(.5 - aa, .5 + aa, d); }
float field_pixels(float v) { return (v - .5) / max(fwidth(v), .00001); }

vec3 field_ink(vec3 base, float pixels, float width, vec3 ink, float strength) {
	float px = abs(pixels), aa = .65;
	float casing = 1.0 - smoothstep(width * .5 - aa, width * .5 + aa, px);
	float inner = 1.0 - smoothstep(max(.1, width * .5 - .6) - aa, max(.1, width * .5 - .6) + aa, px);
	base = mix(base, vec3(.025, .045, .055), casing * .8 * strength);
	base = mix(base, ink, inner * .9 * strength);
	float glow = exp(-max(px - width * .5, 0.0) * 1.3) * .09 * (.92 + .08 * sin(TIME * 1.7));
	return mix(base, ink, glow * strength);
}

float small_land_at(vec2 pixel) {
	pixel = vec2(mod(pixel.x + map_resolution.x, map_resolution.x), clamp(pixel.y, 0.0, map_resolution.y - 1.0));
	vec2 bit_uv = (vec2(floor(pixel.x / 8.0), pixel.y) + .5) / vec2(map_resolution.x / 8.0, map_resolution.y);
	uint bits = uint(floor(texture(tiny_land_bits, bit_uv).r * 255.0 + .5));
	return float((bits >> uint(mod(pixel.x, 8.0))) & uint(1));
}

float ocean_sample(vec2 uv) { return texture(sea_map, vec2(fract(uv.x), clamp(uv.y, 0.0, 1.0))).r; }
float ocean_nearby(vec2 uv) {
	vec2 step = 1.0 / vec2(textureSize(sea_map, 0));
	return max(ocean_sample(uv), max(max(ocean_sample(uv + vec2(step.x, 0.0)), ocean_sample(uv - vec2(step.x, 0.0))), max(ocean_sample(uv + vec2(0.0, step.y)), ocean_sample(uv - vec2(0.0, step.y)))));
}

// Find nearest valid province texel for coastal land fringe where region_map_0 is water
float nearest_province(vec2 uv) {
	vec2 texel = 1.0 / map_resolution;
	// Ring 1 (1 texel)
	float p = province_at(uv + vec2(texel.x, 0.0));
	if (p > 0.5) return p;
	p = province_at(uv - vec2(texel.x, 0.0));
	if (p > 0.5) return p;
	p = province_at(uv + vec2(0.0, texel.y));
	if (p > 0.5) return p;
	p = province_at(uv - vec2(0.0, texel.y));
	if (p > 0.5) return p;
	// Ring 2 (diagonals & 2 texels)
	p = province_at(uv + vec2(texel.x, texel.y));
	if (p > 0.5) return p;
	p = province_at(uv + vec2(-texel.x, texel.y));
	if (p > 0.5) return p;
	p = province_at(uv + vec2(texel.x, -texel.y));
	if (p > 0.5) return p;
	p = province_at(uv + vec2(-texel.x, -texel.y));
	if (p > 0.5) return p;
	p = province_at(uv + vec2(texel.x * 2.0, 0.0));
	if (p > 0.5) return p;
	p = province_at(uv - vec2(texel.x * 2.0, 0.0));
	if (p > 0.5) return p;
	p = province_at(uv + vec2(0.0, texel.y * 2.0));
	if (p > 0.5) return p;
	p = province_at(uv - vec2(0.0, texel.y * 2.0));
	if (p > 0.5) return p;
	// Ring 3 & 4 (3 to 4 texels)
	p = province_at(uv + vec2(texel.x * 3.0, 0.0));
	if (p > 0.5) return p;
	p = province_at(uv - vec2(texel.x * 3.0, 0.0));
	if (p > 0.5) return p;
	p = province_at(uv + vec2(0.0, texel.y * 3.0));
	if (p > 0.5) return p;
	p = province_at(uv - vec2(0.0, texel.y * 3.0));
	if (p > 0.5) return p;
	p = province_at(uv + vec2(texel.x * 4.0, 0.0));
	if (p > 0.5) return p;
	p = province_at(uv - vec2(texel.x * 4.0, 0.0));
	if (p > 0.5) return p;
	p = province_at(uv + vec2(0.0, texel.y * 4.0));
	if (p > 0.5) return p;
	p = province_at(uv - vec2(0.0, texel.y * 4.0));
	if (p > 0.5) return p;
	return 0.0;
}

// ============================================================
// Cartography: boundary SDF + pair-based coverage (inlined)
// ============================================================
struct MapCoverage {
	vec3 tint;
	float country_hit;
	float hover_hit;
	float state_hit;
	float province_hit;
	float country_distance;
	float state_distance;
	float province_distance;
	float selected_state_distance;
	float selected_province_distance;
	bool national_edge;
	bool state_edge;
	bool province_edge;
};

MapCoverage map_coverage(vec2 uv, float pid, float sid, float owner) {
	MapCoverage c;
	c.tint = sid > .5 ? texture(colors, lookup(sid)).rgb : vec3(0.0);
	c.country_hit = owner == selected_country && owner > .5 ? 1.0 : 0.0;
	c.hover_hit = owner == hovered_country && owner > .5 ? 1.0 : 0.0;
	c.state_hit = sid == selected_region && sid > .5 ? 1.0 : 0.0;
	c.province_hit = pid == selected_province && pid > .5 ? 1.0 : 0.0;
	c.country_distance = 10000.0;
	c.state_distance = 10000.0;
	c.province_distance = 10000.0;
	c.selected_state_distance = c.state_hit > .5 ? 10000.0 : -10000.0;
	c.selected_province_distance = c.province_hit > .5 ? 10000.0 : -10000.0;
	c.national_edge = false;
	c.state_edge = false;
	c.province_edge = false;

	if (physical_mode && camera_distance > 1.65 && !inspection_active && hovered_country < 0.5) return c;

	float hint = texture(boundary_hint, uv).r;
	if (hint <= .001) return c;

	// Read continuous signed distance to vector boundary
	highp float sd = texture(boundary_distance, uv).r;
	float footprint = max(fwidth(sd), .000001);
	float pixels = sd / footprint;

	// Read boundary province pair at uv
	vec2 size = vec2(textureSize(boundary_pairs, 0));
	vec4 p00 = texture(boundary_pairs, uv);
	if (all(equal(p00, vec4(0.0)))) {
		vec2 step = 1.0 / size;
		p00 = texture(boundary_pairs, uv + vec2(step.x, 0.0));
		if (all(equal(p00, vec4(0.0)))) p00 = texture(boundary_pairs, uv - vec2(step.x, 0.0));
		if (all(equal(p00, vec4(0.0)))) p00 = texture(boundary_pairs, uv + vec2(0.0, step.y));
		if (all(equal(p00, vec4(0.0)))) p00 = texture(boundary_pairs, uv - vec2(0.0, step.y));
	}

	if (any(greaterThan(p00, vec4(0.0)))) {
		vec4 bytes = floor(p00 * 255.0 + .5);
		float a = bytes.r + bytes.g * 256.0;
		float b = bytes.b + bytes.a * 256.0;
		vec4 ar = province_record(a);
		vec4 br = province_record(b);
		float sa = ar.r + ar.g * 256.0;
		float sb = br.r + br.g * 256.0;
		float oa = ar.b + ar.a * 256.0;
		float ob = br.b + br.a * 256.0;

		float h = smoothstep(-footprint * .65, footprint * .65, sd);
		vec3 ca = sa > .5 ? texture(colors, lookup(sa)).rgb : vec3(0.0);
		vec3 cb = sb > .5 ? texture(colors, lookup(sb)).rgb : vec3(0.0);

		// Smooth antialiased state fill transition along the vector curve
		c.tint = sa < .5 ? cb : (sb < .5 ? ca : mix(cb, ca, h));

		c.country_hit = (oa == selected_country && oa > .5 ? h : 0.0) + (ob == selected_country && ob > .5 ? 1.0 - h : 0.0);
		c.hover_hit = (oa == hovered_country && oa > .5 ? h : 0.0) + (ob == hovered_country && ob > .5 ? 1.0 - h : 0.0);

		bool ah = (sa == selected_region && sa > .5);
		bool bh = (sb == selected_region && sb > .5);
		c.state_hit = (ah ? h : 0.0) + (bh ? 1.0 - h : 0.0);
		c.selected_state_distance = (ah != bh) ? (ah ? pixels : -pixels) : (ah ? 10000.0 : -10000.0);

		ah = (a == selected_province && a > .5);
		bh = (b == selected_province && b > .5);
		c.province_hit = (ah ? h : 0.0) + (bh ? 1.0 - h : 0.0);
		c.selected_province_distance = (ah != bh) ? (ah ? pixels : -pixels) : (ah ? 10000.0 : -10000.0);

		c.national_edge = (oa != ob && oa > .5 && ob > .5);
		c.state_edge = (sa != sb && sa > .5 && sb > .5);
		c.province_edge = (a != b && a > .5 && b > .5 && sa == sb);

		c.country_distance = c.national_edge ? pixels : 10000.0;
		c.state_distance = c.state_edge ? pixels : 10000.0;
		c.province_distance = c.province_edge ? pixels : 10000.0;

		// Coastal edge: suppress internal border lines, extend land selection
		if (sa < .5 || sb < .5) {
			float land_state = sa > .5 ? sa : sb;
			float land_prov = sa > .5 ? a : b;
			float land_owner = sa > .5 ? oa : ob;
			c.state_hit = (land_state == selected_region && land_state > .5 ? 1.0 : 0.0);
			c.province_hit = (land_prov == selected_province && land_prov > .5 ? 1.0 : 0.0);
			c.country_hit = (land_owner == selected_country && land_owner > .5 ? 1.0 : 0.0);
			c.hover_hit = (land_owner == hovered_country && land_owner > .5 ? 1.0 : 0.0);
			c.selected_state_distance = c.state_hit > .5 ? 10000.0 : -10000.0;
			c.selected_province_distance = c.province_hit > .5 ? 10000.0 : -10000.0;
		}
	}

	return c;
}

// ============================================================
// Physical-mode helpers
// ============================================================
float patch_hash(vec2 p) {
	uvec2 q = uvec2(ivec2(p));
	uint h = q.x * uint(1597334677) ^ q.y * uint(1181783497);
	h = (h ^ (h >> uint(16))) * uint(747796405);
	h = (h ^ (h >> uint(13))) * uint(289133645);
	return float((h ^ (h >> uint(16))) & uint(16777215)) / 16777216.0;
}
float patch_noise(vec2 p) {
	vec2 i = floor(p), f = fract(p); f = f * f * (3.0 - 2.0 * f);
	return mix(mix(patch_hash(i), patch_hash(i + vec2(1, 0)), f.x), mix(patch_hash(i + vec2(0, 1)), patch_hash(i + vec2(1, 1)), f.x), f.y);
}
vec3 varied_sample(float layer, vec2 uv, float phase, vec2 dx, vec2 dy) {
	float i = floor(phase);
	vec2 a = vec2(patch_hash(vec2(i, layer)), patch_hash(vec2(layer + 19.0, i))) * 37.0;
	return textureGrad(terrain_materials, vec3(uv + a, layer), dx, dy).rgb;
}
vec3 material(float layer, vec3 position, vec3 phase, vec3 dx, vec3 dy) {
	vec3 w = pow(abs(normalize(position)), vec3(6.0)); w /= max(.00001, w.x + w.y + w.z);
	w = max(w - vec3(.025), vec3(0.0)); w /= w.x + w.y + w.z;
	vec3 a = vec3(0.0), b = vec3(0.0), c = vec3(0.0);
	if (w.x > .001) a = varied_sample(layer, position.yz, phase.x, dx.yz, dy.yz);
	if (w.y > .001) b = varied_sample(layer, position.xz, phase.y, dx.xz, dy.xz);
	if (w.z > .001) c = varied_sample(layer, position.xy, phase.z, dx.xy, dy.xy);
	return a * w.x + b * w.y + c * w.z;
}
vec3 biome_at(vec2 uv) {
	vec2 size = vec2(textureSize(terrain_types, 0));
	vec2 at = uv * size - .5;
	vec2 origin = (floor(at) + .5) / size;
	vec2 f = fract(at);
	vec4 entries[4];
	entries[0] = texture(terrain_types, origin);
	entries[1] = texture(terrain_types, origin + vec2(1.0 / size.x, 0.0));
	entries[2] = texture(terrain_types, origin + vec2(0.0, 1.0 / size.y));
	entries[3] = texture(terrain_types, origin + 1.0 / size);
	float influence[4];
	influence[0] = (1.0 - f.x) * (1.0 - f.y); influence[1] = f.x * (1.0 - f.y);
	influence[2] = (1.0 - f.x) * f.y; influence[3] = f.x * f.y;
	float best = 0.0; float next = 0.0; float first = 0.0; float second = 0.0;
	for (int category = 0; category < 8; category++) {
		float total = 0.0;
		for (int corner = 0; corner < 4; corner++) {
			float a = floor(entries[corner].r * 255.0 + .5);
			float b = floor(entries[corner].g * 255.0 + .5);
			total += influence[corner] * ((a == float(category) ? 1.0 - entries[corner].b : 0.0) + (b == float(category) ? entries[corner].b : 0.0));
		}
		if (total > best) { next = best; second = first; best = total; first = float(category); }
		else if (total > next) { next = total; second = float(category); }
	}
	return vec3(first, second, next / max(best + next, .00001));
}

// ============================================================
// Vertex
// ============================================================
void vertex() {
	cartography_uv = UV;
	float lon = (UV.x - .5) * 6.28318530718, lat = (.5 - UV.y) * 3.14159265359;
	vec3 n = vec3(cos(lat) * sin(lon), sin(lat), cos(lat) * cos(lon));
	geographic_normal = n;
	VERTEX = n * (1.0 + relief(UV));
	NORMAL = n;
	radial_world = normalize(mat3(MODEL_MATRIX) * n);
	east_world = normalize(mat3(MODEL_MATRIX) * vec3(cos(lon), 0.0, -sin(lon)));
	north_world = normalize(mat3(MODEL_MATRIX) * vec3(-sin(lat) * sin(lon), cos(lat), -sin(lat) * cos(lon)));
}

// ============================================================
// Fragment
// ============================================================
void fragment() {
	highp vec2 uv = vec2(fract(cartography_uv.x), clamp(cartography_uv.y, .000001, .999999));
	float facing = clamp(dot(normalize(NORMAL), normalize(VIEW)), 0.0, 1.0);
	vec3 water = mix(vec3(.025, .105, .18), vec3(.075, .27, .39), facing);
	float passage_id = water_passage(uv);
	float pid = passage_id > 0.0 ? 0.0 : province_at(uv);

	float coast_value = texture(coast_distance, uv).r;
	float land_coverage = coverage_alpha(coast_value);
	if (land_coverage < .999 && small_land_at(floor(uv * map_resolution)) > .5) {
		vec2 pixel2 = uv * map_resolution - .5, corner = floor(pixel2), weight = fract(pixel2);
		float row0 = mix(small_land_at(corner), small_land_at(corner + vec2(1.0, 0.0)), weight.x);
		float row1 = mix(small_land_at(corner + vec2(0.0, 1.0)), small_land_at(corner + vec2(1.0)), weight.x);
		land_coverage = max(land_coverage, coverage_alpha(mix(row0, row1, weight.y)));
	}
	if (passage_id > 0.0) land_coverage = 0.0;

	// Fill in province for smoothed coastal land fringe
	if (pid < 0.5 && land_coverage > 0.001) {
		pid = nearest_province(uv);
	}

	vec4 rec = province_record(pid);
	float region = rec.r + rec.g * 256.0;
	float owner = rec.b + rec.a * 256.0;
	MapCoverage coverage = map_coverage(uv, pid, region, owner);
	bool chosen = inspection_active && owner > 0.0 && owner == selected_country;
	vec2 texel = 1.0 / map_resolution;
	vec2 pixel = uv * map_resolution - .5;
	vec2 origin = (floor(pixel) + .5) * texel;
	vec2 blend = fract(pixel);
	vec2 dx = dFdx(uv) * .3 * far_filter;
	vec2 dy = dFdy(uv) * .3 * far_filter;

	// Political surface colour
	vec4 surface = vec4(water, 0.0);
	if (!physical_mode && !information_mode && region > .5) surface = vec4(coverage.tint, 1.0);
	else if (!physical_mode) {
		vec4 c00 = color_at(mix(origin, uv - dx - dy, far_filter), water);
		vec4 c10 = color_at(mix(origin + vec2(texel.x, 0), uv + dx - dy, far_filter), water);
		vec4 c01 = color_at(mix(origin + vec2(0, texel.y), uv - dx + dy, far_filter), water);
		vec4 c11 = color_at(mix(origin + texel, uv + dx + dy, far_filter), water);
		blend = mix(blend, vec2(.5), far_filter);
		surface = mix(mix(c00, c10, blend.x), mix(c01, c11, blend.x), blend.y);
		if (passage_id > 0.0) surface = vec4(water, 0.0);
	}

	vec3 land_color = clamp((surface.rgb - water * (1.0 - surface.a)) / max(.0001, surface.a), vec3(0.0), vec3(1.0));
	if (surface.a < .001 && land_coverage > .001 && !physical_mode && region > .5) {
		land_color = coverage.tint;
	}
	float selected_hit = coverage.country_hit;
	float hovered_hit = coverage.hover_hit;
	vec3 country_tint = coverage.tint;
	float national_band = coverage.national_edge ? 1.0 - smoothstep(1.5, 10.0, abs(coverage.country_distance)) : 0.0;
	if (!physical_mode && !information_mode && region > .5) land_color = country_tint;
	vec3 base = mix(water, land_color, land_coverage);

#ifdef PHYSICAL_MAP
	if (physical_mode && land_coverage > .001) {
		vec3 earth = texture(terrain_color, uv).rgb;
		vec3 types = vec3(0.0);
		if (terrain_mix > .001) types = biome_at(uv);
		float primary = types.r;
		float secondary = types.g;
		vec3 n = normalize(geographic_normal);
		vec3 material_position = n * 2600.0;
		vec3 material_phase = vec3(0.0);
		vec3 urban_dx = dFdx(n) * 430.0, urban_dy = dFdy(n) * 430.0;
		float close = smoothstep(0.0, 1.0, terrain_mix);
		vec3 pattern = vec3(.5);
		if (close > .001) {
			vec3 warp = vec3(patch_noise(material_position.xy * .65 + 13.0), patch_noise(material_position.yz * .65 + 37.0), patch_noise(material_position.zx * .65 + 59.0));
			material_position += (warp - .5) * .22;
			material_phase = warp * 7.0;
		}
		vec3 material_dx = dFdx(material_position), material_dy = dFdy(material_position);
		if (close > .001) {
			pattern = material(primary, material_position, material_phase, material_dx, material_dy);
			// OPTIMISATION: skip secondary biome blend when weight is negligible
			if (types.b > .18 && primary != secondary && types.b > .1)
				pattern = mix(pattern, material(secondary, material_position, material_phase, material_dx, material_dy), types.b);
		}
		earth = mix(earth, mix(earth * pattern * 1.6, pattern, .48), close * .88);
		float far_blend = far_terrain_enabled ? smoothstep(1.22, 1.48, camera_distance) : 0.0;
		vec3 relief_normal = radial_world;
		float snow = 0.0;
		if (far_blend < 1.0) {
			vec4 elev = texture(relief_data, uv);
			float meters = elev.b * 9000.0;
			vec2 step = 1.0 / vec2(textureSize(relief_data, 0));
			float slope_e = (relief(uv + vec2(step.x, 0)) - relief(uv - vec2(step.x, 0))) / (2.0 * step.x * 6.28318530718 * max(.08, sin(uv.y * 3.14159265359)));
			float slope_n = (relief(uv + vec2(0, step.y)) - relief(uv - vec2(0, step.y))) / (2.0 * step.y * 3.14159265359);
			relief_normal = normalize(radial_world - east_world * slope_e + north_world * slope_n);
			float steep = length(vec2(slope_e, slope_n));
			float dry = (primary == 3.0 ? 1.0 - types.b : 0.0) + (secondary == 3.0 ? types.b : 0.0);
			float icy = (primary == 6.0 ? 1.0 - types.b : 0.0) + (secondary == 6.0 ? types.b : 0.0);
			// OPTIMISATION: skip rock exposure at far zoom
			if (far_blend < 0.5) {
				float exposed = max(smoothstep(.25, .95, steep), smoothstep(2900.0, 5400.0, meters)) * (1.0 - dry * .65) * (1.0 - icy);
				if (exposed * close * (1.0 - far_blend) > .01)
					earth = mix(earth, material(5.0, material_position, material_phase, material_dx, material_dy) * .72 + vec3(.10), exposed * .40 * close * (1.0 - far_blend));
			}
			float snowline = mix(4700.0, 1700.0, smoothstep(.25, .85, abs(uv.y - .5) * 2.0));
			snow = smoothstep(snowline, snowline + 1000.0, meters) * (1.0 - smoothstep(.65, 1.25, steep));
		}
		if (far_blend > 0.0) {
			vec4 cached = texture(far_terrain, uv);
			vec2 xy = (cached.rg * 255.0 - vec2(128.0)) / 127.0;
			float z = sqrt(max(.000001, 1.0 - dot(xy, xy)));
			vec3 cached_normal = normalize(radial_world * z + east_world * xy.x + north_world * xy.y);
			relief_normal = normalize(mix(relief_normal, cached_normal, far_blend));
			snow = mix(snow, cached.b, far_blend);
			// OPTIMISATION: skip far-zoom rock for cached terrain
			if (far_blend < 0.5) {
				float cached_dry = (primary == 3.0 ? 1.0 - types.b : 0.0) + (secondary == 3.0 ? types.b : 0.0);
				float cached_icy = (primary == 6.0 ? 1.0 - types.b : 0.0) + (secondary == 6.0 ? types.b : 0.0);
				float cached_exposed = cached.a * (1.0 - cached_dry * .65) * (1.0 - cached_icy);
				if (cached_exposed * close > .01) {
					vec3 rock_color = material(5.0, material_position, material_phase, material_dx, material_dy) * .72 + vec3(.10);
					earth = mix(earth, rock_color, cached_exposed * .40 * close * far_blend);
				}
			}
		}
		earth = mix(earth, vec3(.87, .91, .94), snow * .68);
		float urban = 0.0;
		if (city_detail > .001) urban = texture(urban_density, uv).r * city_detail;
		if (urban > .001) {
			vec3 up = n * 430.0;
			vec3 weights = pow(abs(n), vec3(8.0)); weights /= weights.x + weights.y + weights.z;
			vec3 blocks = textureGrad(urban_material, up.yz, urban_dx.yz, urban_dy.yz).rgb * weights.x + textureGrad(urban_material, up.xz, urban_dx.xz, urban_dy.xz).rgb * weights.y + textureGrad(urban_material, up.xy, urban_dx.xy, urban_dy.xy).rgb * weights.z;
			vec3 city = mix(vec3(.33, .35, .32), blocks * .9 + vec3(.05), .86);
			earth = mix(earth, city, urban * .78);
		}
		float physical_land = land_coverage;
		if (passage_id > 0.0) physical_land = 0.0;
		base = mix(water, earth, physical_land);
		float micro_h = dot(pattern, vec3(.299, .587, .114));
		float micro_bump = clamp((dFdx(micro_h) - dFdy(micro_h)) * 3.5, -0.28, 0.28) * close * physical_land;
		float sun = clamp(dot(relief_normal, normalize(vec3(-.42, .55, .72))) + micro_bump, -.75, 1.0);
		base *= .52 + .52 * smoothstep(-.5, .9, sun);
		float haze = pow(1.0 - facing, 2.8) * .29;
		base = mix(base, vec3(.18, .35, .49), haze);
		float coastal_band = 1.0 - smoothstep(1.5, 10.0, abs(field_pixels(coast_value)));
		float political_band = max(national_band * .20, coastal_band * .12);
		if (political_band > .002 && land_coverage > .001) {
			base = mix(base, country_tint, political_band * border_strength * land_coverage);
		}
	}
#endif

	// Selection/hover/border overlays (shared by all modes)
	if (inspection_active && !information_mode) { base = mix(base, vec3(.93, .85, .65), (physical_mode ? .055 : .09) * selected_hit * land_coverage); }
	float near = 1.0 - smoothstep(1.45, 1.65, camera_distance);
	float coast_px = field_pixels(coast_value);
	float ocean_coast = (abs(coast_px) < 8.0 || selected_sea > 0.0) ? ocean_nearby(uv) : 1.0;
	float inland = smoothstep(1.5, 3.0, coast_px);
	bool selected_state = inspection_active && selected_region > 0.0;
	bool selected_prov = inspection_active && selected_province > 0.0 && province_opacity > 0.0;
	if (selected_state) base = mix(base, vec3(.64, .82, .79), .13 * coverage.state_hit * land_coverage);
	if (hovered_country > 0.0) base = mix(base, vec3(.88, .87, .72), .055 * hover_amount * hovered_hit * (1.0 - selected_hit) * land_coverage);
	if (selected_prov) base = mix(base, vec3(.9, .98, 1.0), .07 * province_opacity * coverage.province_hit * land_coverage);
	float state_fade = (1.0 - smoothstep(1.42, 1.72, camera_distance)) * .52;
	if (!show_regions || (inspection_active && owner != selected_country)) state_fade = 0.0;
	if (coverage.national_edge) {
		vec3 ink = inspection_active && (coverage.country_hit > .001) ? vec3(.92, .84, .56) : (physical_mode ? vec3(.10, .13, .12) : vec3(.44, .48, .46));
		base = field_ink(base, coverage.country_distance, 3.0, ink, near * inland);
	} else if (coverage.state_edge) {
		vec3 ink = physical_mode ? vec3(.15, .18, .16) : vec3(.34, .39, .36);
		base = field_ink(base, coverage.state_distance, 1.8, ink, near * state_fade * inland);
	} else if (coverage.province_edge) {
		float fade = 1.0 - smoothstep(1.18, 1.35, camera_distance);
		if (selected_state && region == selected_region) fade = max(fade, 1.0 - smoothstep(1.36, 1.52, camera_distance));
		if (inspection_active && owner != selected_country) fade = 0.0;
		vec3 ink = physical_mode ? vec3(.18, .21, .19) : vec3(.30, .35, .31);
		base = field_ink(base, coverage.province_distance, 1.2, ink, near * fade * .65 * inland);
	}
	if (selected_state && abs(coverage.selected_state_distance) < 20.0)
		base = field_ink(base, coverage.selected_state_distance, 2.0, vec3(.70, .82, .79), near * inland);
	if (selected_prov && abs(coverage.selected_province_distance) < 20.0)
		base = field_ink(base, coverage.selected_province_distance, 1.6, vec3(.75, .87, .81), province_opacity * near * inland);
	// Coastline ink
	vec3 coast_ink = vec3(.34, .39, .36); float coast_width = 3.2;
	if (chosen) { coast_ink = vec3(.90, .81, .58); coast_width = 2.6; }
	if ((selected_state && coverage.state_hit > .30) || (selected_prov && coverage.province_hit > .30)) { coast_ink = vec3(.70, .82, .79); coast_width = 2.0; }
	if (ocean_coast < .5) { coast_ink = vec3(.22, .30, .29); coast_width = 1.1; }
	base = field_ink(base, coast_px, coast_width, coast_ink, near * (ocean_coast < .5 ? .45 : (physical_mode ? .8 : 1.0)));
	ALBEDO = base;
}
