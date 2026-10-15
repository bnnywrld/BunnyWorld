shader_type spatial;
render_mode unshaded, blend_add, cull_front, depth_draw_never;
void fragment(){
 float mu=abs(dot(normalize(NORMAL),normalize(VIEW)));
 float horizon=pow(1.0-mu,2.65)*smoothstep(0.0,.12,mu);
 float sun=clamp(dot(normalize(NORMAL),normalize(vec3(-.42,.55,.72))),-.8,1.0);
 vec3 blue=mix(vec3(.06,.16,.39),vec3(.16,.43,.82),smoothstep(-.35,.5,sun));
 float scattering=horizon*(.30+.48*smoothstep(-.3,.65,sun));
 ALBEDO=blue;ALPHA=scattering;
}
