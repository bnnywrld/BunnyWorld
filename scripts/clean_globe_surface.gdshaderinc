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
uniform sampler2D sea_map : filter_linear, repeat_disable;
uniform vec2 map_resolution = vec2(6144.0, 3072.0);

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

// --- Uniforms: sea selection coverage (from display_coverage.gd) ---
uniform sampler2D sea_coverage : filter_linear, repeat_disable;
uniform vec4 sea_coverage_rect = vec4(0.0);
uniform bool sea_coverage_enabled = false;

// --- Uniforms: material details ---
uniform sampler2D water_normal : filter_linear_mipmap, repeat_enable;
uniform sampler2D rock_detail : filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D farmland_detail : filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D swamp_detail : filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D tundra_detail : filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D savanna_detail : filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D chaparral_detail : filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D rice_paddy_detail : filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D badlands_detail : filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D conifer_detail : filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D rainforest_detail : filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D alluvium_detail : filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D mediterranean_detail : filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D urban_grid_material : source_color, filter_linear_mipmap, repeat_enable;
uniform sampler2D urban_asian_material : source_color, filter_linear_mipmap, repeat_enable;
uniform float city_growth = 1.0;

// --- Uniforms: map mode ---
uniform bool physical_mode = false;
uniform bool information_mode = false;
uniform bool show_regions = false;
uniform float region_opacity = 0.0;

// Cartographic style controls: shared defaults for game and sandbox.
uniform float country_tint_close = 0.10;
uniform float country_tint_far = 0.28;
uniform float country_ribbon_strength = 0.42;
uniform float coastal_shelf_strength = 0.32;
uniform float coastal_foam_strength = 0.30;
uniform float terrain_detail_strength = 0.72;

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
	// Ring 2 (2 texels)
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
	// Ring 3 (4 texels)
	p = province_at(uv + vec2(texel.x * 4.0, 0.0));
	if (p > 0.5) return p;
	p = province_at(uv - vec2(texel.x * 4.0, 0.0));
	if (p > 0.5) return p;
	p = province_at(uv + vec2(0.0, texel.y * 4.0));
	if (p > 0.5) return p;
	p = province_at(uv - vec2(0.0, texel.y * 4.0));
	if (p > 0.5) return p;
	p = province_at(uv + vec2(texel.x * 3.0, texel.y * 3.0));
	if (p > 0.5) return p;
	p = province_at(uv + vec2(-texel.x * 3.0, texel.y * 3.0));
	if (p > 0.5) return p;
	p = province_at(uv + vec2(texel.x * 3.0, -texel.y * 3.0));
	if (p > 0.5) return p;
	p = province_at(uv + vec2(-texel.x * 3.0, -texel.y * 3.0));
	if (p > 0.5) return p;
	// Ring 4 (8 texels)
	p = province_at(uv + vec2(texel.x * 8.0, 0.0));
	if (p > 0.5) return p;
	p = province_at(uv - vec2(texel.x * 8.0, 0.0));
	if (p > 0.5) return p;
	p = province_at(uv + vec2(0.0, texel.y * 8.0));
	if (p > 0.5) return p;
	p = province_at(uv - vec2(0.0, texel.y * 8.0));
	if (p > 0.5) return p;
	p = province_at(uv + vec2(texel.x * 6.0, texel.y * 6.0));
	if (p > 0.5) return p;
	p = province_at(uv + vec2(-texel.x * 6.0, texel.y * 6.0));
	if (p > 0.5) return p;
	p = province_at(uv + vec2(texel.x * 6.0, -texel.y * 6.0));
	if (p > 0.5) return p;
	p = province_at(uv + vec2(-texel.x * 6.0, -texel.y * 6.0));
	if (p > 0.5) return p;
	// Ring 5 (16 texels)
	p = province_at(uv + vec2(texel.x * 16.0, 0.0));
	if (p > 0.5) return p;
	p = province_at(uv - vec2(texel.x * 16.0, 0.0));
	if (p > 0.5) return p;
	p = province_at(uv + vec2(0.0, texel.y * 16.0));
	if (p > 0.5) return p;
	p = province_at(uv - vec2(0.0, texel.y * 16.0));
	if (p > 0.5) return p;
	p = province_at(uv + vec2(texel.x * 12.0, texel.y * 12.0));
	if (p > 0.5) return p;
	p = province_at(uv + vec2(-texel.x * 12.0, texel.y * 12.0));
	if (p > 0.5) return p;
	p = province_at(uv + vec2(texel.x * 12.0, -texel.y * 12.0));
	if (p > 0.5) return p;
	p = province_at(uv + vec2(-texel.x * 12.0, -texel.y * 12.0));
	if (p > 0.5) return p;
	return 0.0;
}

