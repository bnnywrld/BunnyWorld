// One categorical reconstruction for political colour, State/province fill
// and all close-view internal lines. IDs remain discrete; only membership
// coverage is interpolated. No ownership-dependent precomputed mask exists.
uniform sampler2D boundary_hint : filter_linear, repeat_enable;
uniform sampler2D boundary_pairs : filter_nearest, repeat_enable;
uniform sampler2D boundary_distance : filter_linear, repeat_enable;
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
vec4 cubic_derivative(float t){return vec4(-.5+2.0*t-1.5*t*t,-5.0*t+4.5*t*t,.5+4.0*t-4.5*t*t,-t+1.5*t*t);}
float coverage_pixels(float value,vec2 gradient,vec2 screen_dx,vec2 screen_dy){
 float footprint=abs(dot(gradient,screen_dx))+abs(dot(gradient,screen_dy));
 return (value-.5)/max(footprint,.000001);
}
float resolved_coverage(float value,vec2 gradient,vec2 screen_dx,vec2 screen_dy){
 float aa=max((abs(dot(gradient,screen_dx))+abs(dot(gradient,screen_dy)))*.65,.000001);
 return smoothstep(.5-aa,.5+aa,value);
}
MapCoverage map_coverage(vec2 uv,float pid,float sid,float owner){
 MapCoverage c;
 c.tint=sid>.5?texture(colors,lookup(sid)).rgb:vec3(0.0);
 c.country_hit=owner==selected_country&&owner>.5?1.0:0.0;
 c.hover_hit=owner==hovered_country&&owner>.5?1.0:0.0;
 c.state_hit=sid==selected_region&&sid>.5?1.0:0.0;
 c.province_hit=pid==selected_province&&pid>.5?1.0:0.0;
 c.country_distance=10000.0;c.state_distance=10000.0;c.province_distance=10000.0;
 c.selected_state_distance=c.state_hit>.5?10000.0:-10000.0;
 c.selected_province_distance=c.province_hit>.5?10000.0:-10000.0;
 c.national_edge=false;c.state_edge=false;c.province_edge=false;
 // Derivatives are evaluated before the nonuniform boundary branch.
 highp vec2 pixel=uv*map_resolution;
 highp vec2 screen_dx=dFdx(pixel),screen_dy=dFdy(pixel);
 // Primary reconstruction uses distance to the shared smoothed vector
 // curve. Pair IDs only select membership; they never determine its shape.
 highp float sd=texture(boundary_distance,uv).r;
 float footprint=max(fwidth(sd),.000001);
 vec2 size=vec2(textureSize(boundary_pairs,0));
 vec2 origin=(floor(uv*size-.5)+.5)/size;
 vec4 p00=texture(boundary_pairs,origin);
 float hint=texture(boundary_hint,uv).r;
 // Empty pair cells cannot enter the curve branch; outside the conservative
 // junction hint the old path returns the categorical result as well.
 if(hint<=.001&&all(equal(p00,vec4(0.0))))return c;
 vec4 p10=texture(boundary_pairs,origin+vec2(1.0/size.x,0.0));
 vec4 p01=texture(boundary_pairs,origin+vec2(0.0,1.0/size.y));
 vec4 p11=texture(boundary_pairs,origin+1.0/size);
 if(any(greaterThan(p00,vec4(0.0)))&&all(equal(p00,p10))&&all(equal(p00,p01))&&all(equal(p00,p11))){
  vec4 bytes=floor(p00*255.0+.5);
  float a=bytes.r+bytes.g*256.0,b=bytes.b+bytes.a*256.0;
  vec4 ar=province_record(a),br=province_record(b);
  float sa=ar.r+ar.g*256.0,sb=br.r+br.g*256.0,oa=ar.b+ar.a*256.0,ob=br.b+br.a*256.0;
  float h=smoothstep(-footprint*.65,footprint*.65,sd),pixels=sd/footprint;
  vec3 ca=texture(colors,lookup(sa)).rgb,cb=texture(colors,lookup(sb)).rgb;
  c.tint=sa<.5?cb:(sb<.5?ca:mix(cb,ca,h));
  c.country_hit=(oa==selected_country&&oa>.5?h:0.0)+(ob==selected_country&&ob>.5?1.0-h:0.0);
  c.hover_hit=(oa==hovered_country&&oa>.5?h:0.0)+(ob==hovered_country&&ob>.5?1.0-h:0.0);
  bool ah=sa==selected_region&&sa>.5,bh=sb==selected_region&&sb>.5;
  c.state_hit=(ah?h:0.0)+(bh?1.0-h:0.0);
  c.selected_state_distance=ah!=bh?(ah?pixels:-pixels):(ah?10000.0:-10000.0);
  ah=a==selected_province&&a>.5;bh=b==selected_province&&b>.5;
  c.province_hit=(ah?h:0.0)+(bh?1.0-h:0.0);
  c.selected_province_distance=ah!=bh?(ah?pixels:-pixels):(ah?10000.0:-10000.0);
  c.national_edge=oa!=ob&&oa>.5&&ob>.5;
  c.state_edge=sa!=sb&&sa>.5&&sb>.5;
  c.province_edge=a!=b&&a>.5&&b>.5&&sa==sb;
  c.country_distance=c.national_edge?pixels:10000.0;
  c.state_distance=c.state_edge?pixels:10000.0;
  c.province_distance=c.province_edge?pixels:10000.0;
  if(sa<.5||sb<.5){
   // One coastline field clips both colour and selection. A province's
   // independently sampled coastal segment must never cut a second shore.
   float land_state=sa>.5?sa:sb,land_province=sa>.5?a:b,land_owner=sa>.5?oa:ob;
   c.state_hit=land_state==selected_region?1.0:0.0;
   c.province_hit=land_province==selected_province?1.0:0.0;
   c.country_hit=land_owner==selected_country?1.0:0.0;
   c.hover_hit=land_owner==hovered_country?1.0:0.0;
   c.selected_state_distance=c.state_hit>.5?10000.0:-10000.0;
   c.selected_province_distance=c.province_hit>.5?10000.0:-10000.0;
  }
  return c;
 }
 // Conservative fallback at multi-province junctions and subpixel islands.
 // This uses current membership as well; no old State masks are involved.
 if(hint>.001){
  highp vec2 at=pixel-.5,cell=floor(at),f=fract(at);
  vec4 wx=cubic_weights(f.x),wy=cubic_weights(f.y);
  vec4 dwx=cubic_derivative(f.x),dwy=cubic_derivative(f.y);
  float countries[16];float amounts[16];vec2 gradients[16];float tint_states[16];int count=0;
  float own_value=0.0,state_value=0.0,province_value=0.0,sh=0.0,ph=0.0;
  vec2 own_grad=vec2(0.0),state_grad=vec2(0.0),province_grad=vec2(0.0),sg=vec2(0.0),pg=vec2(0.0);
  bool other_state=false,other_province=false;
  for(int y=0;y<4;y++)for(int x=0;x<4;x++){
   float p=province_at((cell+vec2(float(x)-.5,float(y)-.5))/map_resolution);
   vec4 rec=province_record(p);
   float s=rec.r+rec.g*256.0,o=rec.b+rec.a*256.0,w=wx[x]*wy[y];vec2 g=vec2(dwx[x]*wy[y],wx[x]*dwy[y]);
   if(o==owner){own_value+=w;own_grad+=g;}
   if(s==sid){state_value+=w;state_grad+=g;}
   if(p==pid){province_value+=w;province_grad+=g;}
   if(s==selected_region&&s>.5){sh+=w;sg+=g;}
   if(p==selected_province&&p>.5){ph+=w;pg+=g;}
   if(s>.5&&s!=sid)other_state=true;
   if(p>.5&&p!=pid&&s==sid)other_province=true;
   if(o>.5){
    int found=-1;for(int j=0;j<16;j++){if(j>=count)break;if(countries[j]==o){found=j;break;}}
    if(found<0){found=count;countries[count]=o;amounts[count]=0.0;gradients[count]=vec2(0.0);tint_states[count]=s;count++;}
    amounts[found]+=w;gradients[found]+=g;
   }
  }
  // Country colour and its selection share the exact same resolved coverage.
  float total=0.0;vec3 tint=vec3(0.0);float ch=0.0,hh=0.0;
  for(int j=0;j<16;j++){
   if(j>=count)break;
   float a=resolved_coverage(amounts[j],gradients[j],screen_dx,screen_dy);
   tint+=texture(colors,lookup(tint_states[j])).rgb*a;total+=a;
   if(countries[j]==selected_country)ch=a;
   if(countries[j]==hovered_country)hh=a;
  }
  if(total>.000001){c.tint=tint/total;c.country_hit=ch/total;c.hover_hit=hh/total;}
  // At a 3+ country junction no category may exceed half. Use nonnegative
  // weights there rather than inventing a fourth owner or punching a hole.
  else if(count>0){
   total=0.0;tint=vec3(0.0);ch=0.0;hh=0.0;
   for(int j=0;j<16;j++){if(j>=count)break;float a=max(amounts[j],0.0);tint+=texture(colors,lookup(tint_states[j])).rgb*a;total+=a;if(countries[j]==selected_country)ch=a;if(countries[j]==hovered_country)hh=a;}
   c.tint=tint/max(total,.000001);c.country_hit=ch/max(total,.000001);c.hover_hit=hh/max(total,.000001);
  }
  c.state_hit=resolved_coverage(sh,sg,screen_dx,screen_dy);
  c.province_hit=resolved_coverage(ph,pg,screen_dx,screen_dy);
  c.country_distance=coverage_pixels(own_value,own_grad,screen_dx,screen_dy);
  c.state_distance=coverage_pixels(state_value,state_grad,screen_dx,screen_dy);
  c.province_distance=coverage_pixels(province_value,province_grad,screen_dx,screen_dy);
  c.selected_state_distance=coverage_pixels(sh,sg,screen_dx,screen_dy);
  c.selected_province_distance=coverage_pixels(ph,pg,screen_dx,screen_dy);
  c.national_edge=count>1&&owner>.5;
  c.state_edge=other_state&&sid>.5;
  c.province_edge=other_province&&pid>.5;
 }
 return c;
}
