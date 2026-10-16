// Match the immutable 192x144 detail surface's barycentric height. Direct
// relief sampling puts outlines above/below the coarser terrain triangles,
// exposing ledges even when the geographic coverage is antialiased.
uniform vec2 detail_center=vec2(0.0);
uniform vec2 detail_span=vec2(0.0);
float edge_sample_height(vec2 uv){
 vec2 data=textureLod(relief_data,vec2(fract(uv.x),clamp(uv.y,.000001,.999999)),0.0).rg;
 return dot(data,vec2(255.0,65280.0))/65535.0*.016;
}
float border_relief(vec2 uv){
 vec2 delta=vec2(fract(uv.x-detail_center.x+.5)-.5,uv.y-detail_center.y);
 if(detail_span.x<=0.0||any(greaterThan(abs(delta),detail_span*.985)))return edge_sample_height(uv);
 vec2 grid=vec2(192.0,144.0);
 vec2 at=(delta/(detail_span*2.0)+.5)*grid;
 vec2 cell=floor(at),f=fract(at);
 vec2 step=detail_span*2.0/grid;
 vec2 origin=detail_center-detail_span+cell*step;
 float a=edge_sample_height(origin),b=edge_sample_height(origin+vec2(step.x,0.0));
 float c=edge_sample_height(origin+vec2(0.0,step.y)),d=edge_sample_height(origin+step);
 return f.x+f.y<=1.0?a*(1.0-f.x-f.y)+b*f.x+c*f.y:b*(1.0-f.y)+c*(1.0-f.x)+d*(f.x+f.y-1.0);
}
