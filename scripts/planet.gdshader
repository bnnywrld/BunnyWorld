shader_type spatial;
render_mode unshaded;
#include "res://scripts/microstate.gdshaderinc"
#include "res://scripts/water_passages.gdshaderinc"
uniform sampler2D region_map_0 : filter_nearest, repeat_disable;
uniform sampler2D region_map_1 : filter_nearest, repeat_disable;
uniform sampler2D region_map_2 : filter_nearest, repeat_disable;
uniform sampler2D region_map_3 : filter_nearest, repeat_disable;
uniform sampler2D province_index : filter_nearest, repeat_disable;
uniform sampler2D relief_data : filter_linear, repeat_enable;
uniform sampler2DArray terrain_materials : source_color, filter_linear_mipmap_anisotropic, repeat_enable;
uniform sampler2D terrain_types : filter_nearest, repeat_enable;
uniform sampler2D terrain_color : source_color, filter_linear_mipmap, repeat_enable;
varying vec3 geographic_normal;
uniform vec2 detail_center=vec2(0.0);
uniform vec2 detail_span=vec2(0.0);
varying flat float patch_surface;
varying vec3 radial_world;
varying vec3 east_world;
varying vec3 north_world;
const vec2 map_resolution=vec2(16384.0,8192.0);
uniform sampler2D local_coast : filter_linear, repeat_disable;
uniform vec4 local_coast_rect=vec4(0.0);
uniform bool local_coast_enabled=false;
uniform sampler2D tiny_land_bits : filter_nearest, repeat_disable;
uniform sampler2D coast_distance : filter_linear, repeat_enable;
uniform sampler2D state_coverage : filter_linear, repeat_disable;
uniform sampler2D province_coverage : filter_linear, repeat_disable;
uniform vec4 state_coverage_rect=vec4(0.0);
uniform vec4 province_coverage_rect=vec4(0.0);
uniform bool state_coverage_enabled=false;
uniform bool province_coverage_enabled=false;
uniform sampler2D colors : source_color, filter_nearest;
uniform sampler2D owners : filter_nearest;
uniform sampler2D sea_map : filter_nearest, repeat_disable;
uniform float palette_width=8192.0;
uniform float selected_country=0.0;
uniform float hovered_country=0.0;
uniform float hover_amount=0.0;
uniform float selected_region=0.0;
uniform float selected_province=0.0;
uniform float selected_sea=0.0;
uniform bool inspection_active=false;
uniform float province_opacity=0.0;
uniform bool physical_mode=false;
uniform bool information_mode=false;
uniform sampler2D border_fade : filter_linear, repeat_disable;
uniform sampler2D urban_density : filter_linear_mipmap, repeat_enable;
uniform sampler2D urban_material : source_color, filter_linear_mipmap, repeat_enable;
uniform float city_detail=0.0;
uniform float terrain_mix=0.0;
uniform bool show_regions=false;
uniform float region_opacity=0.0;
uniform float far_filter=0.0;
uniform float border_width=1.15;
uniform float border_strength=1.0;
uniform float coast_strength=1.0;
vec3 map_data(vec2 uv){
 uv=vec2(fract(uv.x),clamp(uv.y,0.0,.999999));vec2 p=fract(uv*2.0);vec3 data;
 if(uv.y<.5){data=uv.x<.5?texture(region_map_0,p).rgb:texture(region_map_1,p).rgb;}
 else{data=uv.x<.5?texture(region_map_2,p).rgb:texture(region_map_3,p).rgb;}
 return floor(data*255.0+.5);
}
float province_at(vec2 uv){vec3 d=map_data(uv);return resolve_micro_province(uv,d.r+d.g*256.0);}
float region_at(vec2 uv){float pid=province_at(uv);vec3 d=floor(texture(province_index,vec2((mod(pid,256.0)+.5)/256.0,(floor(pid/256.0)+.5)/256.0)).rgb*255.0+.5);return d.r+d.g*256.0;}
vec2 lookup(float id){return vec2((id+.5)/palette_width,.5);}
float owner_at(float id){vec3 d=texture(owners,lookup(id)).rgb;return floor(d.r*255.0+.5)+floor(d.g*255.0+.5)*256.0;}
vec4 color_at(vec2 uv,vec3 water){float id=region_at(uv);return id<.5?vec4(water,0.0):vec4(texture(colors,lookup(id)).rgb,1.0);}
float relief(vec2 uv){vec2 d=textureLod(relief_data,vec2(fract(uv.x),clamp(uv.y,0.0,1.0)),0.0).rg;return(dot(d,vec2(255.0,65280.0))/65535.0)*.016;}
void vertex(){
 patch_surface=UV2.x;
 if(patch_surface>.5){UV=detail_center+(UV*2.0-1.0)*detail_span;UV.y=clamp(UV.y,.000001,.999999);}
 float lon=(UV.x-.5)*6.28318530718,lat=(.5-UV.y)*3.14159265359;
 vec3 n=vec3(cos(lat)*sin(lon),sin(lat),cos(lat)*cos(lon));
 geographic_normal=n;
 VERTEX=n*(1.0+relief(UV)+(patch_surface>.5?.000002:0.0));
 NORMAL=n;
 radial_world=normalize(mat3(MODEL_MATRIX)*n);
 east_world=normalize(mat3(MODEL_MATRIX)*vec3(cos(lon),0.0,-sin(lon)));
 north_world=normalize(mat3(MODEL_MATRIX)*vec3(-sin(lat)*sin(lon),cos(lat),-sin(lat)*cos(lon)));
}
float patch_hash(vec2 p){
 // Integer avalanche avoids repeated sine evaluations in the detail shader.
 uvec2 q=uvec2(ivec2(p));
 uint h=q.x*uint(1597334677)^q.y*uint(1181783497);
 h=(h^(h>>uint(16)))*uint(747796405);
 h=(h^(h>>uint(13)))*uint(289133645);
 return float((h^(h>>uint(16)))&uint(16777215))/16777216.0;
}
float patch_noise(vec2 p){
 vec2 i=floor(p),f=fract(p);f=f*f*(3.0-2.0*f);
 return mix(mix(patch_hash(i),patch_hash(i+vec2(1,0)),f.x),mix(patch_hash(i+vec2(0,1)),patch_hash(i+vec2(1,1)),f.x),f.y);
}
vec3 varied_sample(float layer,vec2 uv,float phase,vec2 dx,vec2 dy){
 // Two fixed-world patch samples. Explicit gradients preserve mip selection
 // across changes of patch identity; nothing is generated/uploaded on travel.
 float i=floor(phase),f=fract(phase);
 vec2 a=vec2(patch_hash(vec2(i,layer)),patch_hash(vec2(layer+19.0,i)))*37.0;
 vec2 b=vec2(patch_hash(vec2(i+1.0,layer)),patch_hash(vec2(layer+19.0,i+1.0)))*37.0;
 bool odd=mod(i,2.0)>.5;
 vec2 uva=odd?vec2(-uv.y,uv.x):uv;
 vec2 uvb=odd?uv:vec2(-uv.y,uv.x);
 vec2 dxa=odd?vec2(-dx.y,dx.x):dx;
 vec2 dya=odd?vec2(-dy.y,dy.x):dy;
 vec2 dxb=odd?dx:vec2(-dx.y,dx.x);
 vec2 dyb=odd?dy:vec2(-dy.y,dy.x);
 vec3 first=textureGrad(terrain_materials,vec3(uva+a,layer),dxa,dya).rgb;
 vec3 second=textureGrad(terrain_materials,vec3(uvb+b,layer),dxb,dyb).rgb;
 float blend=smoothstep(.18,.82,f);
 return mix(first,second,blend);
}
vec3 material(float layer,vec3 position,vec3 phase,vec3 dx,vec3 dy){
 // World-anchored triplanar mapping avoids longitude/pole stretching and seams.
 vec3 w=pow(abs(normalize(position)),vec3(6.0));w/=max(.00001,w.x+w.y+w.z);
 w=max(w-vec3(.025),vec3(0.0));w/=w.x+w.y+w.z;
 vec3 a=vec3(0.0),b=vec3(0.0),c=vec3(0.0);
 if(w.x>.001)a=varied_sample(layer,position.yz,phase.x,dx.yz,dy.yz);
 if(w.y>.001)b=varied_sample(layer,position.xz,phase.y,dx.xz,dy.xz);
 if(w.z>.001)c=varied_sample(layer,position.xy,phase.z,dx.xy,dy.xy);
 return a*w.x+b*w.y+c*w.z;
}
vec3 biome_at(vec2 uv){
 // Interpolate class WEIGHTS rather than numeric class IDs. Keeps transitions
 // smooth without selecting a nonexistent material between two categories.
 vec2 size=vec2(textureSize(terrain_types,0));
 vec2 at=uv*size-.5;
 vec2 origin=(floor(at)+.5)/size;
 vec2 f=fract(at);
 vec4 entries[4];
 entries[0]=texture(terrain_types,origin);
 entries[1]=texture(terrain_types,origin+vec2(1.0/size.x,0.0));
 entries[2]=texture(terrain_types,origin+vec2(0.0,1.0/size.y));
 entries[3]=texture(terrain_types,origin+1.0/size);
 float influence[4];
 influence[0]=(1.0-f.x)*(1.0-f.y);influence[1]=f.x*(1.0-f.y);
 influence[2]=(1.0-f.x)*f.y;influence[3]=f.x*f.y;
 float best=0.0;float next=0.0;float first=0.0;float second=0.0;
 for(int category=0;category<8;category++){
  float total=0.0;
  for(int corner=0;corner<4;corner++){
   float a=floor(entries[corner].r*255.0+.5);
   float b=floor(entries[corner].g*255.0+.5);
   total+=influence[corner]*((a==float(category)?1.0-entries[corner].b:0.0)+(b==float(category)?entries[corner].b:0.0));
  }
  if(total>best){next=best;second=first;best=total;first=float(category);}
  else if(total>next){next=total;second=float(category);}
 }
 return vec3(first,second,next/max(best+next,.00001));
}
float small_land_at(vec2 pixel){
 pixel=vec2(mod(pixel.x+map_resolution.x,map_resolution.x),clamp(pixel.y,0.0,map_resolution.y-1.0));
 vec2 bit_uv=(vec2(floor(pixel.x/8.0),pixel.y)+.5)/vec2(2048.0,8192.0);
 uint bits=uint(floor(texture(tiny_land_bits,bit_uv).r*255.0+.5));
 return float((bits>>uint(mod(pixel.x,8.0)))&uint(1));
}
float coverage_alpha(float d){float aa=max(fwidth(d)*.65,1.0/255.0);return smoothstep(.5-aa,.5+aa,d);}
float tile_coverage(sampler2D field,vec4 rect,vec2 uv){
 vec2 local=vec2(fract(uv.x-rect.x+1.0),uv.y-rect.y)/max(rect.zw,vec2(.0000001));
 if(any(lessThan(local,vec2(0.0)))||any(greaterThan(local,vec2(1.0))))return 0.0;
 return coverage_alpha(texture(field,local).r);
}
void fragment(){
 vec2 uv=vec2(fract(UV.x),clamp(UV.y,.000001,.999999));
 vec2 delta=vec2(abs(fract(uv.x-detail_center.x+.5)-.5),abs(uv.y-detail_center.y));
 if(patch_surface<.5&&detail_span.x>0.0&&all(lessThan(delta,detail_span*.985)))discard;
 float facing=clamp(dot(normalize(NORMAL),normalize(VIEW)),0.0,1.0);
 vec3 water=mix(vec3(.025,.105,.18),vec3(.075,.27,.39),facing);
 float passage_id=water_passage(uv);
 float region=passage_id>0.0?0.0:region_at(uv);float owner=owner_at(region);
 bool chosen=inspection_active&&owner>0.0&&owner==selected_country;
 vec2 texel=1.0/map_resolution;vec2 pixel=uv*map_resolution-.5;vec2 origin=(floor(pixel)+.5)*texel;vec2 blend=fract(pixel);
 vec2 dx=dFdx(uv)*.3*far_filter;vec2 dy=dFdy(uv)*.3*far_filter;
 // Physical terrain uses the prepared coast field, so it no longer needs
 // four province/region/palette decodes just to reconstruct land coverage.
 vec4 surface=vec4(water,0.0);
 if(!physical_mode){
 vec4 c00=color_at(mix(origin,uv-dx-dy,far_filter),water);vec4 c10=color_at(mix(origin+vec2(texel.x,0),uv+dx-dy,far_filter),water);
 vec4 c01=color_at(mix(origin+vec2(0,texel.y),uv-dx+dy,far_filter),water);vec4 c11=color_at(mix(origin+texel,uv+dx+dy,far_filter),water);
 blend=mix(blend,vec2(.5),far_filter);surface=mix(mix(c00,c10,blend.x),mix(c01,c11,blend.x),blend.y);
 if(passage_id>0.0)surface=vec4(water,0.0);
 // Subpixel enclaves cannot rely on four coarse atlas samples for their fill.
 if(abs(region-micro_region)<.5){surface=vec4(texture(colors,lookup(region)).rgb,1.0);}
 }

 float coast_value=texture(coast_distance,uv).r;
 if(local_coast_enabled&&city_detail>.001){
  vec2 at=vec2(fract(uv.x-local_coast_rect.x+1.0),uv.y-local_coast_rect.y)/local_coast_rect.zw;
  if(all(greaterThanEqual(at,vec2(0.0)))&&all(lessThanEqual(at,vec2(1.0)))){
   vec2 edge=min(at,1.0-at)*local_coast_rect.zw*map_resolution;
   float local_blend=smoothstep(0.0,3.0,min(edge.x,edge.y))*city_detail;
   coast_value=mix(coast_value,texture(local_coast,at).r,local_blend);
  }
 }
 float land_coverage=coverage_alpha(coast_value);
 if(land_coverage<.999&&region>0.0&&small_land_at(floor(uv*map_resolution))>.5){
  vec2 pixel=uv*map_resolution-.5,corner=floor(pixel),weight=fract(pixel);
  float row0=mix(small_land_at(corner),small_land_at(corner+vec2(1.0,0.0)),weight.x);
  float row1=mix(small_land_at(corner+vec2(0.0,1.0)),small_land_at(corner+vec2(1.0)),weight.x);
  land_coverage=max(land_coverage,coverage_alpha(mix(row0,row1,weight.y)));
 }
 if(passage_id>0.0)land_coverage=0.0;
 if(abs(region-micro_region)<.5)land_coverage=1.0;
 vec3 land_color=clamp((surface.rgb-water*(1.0-surface.a))/max(.0001,surface.a),vec3(0.0),vec3(1.0));
 if(surface.a<.001&&land_coverage>.001&&!physical_mode){
  float nearby=region_at(uv+vec2(texel.x,0.0));
  if(nearby<.5)nearby=region_at(uv-vec2(texel.x,0.0));
  if(nearby<.5)nearby=region_at(uv+vec2(0.0,texel.y));
  if(nearby<.5)nearby=region_at(uv-vec2(0.0,texel.y));
  land_color=nearby>.5?texture(colors,lookup(nearby)).rgb:water;
 }
 vec3 base=mix(water,land_color,land_coverage);
 if(physical_mode){
  vec3 earth=texture(terrain_color,uv).rgb;
  vec3 types=biome_at(uv);
  float primary=types.r;
  float secondary=types.g;
  vec3 n=normalize(geographic_normal);
  vec3 material_position=n*1900.0;
  vec3 material_phase=vec3(0.0);
  vec3 urban_dx=dFdx(n)*430.0,urban_dy=dFdy(n)*430.0;
  float close=smoothstep(0.0,1.0,terrain_mix);
  vec3 pattern=vec3(.5);
  if(close>.001){
   // Compute spatial variation once, shared by both biomes and exposed rock.
   vec3 warp=vec3(patch_noise(material_position.xy*.85+13.0),patch_noise(material_position.yz*.85+37.0),patch_noise(material_position.zx*.85+59.0))-.5;
   material_position+=warp*.82;
   material_phase=vec3(patch_noise(material_position.yz*.43),patch_noise(material_position.xz*.43+17.0),patch_noise(material_position.xy*.43+31.0))*7.0;
  }
  vec3 material_dx=dFdx(material_position),material_dy=dFdy(material_position);
  if(close>.001){
   pattern=material(primary,material_position,material_phase,material_dx,material_dy);
   if(types.b>.015&&primary!=secondary)pattern=mix(pattern,material(secondary,material_position,material_phase,material_dx,material_dy),types.b);
  }
  // Regional colour is low frequency; material detail never changes residency.
  earth=mix(earth,mix(earth*pattern*1.6,pattern,.48),close*.88);
  vec4 elev=texture(relief_data,uv);
  float meters=elev.b*9000.0;
  vec2 step=1.0/vec2(textureSize(relief_data,0));
  float slope_e=(relief(uv+vec2(step.x,0))-relief(uv-vec2(step.x,0)))/(2.0*step.x*6.28318530718*max(.08,sin(uv.y*3.14159265359)));
  float slope_n=(relief(uv+vec2(0,step.y))-relief(uv-vec2(0,step.y)))/(2.0*step.y*3.14159265359);
  vec3 relief_normal=normalize(radial_world-east_world*slope_e+north_world*slope_n);
  float steep=length(vec2(slope_e,slope_n));
  float dry=(primary==3.0?1.0-types.b:0.0)+(secondary==3.0?types.b:0.0);
  float icy=(primary==6.0?1.0-types.b:0.0)+(secondary==6.0?types.b:0.0);
  float exposed=max(smoothstep(.25,.95,steep),smoothstep(2900.0,5400.0,meters))*(1.0-dry*.65)*(1.0-icy);
  if(exposed*close>.01)earth=mix(earth,material(5.0,material_position,material_phase,material_dx,material_dy)*.72+vec3(.10),exposed*.40*close);
  float snowline=mix(4700.0,1700.0,smoothstep(.25,.85,abs(uv.y-.5)*2.0));
  float snow=smoothstep(snowline,snowline+1000.0,meters)*(1.0-smoothstep(.65,1.25,steep));
  earth=mix(earth,vec3(.87,.91,.94),snow*.68);
  float urban=texture(urban_density,uv).r*city_detail;
  // Four broad blocks in each ~15 km patch match the enlarged building style.
  // Longitude scale is corrected for latitude instead of shrinking streets
  // toward the poles. The grid remains fixed to the world.
  if(urban>.001){
   vec3 up=n*430.0;
   vec3 weights=pow(abs(n),vec3(8.0));weights/=weights.x+weights.y+weights.z;
   vec3 blocks=textureGrad(urban_material,up.yz,urban_dx.yz,urban_dy.yz).rgb*weights.x+textureGrad(urban_material,up.xz,urban_dx.xz,urban_dy.xz).rgb*weights.y+textureGrad(urban_material,up.xy,urban_dx.xy,urban_dy.xy).rgb*weights.z;
   vec3 city=mix(vec3(.33,.35,.32),blocks*.9+vec3(.05),.86);
   earth=mix(earth,city,urban*.78);
  }
  // Reconstruct the same four categorical samples used by political fill.
  // A screen-footprint AA band avoids the coarser physical mask halo.
  float physical_land=land_coverage;
  if(passage_id>0.0)physical_land=0.0;
  if(abs(region-micro_region)<.5)physical_land=1.0;
  base=mix(water,earth,physical_land);
  float sun=clamp(dot(relief_normal,normalize(vec3(-.42,.55,.72))),-.75,1.0);
  base*=.70+.32*smoothstep(-.5,.9,sun);
  float haze=pow(1.0-facing,2.8)*.29;base=mix(base,vec3(.18,.35,.49),haze);
  if(owner>0.0){float band=texture(border_fade,uv).r;float amount=band*.20*border_strength*land_coverage;base=mix(base,texture(colors,lookup(region)).rgb,amount);}
 }
 // Visible country/region/coast boundaries use subpixel GPU ribbons. Picking
 // always reads the discrete ID atlas, independently of visual antialiasing.
 if(chosen&&!information_mode){base=mix(base,vec3(.93,.85,.65),(physical_mode?.055:.09)*land_coverage);}
 if(inspection_active&&state_coverage_enabled&&show_regions){
  float hit=tile_coverage(state_coverage,state_coverage_rect,uv);
  if(abs(region-micro_region)<.5)hit=abs(selected_region-micro_region)<.5?1.0:0.0;
  base=mix(base,vec3(.64,.82,.79),.075*hit*land_coverage);
 }
 if(owner>0.0&&owner==hovered_country&&!chosen){base=mix(base,vec3(.88,.87,.72),.055*hover_amount*land_coverage);}
 if(province_opacity>0.0&&province_coverage_enabled){
  float hit=tile_coverage(province_coverage,province_coverage_rect,uv);
  if(abs(region-micro_region)<.5)hit=abs(selected_province-micro_province)<.5?1.0:0.0;
  base=mix(base,vec3(.9,.98,1.0),.12*province_opacity*hit*land_coverage);
 }
 if(region<.5&&selected_sea>0.0){vec3 d=floor(texture(sea_map,uv).rgb*255.0+.5);float sea=passage_id>0.0?passage_id:d.r+d.g*256.0;if(sea==selected_sea){base=mix(base,vec3(.16,.45,.56),.25*(1.0-land_coverage));}}
 ALBEDO=base;
}