float tile_value(sampler2D field, vec4 rect, vec2 uv) {
	highp vec2 relative = uv - rect.xy;
	if (relative.x < 0.0) relative.x += 1.0;
	highp vec2 local = relative / max(rect.zw, vec2(0.0000001));
	if (any(lessThan(local, vec2(0.0))) || any(greaterThan(local, vec2(1.0)))) return 0.0;
	return texture(field, local).r;
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

	highp vec2 pixel = uv * map_resolution - 0.5;
	vec2 cell = floor(pixel);
	vec2 f = fract(pixel);
	vec2 sf = f * f * (3.0 - 2.0 * f);

	vec2 texel = 1.0 / map_resolution;
	vec2 c00 = (cell + vec2(0.5, 0.5)) * texel;
	vec2 c10 = c00 + vec2(texel.x, 0.0);
	vec2 c01 = c00 + vec2(0.0, texel.y);
	vec2 c11 = c00 + texel;

	float p00 = province_at(c00);
	float p10 = province_at(c10);
	float p01 = province_at(c01);
	float p11 = province_at(c11);

	// On coastal land fringes, substitute land province for water corner samples
	if (pid > 0.5) {
		if (p00 < 0.5) p00 = pid;
		if (p10 < 0.5) p10 = pid;
		if (p01 < 0.5) p01 = pid;
		if (p11 < 0.5) p11 = pid;
	}

	// Fast path: inside province away from boundaries (covers ~98% of globe)
	if (p00 == p10 && p00 == p01 && p00 == p11) {
		return c;
	}

	vec4 rec00 = province_record(p00);
	vec4 rec10 = province_record(p10);
	vec4 rec01 = province_record(p01);
	vec4 rec11 = province_record(p11);

	float s00 = rec00.r + rec00.g * 256.0;
	float s10 = rec10.r + rec10.g * 256.0;
	float s01 = rec01.r + rec01.g * 256.0;
	float s11 = rec11.r + rec11.g * 256.0;

	float o00 = rec00.b + rec00.a * 256.0;
	float o10 = rec10.b + rec10.a * 256.0;
	float o01 = rec01.b + rec01.a * 256.0;
	float o11 = rec11.b + rec11.a * 256.0;

	// Political tint smooth subpixel antialiasing across state boundaries
	if (s00 != s10 || s00 != s01 || s00 != s11) {
		vec3 ca = s00 > .5 ? texture(colors, lookup(s00)).rgb : vec3(0.0);
		vec3 cb = s10 > .5 ? texture(colors, lookup(s10)).rgb : vec3(0.0);
		vec3 cc = s01 > .5 ? texture(colors, lookup(s01)).rgb : vec3(0.0);
		vec3 cd = s11 > .5 ? texture(colors, lookup(s11)).rgb : vec3(0.0);
		c.tint = mix(mix(ca, cb, sf.x), mix(cc, cd, sf.x), sf.y);
	}

	// Selected state highlight & border distance (smooth continuous field, zero pixel steps)
	if (selected_region > 0.5) {
		float h00 = (s00 == selected_region) ? 1.0 : 0.0;
		float h10 = (s10 == selected_region) ? 1.0 : 0.0;
		float h01 = (s01 == selected_region) ? 1.0 : 0.0;
		float h11 = (s11 == selected_region) ? 1.0 : 0.0;
		float h_sel = mix(mix(h00, h10, sf.x), mix(h01, h11, sf.x), sf.y);
		float fw_sel = max(fwidth(h_sel), 0.00001);
		c.state_hit = (h00 != h10 || h00 != h01 || h00 != h11) ? smoothstep(-0.75, 0.75, (h_sel - 0.5) / fw_sel) : ((s00 == selected_region) ? 1.0 : 0.0);
		// State borders ONLY separate two land states. The coastline field defines the boundary against water.
		bool land_neighbor = (s00 > .5 && s00 != selected_region) ||
		                     (s10 > .5 && s10 != selected_region) ||
		                     (s01 > .5 && s01 != selected_region) ||
		                     (s11 > .5 && s11 != selected_region);
		if (land_neighbor && (h00 > .5 || h10 > .5 || h01 > .5 || h11 > .5)) {
			c.selected_state_distance = (h_sel - 0.5) / fw_sel;
		} else {
			c.selected_state_distance = 10000.0;
		}
	}

	// Selected & hovered country highlight (screen-space subpixel antialiasing)
	if (selected_country > 0.5) {
		float hc00 = (o00 == selected_country) ? 1.0 : 0.0;
		float hc10 = (o10 == selected_country) ? 1.0 : 0.0;
		float hc01 = (o01 == selected_country) ? 1.0 : 0.0;
		float hc11 = (o11 == selected_country) ? 1.0 : 0.0;
		float h_c = mix(mix(hc00, hc10, sf.x), mix(hc01, hc11, sf.x), sf.y);
		float fw_c = max(fwidth(h_c), 0.00001);
		c.country_hit = (hc00 != hc10 || hc00 != hc01 || hc00 != hc11) ? smoothstep(-0.75, 0.75, (h_c - 0.5) / fw_c) : ((o00 == selected_country) ? 1.0 : 0.0);
	}
	if (hovered_country > 0.5) {
		float hov00 = (o00 == hovered_country) ? 1.0 : 0.0;
		float hov10 = (o10 == hovered_country) ? 1.0 : 0.0;
		float hov01 = (o01 == hovered_country) ? 1.0 : 0.0;
		float hov11 = (o11 == hovered_country) ? 1.0 : 0.0;
		float h_hov = mix(mix(hov00, hov10, sf.x), mix(hov01, hov11, sf.x), sf.y);
		float fw_hov = max(fwidth(h_hov), 0.00001);
		c.hover_hit = (hov00 != hov10 || hov00 != hov01 || hov00 != hov11) ? smoothstep(-0.75, 0.75, (h_hov - 0.5) / fw_hov) : ((o00 == hovered_country) ? 1.0 : 0.0);
	}

	// Selected province highlight & distance
	if (selected_province > 0.5) {
		float hp00 = (p00 == selected_province) ? 1.0 : 0.0;
		float hp10 = (p10 == selected_province) ? 1.0 : 0.0;
		float hp01 = (p01 == selected_province) ? 1.0 : 0.0;
		float hp11 = (p11 == selected_province) ? 1.0 : 0.0;
		float h_p = mix(mix(hp00, hp10, sf.x), mix(hp01, hp11, sf.x), sf.y);
		float fw_p = max(fwidth(h_p), 0.00001);
		c.province_hit = (hp00 != hp10 || hp00 != hp01 || hp00 != hp11) ? smoothstep(-0.75, 0.75, (h_p - 0.5) / fw_p) : ((p00 == selected_province) ? 1.0 : 0.0);
		bool land_pneighbor = (p00 > .5 && p00 != selected_province) ||
		                      (p10 > .5 && p10 != selected_province) ||
		                      (p01 > .5 && p01 != selected_province) ||
		                      (p11 > .5 && p11 != selected_province);
		if (land_pneighbor && (hp00 > .5 || hp10 > .5 || hp01 > .5 || hp11 > .5)) {
			c.selected_province_distance = (h_p - 0.5) / fw_p;
		} else {
			c.selected_province_distance = 10000.0;
		}
	}

	// National borders (highest priority)
	bool nat_diff = (o00 != o10 || o00 != o01 || o00 != o11) && (o00 > .5 && o10 > .5 && o01 > .5 && o11 > .5);
	if (nat_diff) {
		float n00 = (o00 == owner) ? 1.0 : 0.0;
		float n10 = (o10 == owner) ? 1.0 : 0.0;
		float n01 = (o01 == owner) ? 1.0 : 0.0;
		float n11 = (o11 == owner) ? 1.0 : 0.0;
		float h_nat = mix(mix(n00, n10, sf.x), mix(n01, n11, sf.x), sf.y);
		float fw_nat = max(fwidth(h_nat), 0.0001);
		c.national_edge = true;
		c.country_distance = (h_nat - 0.5) / fw_nat;
	}

	// State borders (only within same nation)
	bool state_diff = (s00 != s10 || s00 != s01 || s00 != s11) && (s00 > .5 && s10 > .5 && s01 > .5 && s11 > .5);
	if (state_diff && !nat_diff) {
		float st00 = (s00 == sid) ? 1.0 : 0.0;
		float st10 = (s10 == sid) ? 1.0 : 0.0;
		float st01 = (s01 == sid) ? 1.0 : 0.0;
		float st11 = (s11 == sid) ? 1.0 : 0.0;
		float h_st = mix(mix(st00, st10, sf.x), mix(st01, st11, sf.x), sf.y);
		float fw_st = max(fwidth(h_st), 0.0001);
		c.state_edge = true;
		c.state_distance = (h_st - 0.5) / fw_st;
	}

	// Province borders (only within same state)
	bool prov_diff = (p00 != p10 || p00 != p01 || p00 != p11) && !state_diff && !nat_diff;
	if (prov_diff) {
		float pr00 = (p00 == pid) ? 1.0 : 0.0;
		float pr10 = (p10 == pid) ? 1.0 : 0.0;
		float pr01 = (p01 == pid) ? 1.0 : 0.0;
		float pr11 = (p11 == pid) ? 1.0 : 0.0;
		float h_pr = mix(mix(pr00, pr10, sf.x), mix(pr01, pr11, sf.x), sf.y);
		float fw_pr = max(fwidth(h_pr), 0.0001);
		c.province_edge = true;
		c.province_distance = (h_pr - 0.5) / fw_pr;
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

// --- HOI4 Overlay blend mode in gamma space ---
vec3 to_gamma(vec3 c) {
	return pow(max(c, vec3(0.0)), vec3(1.0 / 2.2));
}
vec3 to_linear(vec3 c) {
	return pow(max(c, vec3(0.0)), vec3(2.2));
}
vec3 get_overlay(vec3 base_color, vec3 overlay_color, float amount) {
	vec3 bg = to_gamma(base_color);
	vec3 og = to_gamma(overlay_color);
	vec3 res;
	res.r = og.r < 0.5 ? (2.0 * og.r * bg.r) : (1.0 - 2.0 * (1.0 - og.r) * (1.0 - bg.r));
	res.g = og.g < 0.5 ? (2.0 * og.g * bg.g) : (1.0 - 2.0 * (1.0 - og.g) * (1.0 - bg.g));
	res.b = og.b < 0.5 ? (2.0 * og.b * bg.b) : (1.0 - 2.0 * (1.0 - og.b) * (1.0 - bg.b));
	return mix(base_color, to_linear(clamp(res, vec3(0.0), vec3(1.0))), amount);
}

// --- Multi-biome sampling with farmland, rice paddies, conifer woods, badlands, swamp, savanna, chaparral, and tundra ---
vec3 sample_biome(float layer, vec2 uv_coord, vec2 dx_coord, vec2 dy_coord, vec2 globe_uv, float meters, float coast_dist) {
	float macro_var = patch_noise(globe_uv * vec2(110.0, 55.0));
	float micro_var = patch_noise(uv_coord * 0.05);

	// East Asia & Southeast Asia check (China, Japan, Korea, SE Asia):
	// Longitude 70E to 145E (globe_uv.x ~0.69 to 0.91), Latitude 10S to 48N (globe_uv.y ~0.23 to 0.58)
	bool is_east_asia = (globe_uv.x > 0.69 && globe_uv.x < 0.91 && globe_uv.y > 0.23 && globe_uv.y < 0.58);

	// Russian / Siberian Boreal Taiga check (Russia north of 52N):
	// Longitude 28E to 180E (globe_uv.x ~0.57 to 1.0), Latitude north of 52N (globe_uv.y < 0.21)
	bool is_russia_boreal = (globe_uv.x > 0.57 && globe_uv.y < 0.21);

	// 1. Farmland / Agriculture (layer 2):
	if (abs(layer - 2.0) < 0.5) {
		// In northern Russia & Siberia: Permafrost & taiga prevent agriculture! Render Siberian pine/larch taiga
		if (is_russia_boreal) {
			vec3 pine = textureGrad(conifer_detail, uv_coord, dx_coord, dy_coord).rgb;
			if (globe_uv.y < 0.14) {
				vec3 tund = textureGrad(tundra_detail, uv_coord, dx_coord, dy_coord).rgb;
				return mix(pine, tund, smoothstep(0.14, 0.10, globe_uv.y));
			}
			return pine;
		}
		vec3 ag_texture;
		if (is_east_asia) {
			// In East Asia, agriculture is Asian flooded rice paddy terraces!
			ag_texture = textureGrad(rice_paddy_detail, uv_coord, dx_coord, dy_coord).rgb;
		} else {
			// In Europe & Americas, agriculture uses the authentic European farmland mosaic (resident_2.png)
			ag_texture = textureGrad(farmland_detail, uv_coord, dx_coord, dy_coord).rgb;
		}
		
		// In coastal river deltas & floodplains (like Nile, Rhine, Mississippi), blend rich silt mudflats
		if (coast_dist < 10.0 && meters < 65.0) {
			vec3 silt = textureGrad(alluvium_detail, uv_coord, dx_coord, dy_coord).rgb;
			float wet_w = smoothstep(10.0, 1.5, coast_dist) * smoothstep(65.0, 8.0, meters);
			ag_texture = mix(ag_texture, silt, wet_w * 0.70);
		}
		return ag_texture;
	}

	// 2. Plains / Grassland (layer 4) - covers 71% of world map:
	if (abs(layer - 4.0) < 0.5) {
		// In northern Russia/Siberia: Plains at high latitudes are cold taiga and tundra, not farmland!
		if (is_russia_boreal) {
			vec3 pine = textureGrad(conifer_detail, uv_coord, dx_coord, dy_coord).rgb;
			vec3 tund = textureGrad(tundra_detail, uv_coord, dx_coord, dy_coord).rgb;
			return mix(pine, tund, smoothstep(0.16, 0.10, globe_uv.y));
		}
		vec3 grass;
		if (is_east_asia) {
			// In East Asia, plains are intensely cultivated rice paddies & agricultural mosaics
			vec3 paddy = textureGrad(rice_paddy_detail, uv_coord, dx_coord, dy_coord).rgb;
			vec3 farm = textureGrad(farmland_detail, uv_coord, dx_coord, dy_coord).rgb;
			grass = mix(paddy, farm, smoothstep(0.40, 0.70, micro_var) * 0.40);
		} else {
			// In Europe & Americas, agricultural plains use the authentic farmland mosaic (resident_2.png)
			vec3 farm = textureGrad(farmland_detail, uv_coord, dx_coord, dy_coord).rgb;
			vec3 pasture = textureGrad(terrain_materials, vec3(uv_coord, 4.0), dx_coord, dy_coord).rgb;
			grass = mix(farm, pasture, smoothstep(0.42, 0.82, macro_var) * 0.45);
		}
		// Coastal river deltas and floodplains: rich silt alluvium mudflats
		if (coast_dist < 10.0 && meters < 65.0) {
			vec3 silt = textureGrad(alluvium_detail, uv_coord, dx_coord, dy_coord).rgb;
			grass = mix(grass, silt, smoothstep(10.0, 2.0, coast_dist) * 0.65);
		}
		// Semi-arid scrub / chaparral / Mediterranean scrub (California, Spain, Italy, Greece, Chile)
		if (abs(globe_uv.y - 0.5) > 0.08 && abs(globe_uv.y - 0.5) < 0.28) {
			vec3 med = textureGrad(mediterranean_detail, uv_coord, dx_coord, dy_coord).rgb;
			vec3 chap = textureGrad(chaparral_detail, uv_coord, dx_coord, dy_coord).rgb;
			vec3 scrub = mix(med, chap, smoothstep(0.35, 0.65, micro_var));
			grass = mix(grass, scrub, smoothstep(0.40, 0.76, macro_var) * 0.65);
		}
		// Drier acacia savanna in tropical & subtropical latitudes (Texas, Florida, Sahel, Australia, Brazil)
		if (abs(globe_uv.y - 0.5) < 0.22) {
			vec3 sav = textureGrad(savanna_detail, uv_coord, dx_coord, dy_coord).rgb;
			grass = mix(grass, sav, smoothstep(0.38, 0.75, macro_var) * 0.70);
		}
		// Cold northern sub-polar tundra in high latitudes (globe_uv.y < 0.20, lat > 54N)
		if (globe_uv.y < 0.20) {
			vec3 tund = textureGrad(tundra_detail, uv_coord, dx_coord, dy_coord).rgb;
			grass = mix(grass, tund, smoothstep(0.20, 0.12, globe_uv.y));
		}
		return grass;
	}

	// 3. Mountain rock & alpine highlands (layer 5):
	if (abs(layer - 5.0) < 0.5) {
		vec3 r_macro = textureGrad(terrain_materials, vec3(uv_coord, 5.0), dx_coord, dy_coord).rgb;
		vec3 r_micro = textureGrad(rock_detail, uv_coord * 1.5, dx_coord * 1.5, dy_coord * 1.5).rgb;
		vec3 rock_base = mix(r_macro, r_micro * 0.95, 0.55);
		// Alpine tundra moss & cold weathered slate at high altitude
		if (meters > 1800.0) {
			vec3 tund = textureGrad(tundra_detail, uv_coord, dx_coord, dy_coord).rgb;
			float alt_w = smoothstep(1800.0, 3200.0, meters);
			rock_base = mix(rock_base, tund, alt_w * 0.70);
		}
		return rock_base;
	}

	// 4. Desert & Arid Lands (layer 3):
	if (abs(layer - 3.0) < 0.5) {
		vec3 sand = textureGrad(terrain_materials, vec3(uv_coord, 3.0), dx_coord, dy_coord).rgb;
		vec3 bad = textureGrad(badlands_detail, uv_coord, dx_coord, dy_coord).rgb;
		vec3 sav = textureGrad(savanna_detail, uv_coord, dx_coord, dy_coord).rgb;
		vec3 med = textureGrad(mediterranean_detail, uv_coord, dx_coord, dy_coord).rgb;
		// Break up dunes with badlands clay, semi-arid scrub and savanna margins
		vec3 arid_mix = mix(bad, mix(med, sav, micro_var), 0.50);
		return mix(sand, arid_mix, smoothstep(0.38, 0.78, macro_var) * 0.70);
	}

	// 5. Forest / Woodland (layers 0 & 1):
	if (layer < 1.5) {
		// Boreal / taiga conifers in northern latitudes (Canada, Russia, Scandinavia - lat > 42N)
		if (globe_uv.y < 0.27) {
			vec3 pine = textureGrad(conifer_detail, uv_coord, dx_coord, dy_coord).rgb;
			vec3 dec = textureGrad(terrain_materials, vec3(uv_coord, layer), dx_coord, dy_coord).rgb;
			return mix(dec, pine, smoothstep(0.27, 0.19, globe_uv.y));
		}
		return textureGrad(terrain_materials, vec3(uv_coord, layer), dx_coord, dy_coord).rgb;
	}

	// 6. Tropical Rainforest / Jungle (layer 7):
	if (abs(layer - 7.0) < 0.5) {
		vec3 j_old = textureGrad(terrain_materials, vec3(uv_coord, 7.0), dx_coord, dy_coord).rgb;
		vec3 j_new = textureGrad(rainforest_detail, uv_coord, dx_coord, dy_coord).rgb;
		return mix(j_old * 0.50 + j_new * 0.50, j_new, 0.85);
	}

	// Snow (layer 6):
	return textureGrad(terrain_materials, vec3(uv_coord, layer), dx_coord, dy_coord).rgb;
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
	float coast_px = field_pixels(coast_value);
	if (land_coverage < 0.999) {
		vec2 w_uv1 = uv * vec2(120.0, 60.0) + vec2(TIME * 0.008, TIME * 0.004);
		vec2 w_uv2 = uv * vec2(220.0, 110.0) - vec2(TIME * 0.006, TIME * 0.009);
		vec3 wn1 = texture(water_normal, w_uv1).rgb * 2.0 - 1.0;
		vec3 wn2 = texture(water_normal, w_uv2).rgb * 2.0 - 1.0;
		vec3 wave_n = normalize(wn1 + wn2 * 0.75);
		vec3 sun_dir_w = normalize(vec3(-0.52, 0.62, 0.58));
		vec3 half_v = normalize(sun_dir_w + normalize(VIEW));
		float spec_angle = max(dot(normalize(NORMAL + wave_n * 0.16), half_v), 0.0);
		float specular = pow(spec_angle, 26.0) * 0.22;
		float wave_diff = clamp(dot(wave_n.xy, vec2(-0.5, 0.5)), -0.22, 0.22);
		water = mix(water, water * (1.0 + wave_diff * 0.40) + vec3(specular), (1.0 - land_coverage) * (physical_mode ? 1.0 : 0.40));

		// Feature A: Shoreline wave surf & shallow turquoise water shelf (HOI4 coastal surf)
		if (land_coverage < 0.98) {
			float surf_fade = smoothstep(1.75, 1.35, camera_distance);
			float geo_shelf = smoothstep(0.40, 0.498, coast_value);
			float px_shelf = smoothstep(9.0, 1.0, -coast_px) * smoothstep(2.0, 1.4, camera_distance);
			float shelf = max(geo_shelf * 0.30, px_shelf);
			vec3 shelf_color = mix(water, vec3(0.08, 0.29, 0.34), coastal_shelf_strength);
			water = mix(water, shelf_color, shelf * (1.0 - land_coverage));
			// Animated multi-band shoreline wave surf foam: ONLY visible at close zoom (camera_distance < 1.75)
			if (surf_fade > 0.001) {
				float wave1 = sin(TIME * 2.8 - coast_px * 0.8) * 0.5 + 0.5;
				float wave2 = sin(TIME * 1.9 + coast_px * 1.2 + 2.1) * 0.5 + 0.5;
				float surf_band1 = smoothstep(6.0, 1.2, -coast_px) * smoothstep(0.30, 0.80, wave1);
				float surf_band2 = smoothstep(14.0, 3.5, -coast_px) * smoothstep(0.50, 0.95, wave2);
				float surf = max(surf_band1, surf_band2 * 0.60) * shelf * surf_fade;
				water = mix(water, vec3(0.90, 0.96, 1.0), surf * coastal_foam_strength * (1.0 - land_coverage));
			}
		}
	}
	// Only apply tiny-island recovery for isolated micro-islands where continuous SDF has near-zero coverage
	if (coast_value < 0.38 && small_land_at(floor(uv * map_resolution)) > .5) {
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
	// Ocean-neighbor taps only affect the narrow coastal bands below.
	float is_ocean = 0.0;
	if (abs(coast_px) < 22.0 || selected_sea > 0.0) {
		is_ocean = smoothstep(0.12, 0.65, ocean_nearby(uv));
	}
	float coast_inland = (coast_px > 0.0) ? (1.0 - smoothstep(1.0, 12.0, coast_px)) * smoothstep(0.0, 1.2, coast_px) * is_ocean : 0.0;
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
		vec3 urban_dx = dFdx(n) * 430.0, urban_dy = dFdy(n) * 430.0;
		float close = smoothstep(0.0, 1.0, terrain_mix);
		vec4 elev = texture(relief_data, uv);
		float meters = elev.b * 9000.0;

		// Conformal Mercator projection: mathematically strictly preserves 90-degree angles and shape ratios
		// Completely eliminates the diagonal shearing streaks across latitude lines
		float lat_rad = clamp((0.5 - uv.y) * 3.14159265359, -1.48, 1.48);
		float merc_y = log(tan(0.78539816339 + lat_rad * 0.5));
		vec2 tile_coord = vec2(fract(uv.x) * 6.28318530718, -merc_y) * 58.0;
		vec2 tile_dx = dFdx(cartography_uv) * vec2(6.28318530718, -3.14159265359 / max(cos(lat_rad), 0.08)) * 58.0;
		vec2 tile_dy = dFdy(cartography_uv) * vec2(6.28318530718, -3.14159265359 / max(cos(lat_rad), 0.08)) * 58.0;

		vec3 pattern = vec3(.5);
		if (close > .001) {
			pattern = sample_biome(primary, tile_coord, tile_dx, tile_dy, uv, meters, coast_px);
			// Smooth secondary biome blend between adjacent provinces (continuous seamless transition)
			if (types.b > .04 && primary != secondary) {
				vec3 sec_sample = sample_biome(secondary, tile_coord, tile_dx, tile_dy, uv, meters, coast_px);
				float blend_w = smoothstep(0.08, 0.92, types.b);
				pattern = mix(pattern, sec_sample, blend_w);
			}

			// Multi-Biome Terrain Modulation:
			// Combine the crisp, high-resolution physical detail and vivid colors of the biomes
			// with the regional climate tones of the NASA Earth colormap (green in PA/FL, dry brown in NV).
			// Keep regional colour dominant; detail provides texture rather than
			// replacing the climate palette with a contrasting tile.
			vec3 textured = mix(earth * (pattern * 1.45), pattern, 0.30);
			earth = mix(earth, textured, close * terrain_detail_strength);
		}
		float far_blend = far_terrain_enabled ? smoothstep(1.22, 1.48, camera_distance) : 0.0;
		vec3 relief_normal = radial_world;
		float snow = 0.0;
		if (far_blend < 1.0) {
			vec2 step = 2.0 / vec2(textureSize(relief_data, 0));
			float slope_e = (relief(uv + vec2(step.x, 0)) - relief(uv - vec2(step.x, 0))) / (2.0 * step.x * 6.28318530718 * max(.08, sin(uv.y * 3.14159265359)));
			float slope_n = (relief(uv + vec2(0, step.y)) - relief(uv - vec2(0, step.y))) / (2.0 * step.y * 3.14159265359);
			relief_normal = normalize(radial_world - east_world * slope_e * 3.2 + north_world * slope_n * 3.2);
			float steep = length(vec2(slope_e, slope_n));
			float dry = (primary == 3.0 ? 1.0 - types.b : 0.0) + (secondary == 3.0 ? types.b : 0.0);
			float icy = (primary == 6.0 ? 1.0 - types.b : 0.0) + (secondary == 6.0 ? types.b : 0.0);
			// Rock exposure on steep slopes and high elevation
			if (far_blend < 0.5) {
				float exposed = max(smoothstep(.25, .95, steep), smoothstep(2900.0, 5400.0, meters)) * (1.0 - dry * .65) * (1.0 - icy);
				if (exposed * close * (1.0 - far_blend) > .01) {
					vec3 rock_color = sample_biome(5.0, tile_coord, tile_dx, tile_dy, uv, meters, coast_px) * 0.75 + vec3(0.08);
					earth = mix(earth, rock_color, exposed * .50 * close * (1.0 - far_blend));
				}
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
			// Rock exposure for cached terrain
			if (far_blend < 0.5) {
				float cached_dry = (primary == 3.0 ? 1.0 - types.b : 0.0) + (secondary == 3.0 ? types.b : 0.0);
				float cached_icy = (primary == 6.0 ? 1.0 - types.b : 0.0) + (secondary == 6.0 ? types.b : 0.0);
				float cached_exposed = cached.a * (1.0 - cached_dry * .65) * (1.0 - cached_icy);
				if (cached_exposed * close > .01) {
					vec3 rock_color = sample_biome(5.0, tile_coord, tile_dx, tile_dy, uv, meters, coast_px) * 0.75 + vec3(0.08);
					earth = mix(earth, rock_color, cached_exposed * .40 * close * far_blend);
				}
			}
		}
		earth = mix(earth, vec3(.87, .91, .94), snow * .68);
		float urban_raw = 0.0;
		if (city_detail > .001) {
			// Domain warp breaks geometric ellipses into organic city sprawl & transport arteries
			vec2 urban_warp = vec2(
				patch_noise(uv * vec2(1400.0, 700.0) + 17.3),
				patch_noise(uv * vec2(1400.0, 700.0) + 53.1)
			) - vec2(0.5);
			urban_raw = texture(urban_density, uv + urban_warp * 0.0016).r;
		}
		if (urban_raw > .16 && city_detail > .001) {
			vec3 up = n * 430.0;
			vec3 weights = pow(abs(n), vec3(8.0)); weights /= weights.x + weights.y + weights.z;

			// East Asian cities: China, Japan, Korea, Taiwan, Hong Kong, Vietnam
			bool is_asian_country = (owner == 44.0 || owner == 108.0 || owner == 112.0 || owner == 113.0 || owner == 230.0 || owner == 197.0 || owner == 227.0);
			bool is_asian_region = (uv.x > 0.68 && uv.x < 0.94 && uv.y > 0.18 && uv.y < 0.62);
			bool use_asian = is_asian_country || (owner < 0.5 && is_asian_region);

			// American / Canadian / Australian / NZ grid cities:
			bool is_grid_country = (owner == 214.0 || owner == 34.0 || owner == 12.0 || owner == 144.0);
			bool is_grid_region = (uv.x > 0.03 && uv.x < 0.35 && uv.y > 0.08 && uv.y < 0.44) || (uv.x > 0.78 && uv.y > 0.55 && uv.y < 0.78);
			bool use_grid = is_grid_country || (owner < 0.5 && is_grid_region);

			vec3 blocks;
			if (use_asian) {
				blocks = textureGrad(urban_asian_material, up.yz, urban_dx.yz, urban_dy.yz).rgb * weights.x +
				         textureGrad(urban_asian_material, up.xz, urban_dx.xz, urban_dy.xz).rgb * weights.y +
				         textureGrad(urban_asian_material, up.xy, urban_dx.xy, urban_dy.xy).rgb * weights.z;
			} else if (use_grid) {
				blocks = textureGrad(urban_grid_material, up.yz, urban_dx.yz, urban_dy.yz).rgb * weights.x +
				         textureGrad(urban_grid_material, up.xz, urban_dx.xz, urban_dy.xz).rgb * weights.y +
				         textureGrad(urban_grid_material, up.xy, urban_dx.xy, urban_dy.xy).rgb * weights.z;
			} else {
				blocks = textureGrad(urban_material, up.yz, urban_dx.yz, urban_dy.yz).rgb * weights.x +
				         textureGrad(urban_material, up.xz, urban_dx.xz, urban_dy.xz).rgb * weights.y +
				         textureGrad(urban_material, up.xy, urban_dx.xy, urban_dy.xy).rgb * weights.z;
			}
			vec3 city = mix(vec3(.28, .30, .29), blocks * .92 + vec3(.04), .88);
			// Higher threshold contracts smaller cities so they hug their building clusters,
			// with organic edges preventing geometric circular spots
			float urban_threshold = mix(0.20, 0.12, clamp(city_growth - 1.0, 0.0, 1.0));
			float urban_opacity = smoothstep(urban_threshold, urban_threshold + 0.18, urban_raw) * city_detail;
			earth = mix(earth, city, urban_opacity * 0.95);
		}
		float physical_land = land_coverage;
		if (passage_id > 0.0) physical_land = 0.0;
		base = mix(water, earth, physical_land);

		// Mountain & hill relief lighting + valley ambient occlusion (smooth, clean, zero pixel noise)
		vec3 sun_dir = normalize(vec3(-0.52, 0.62, 0.58));
		float sun = clamp(dot(relief_normal, sun_dir), -0.75, 1.0);
		float valley_ao = clamp(dot(relief_normal, radial_world) * 0.85 + 0.25, 0.50, 1.0);
		float sun_light = smoothstep(-0.45, 0.85, sun);
		base *= mix(0.64, 1.12, sun_light) * mix(1.0, valley_ao, 0.70);
		// Atmospheric horizon limb gradient
		float horizon_limb = pow(1.0 - facing, 2.6) * 0.35;
		base = mix(base, vec3(0.18, 0.45, 0.68), horizon_limb);

		// 4. Realistic Earth color grading (calibrated to HOI4 / orbital photo reference)
		if (physical_land > 0.001) {
			float l = dot(base, vec3(0.299, 0.587, 0.114));
			// Tone down hyper-saturation: pull back by 14% towards natural earth tones
			base = mix(vec3(l), base, 0.86);
			// Natural atmospheric curve (cool shadows, warm highlights, no radioactive yellow)
			base = pow(base, vec3(1.02, 1.00, 0.96));
			// Soft gentle contrast S-curve
			base = mix(base, base * base * (3.0 - 2.0 * base), 0.12);
		}
		// Restrained political tint preserves terrain and country readability at every zoom.
		if (region > 0.5 && owner > 0.5 && physical_land > 0.001) {
			// Retain a light interior tint at close zoom, increasing towards orbit.
			float interior_strength = mix(country_tint_close, country_tint_far, smoothstep(1.18, 1.85, camera_distance));

			// Border ribbon: along international land borders
			float border_band = coverage.national_edge ? (1.0 - smoothstep(1.0, 10.0, abs(coverage.country_distance))) : 0.0;
			// Coastline ribbon: along the country's sea coast
			float coast_band = (coast_px > 0.0) ? (1.0 - smoothstep(1.0, 8.0, coast_px)) * is_ocean : 0.0;
			float ribbon_band = max(border_band, coast_band);

			// Narrow border ribbons distinguish neighbours without painting a wide halo.
			float ribbon_strength = ribbon_band * country_ribbon_strength * border_strength;

			float tilt_fade = mix(0.80, 1.0, smoothstep(0.15, 0.50, facing));
			float total_strength = clamp(interior_strength * (1.0 - ribbon_band) + ribbon_strength, 0.0, 0.88) * tilt_fade;

			float lum = dot(base, vec3(0.299, 0.587, 0.114));
			vec3 tint_filter = country_tint * (0.45 + 0.85 * lum);
			base = mix(base, tint_filter, total_strength * physical_land);
		}
	}
#endif

	// Distant atmospheric haze over land (clean, smooth ocean without cloudy smudges)
	if (physical_mode && camera_distance > 1.65 && land_coverage > 0.01) {
		float cloud_fade = smoothstep(1.65, 2.50, camera_distance);
		vec2 cloud_uv = uv * vec2(1.0, 0.5) * 28.0 + vec2(TIME * 0.002, 0.0);
		float c_noise = patch_noise(cloud_uv) * 0.60 + patch_noise(cloud_uv * 2.2 + vec2(7.3, 11.1)) * 0.40;
		float clouds = smoothstep(0.58, 0.85, c_noise) * cloud_fade * 0.22 * land_coverage;
		base = mix(base, vec3(0.92, 0.95, 0.98), clouds);
	}

	// Sea selection highlight (aquatic azure tint + luminous cyan boundary)
	float sea_val = sea_coverage_enabled ? tile_value(sea_coverage, sea_coverage_rect, uv) : 0.0;
	float sea_hit = (selected_sea > 0.0 && sea_coverage_enabled) ? coverage_alpha(sea_val) * (1.0 - land_coverage) : 0.0;
	if (selected_sea > 0.0 && sea_hit > 0.001) {
		float sea_edge = 1.0 - smoothstep(1.0, 12.0, abs(field_pixels(sea_val)));
		vec3 sea_glow = mix(vec3(0.08, 0.45, 0.65), vec3(0.35, 0.78, 0.95), sea_edge);
		base = mix(base, sea_glow, (0.28 + 0.32 * sea_edge) * sea_hit);
	}

	// Selection/hover/border overlays (shared by all modes)
	if (inspection_active && !information_mode) {
		base = mix(base, vec3(.93, .85, .65), (physical_mode ? .045 : .09) * selected_hit * land_coverage);
	}
	float select_coast_glow = coast_inland * selected_hit * land_coverage;
	if (inspection_active && select_coast_glow > 0.001) {
		base = mix(base, vec3(0.90, 0.81, 0.58), select_coast_glow * 0.32);
	}
	if (hovered_country > 0.0 && hover_amount > 0.0) {
		float hover_coast_glow = coast_inland * hovered_hit * hover_amount * (1.0 - selected_hit) * land_coverage;
		base = mix(base, vec3(0.88, 0.87, 0.72), (0.045 * hovered_hit + hover_coast_glow * 0.22) * land_coverage);
	}
	bool selected_state = inspection_active && selected_region > 0.0;
	bool selected_prov = inspection_active && selected_province > 0.0 && province_opacity > 0.0;
	if (selected_state) {
		base = mix(base, vec3(0.96, 0.94, 0.88), (0.07 * coverage.state_hit + coast_inland * coverage.state_hit * 0.20) * land_coverage);
	}
	if (selected_prov) base = mix(base, vec3(0.93, 0.85, 0.30), 0.12 * province_opacity * coverage.province_hit * land_coverage);
	float near = 1.0 - smoothstep(1.45, 1.65, camera_distance);
	float ocean_coast = (abs(coast_px) < 8.0 || selected_sea > 0.0) ? is_ocean : 1.0;
	// Border lines are rendered via 3D vector ribbon meshes (Option A: true HOI4 rounded borders)
	// Coastline ink below is retained for crisp, physically-accurate land/sea boundaries.
	vec3 coast_ink = vec3(.34, .39, .36); float coast_width = 1.8;
	if (selected_hit > 0.10) {
		coast_ink = mix(coast_ink, vec3(0.90, 0.81, 0.58), smoothstep(0.10, 0.85, selected_hit) * smoothstep(0.15, 0.65, ocean_coast));
		coast_width = mix(coast_width, 2.2, selected_hit);
	}
	if (selected_sea > 0.0 && sea_val > 0.35) {
		coast_ink = mix(coast_ink, vec3(0.35, 0.78, 0.95), smoothstep(0.15, 0.65, ocean_coast));
		coast_width = max(coast_width, 2.4);
	}
	if (selected_state && coverage.state_hit > .30) {
		coast_ink = mix(coast_ink, vec3(0.96, 0.94, 0.88), smoothstep(0.15, 0.65, ocean_coast));
		coast_width = 2.4;
	}
	if (selected_prov && coverage.province_hit > .30) {
		coast_ink = mix(coast_ink, vec3(0.93, 0.85, 0.30), smoothstep(0.15, 0.65, ocean_coast));
		coast_width = 2.6;
	}
	coast_ink = mix(vec3(.22, .30, .29), coast_ink, smoothstep(0.15, 0.65, ocean_coast));
	coast_width = mix(1.1, coast_width, smoothstep(0.15, 0.65, ocean_coast));
	base = field_ink(base, coast_px, coast_width, coast_ink, near * mix(0.45, (physical_mode ? .8 : 1.0), smoothstep(0.15, 0.65, ocean_coast)));
	ALBEDO = base;
}
