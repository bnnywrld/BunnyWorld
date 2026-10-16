shader_type spatial;
render_mode unshaded, cull_disabled, depth_draw_never, depth_test_disabled;
uniform sampler2D glyph_atlas : source_color, filter_linear_mipmap, repeat_disable;
uniform sampler2D label_visibility : filter_nearest, repeat_disable;
uniform float camera_distance=3.0;
varying float label_alpha;
varying vec3 radial;
void vertex(){
 vec3 eye=(MODELVIEW_MATRIX*vec4(VERTEX,1.0)).xyz;
 float height=UV2.y*abs(PROJECTION_MATRIX[1][1])*VIEWPORT_SIZE.y/(2.0*max(.01,-eye.z));
 float visible=textureLod(label_visibility,vec2(UV2.x,.5),0.0).r;
 label_alpha=visible*smoothstep(7.0,10.0,height)*smoothstep(1.22,1.48,camera_distance)*.9;
 POSITION=visible<.5?vec4(2.0,2.0,2.0,1.0):PROJECTION_MATRIX*vec4(eye,1.0);
 radial=normalize(mat3(MODELVIEW_MATRIX)*normalize(VERTEX));
}
void fragment(){
 vec4 glyph=texture(glyph_atlas,UV);
 float facing=dot(normalize(radial),normalize(VIEW));
 ALBEDO=glyph.rgb*vec3(.94,.92,.86);
 ALPHA=glyph.a*label_alpha*smoothstep(.10,.25,facing);
}
