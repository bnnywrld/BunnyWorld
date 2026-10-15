shader_type spatial;
render_mode unshaded, cull_back, depth_prepass_alpha;
uniform float visibility_alpha : hint_range(0.0, 1.0) = 0.0;
uniform bool windows_enabled = true;
varying vec3 local_normal;
void vertex() { local_normal = NORMAL; }
void fragment() {
    float light = 0.55 + 0.45 * max(dot(normalize(NORMAL), normalize(vec3(-0.4, 0.8, 0.5))), 0.0);
    vec3 base = COLOR.rgb;
    if (windows_enabled && abs(local_normal.y) < 0.5) {
        vec2 cell = fract(UV * vec2(4.0, 8.0));
        float window = step(0.2, cell.x) * step(cell.x, 0.73) * step(0.22, cell.y) * step(cell.y, 0.7);
        base = mix(base, vec3(0.19, 0.28, 0.32), window * 0.68);
    }
    ALBEDO = base * light;
    ALPHA = visibility_alpha;
}
