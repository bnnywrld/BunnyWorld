// One bounded subpixel enclave. No extra texture/sampler is needed.
uniform vec4 micro_bounds = vec4(0.0);
uniform vec2 micro_polygon[64];
uniform int micro_vertex_count = 0;
uniform float micro_province = -1.0;
uniform float micro_host_province = 0.0;
uniform float micro_region = -1.0;
float resolve_micro_province(vec2 uv, float coarse) {
    if (micro_vertex_count > 2 && uv.x >= micro_bounds.x && uv.y >= micro_bounds.y && uv.x <= micro_bounds.z && uv.y <= micro_bounds.w) {
        bool inside = false;
        vec2 previous = micro_polygon[micro_vertex_count - 1];
        for (int i = 0; i < 64; i++) {
            if (i >= micro_vertex_count) { break; }
            vec2 current = micro_polygon[i];
            if ((current.y > uv.y) != (previous.y > uv.y)) {
                float crossing = (previous.x - current.x) * (uv.y - current.y) / (previous.y - current.y) + current.x;
                if (uv.x < crossing) { inside = !inside; }
            }
            previous = current;
        }
        if (inside) { return micro_province; }
    }
    return abs(coarse - micro_province) < 0.5 ? micro_host_province : coarse;
}
