// Authored narrow waterways: source of truth is data/waterways.json.
float water_passage(vec2 uv){
 vec2 p=vec2(uv.x*360.0-180.0,90.0-uv.y*180.0);
 if(p.x>32.250000&&p.x<32.630000&&p.y>29.900000&&p.y<31.330000){
  vec2 metric=vec2(cos(p.y*.01745329252)*111.195,111.195);
  {vec2 a=vec2(32.300000,31.280000);vec2 v=(vec2(32.320000,31.050000)-a)*metric;vec2 q=(p-a)*metric;float t=clamp(dot(q,v)/max(dot(v,v),.000001),0.0,1.0);if(length(q-v*t)<0.110000)return 69.0;}
  {vec2 a=vec2(32.320000,31.050000);vec2 v=(vec2(32.340000,30.820000)-a)*metric;vec2 q=(p-a)*metric;float t=clamp(dot(q,v)/max(dot(v,v),.000001),0.0,1.0);if(length(q-v*t)<0.110000)return 69.0;}
  {vec2 a=vec2(32.340000,30.820000);vec2 v=(vec2(32.300000,30.600000)-a)*metric;vec2 q=(p-a)*metric;float t=clamp(dot(q,v)/max(dot(v,v),.000001),0.0,1.0);if(length(q-v*t)<0.110000)return 69.0;}
  {vec2 a=vec2(32.300000,30.600000);vec2 v=(vec2(32.490000,30.350000)-a)*metric;vec2 q=(p-a)*metric;float t=clamp(dot(q,v)/max(dot(v,v),.000001),0.0,1.0);if(length(q-v*t)<0.110000)return 69.0;}
  {vec2 a=vec2(32.490000,30.350000);vec2 v=(vec2(32.550000,30.100000)-a)*metric;vec2 q=(p-a)*metric;float t=clamp(dot(q,v)/max(dot(v,v),.000001),0.0,1.0);if(length(q-v*t)<0.110000)return 69.0;}
  {vec2 a=vec2(32.550000,30.100000);vec2 v=(vec2(32.580000,29.950000)-a)*metric;vec2 q=(p-a)*metric;float t=clamp(dot(q,v)/max(dot(v,v),.000001),0.0,1.0);if(length(q-v*t)<0.110000)return 69.0;}
 }
 if(p.x>-79.980000&&p.x<-79.520000&&p.y>8.900000&&p.y<9.410000){
  vec2 metric=vec2(cos(p.y*.01745329252)*111.195,111.195);
  {vec2 a=vec2(-79.910000,9.360000);vec2 v=(vec2(-79.930000,9.270000)-a)*metric;vec2 q=(p-a)*metric;float t=clamp(dot(q,v)/max(dot(v,v),.000001),0.0,1.0);if(length(q-v*t)<0.100000)return 53.0;}
  {vec2 a=vec2(-79.930000,9.270000);vec2 v=(vec2(-79.860000,9.180000)-a)*metric;vec2 q=(p-a)*metric;float t=clamp(dot(q,v)/max(dot(v,v),.000001),0.0,1.0);if(length(q-v*t)<0.100000)return 53.0;}
  {vec2 a=vec2(-79.860000,9.180000);vec2 v=(vec2(-79.730000,9.120000)-a)*metric;vec2 q=(p-a)*metric;float t=clamp(dot(q,v)/max(dot(v,v),.000001),0.0,1.0);if(length(q-v*t)<0.100000)return 53.0;}
  {vec2 a=vec2(-79.730000,9.120000);vec2 v=(vec2(-79.660000,9.080000)-a)*metric;vec2 q=(p-a)*metric;float t=clamp(dot(q,v)/max(dot(v,v),.000001),0.0,1.0);if(length(q-v*t)<0.100000)return 53.0;}
  {vec2 a=vec2(-79.660000,9.080000);vec2 v=(vec2(-79.610000,9.030000)-a)*metric;vec2 q=(p-a)*metric;float t=clamp(dot(q,v)/max(dot(v,v),.000001),0.0,1.0);if(length(q-v*t)<0.100000)return 53.0;}
  {vec2 a=vec2(-79.610000,9.030000);vec2 v=(vec2(-79.570000,8.950000)-a)*metric;vec2 q=(p-a)*metric;float t=clamp(dot(q,v)/max(dot(v,v),.000001),0.0,1.0);if(length(q-v*t)<0.100000)return 53.0;}
 }
 if(p.x>28.960000&&p.x<29.130000&&p.y>40.930000&&p.y<41.290000){
  vec2 metric=vec2(cos(p.y*.01745329252)*111.195,111.195);
  {vec2 a=vec2(29.080000,41.240000);vec2 v=(vec2(29.080000,41.190000)-a)*metric;vec2 q=(p-a)*metric;float t=clamp(dot(q,v)/max(dot(v,v),.000001),0.0,1.0);if(length(q-v*t)<0.425000)return 240.0;}
  {vec2 a=vec2(29.080000,41.190000);vec2 v=(vec2(29.060000,41.150000)-a)*metric;vec2 q=(p-a)*metric;float t=clamp(dot(q,v)/max(dot(v,v),.000001),0.0,1.0);if(length(q-v*t)<0.425000)return 240.0;}
  {vec2 a=vec2(29.060000,41.150000);vec2 v=(vec2(29.050000,41.120000)-a)*metric;vec2 q=(p-a)*metric;float t=clamp(dot(q,v)/max(dot(v,v),.000001),0.0,1.0);if(length(q-v*t)<0.425000)return 240.0;}
  {vec2 a=vec2(29.050000,41.120000);vec2 v=(vec2(29.060000,41.090000)-a)*metric;vec2 q=(p-a)*metric;float t=clamp(dot(q,v)/max(dot(v,v),.000001),0.0,1.0);if(length(q-v*t)<0.425000)return 240.0;}
  {vec2 a=vec2(29.060000,41.090000);vec2 v=(vec2(29.040000,41.060000)-a)*metric;vec2 q=(p-a)*metric;float t=clamp(dot(q,v)/max(dot(v,v),.000001),0.0,1.0);if(length(q-v*t)<0.425000)return 240.0;}
  {vec2 a=vec2(29.040000,41.060000);vec2 v=(vec2(29.010000,41.030000)-a)*metric;vec2 q=(p-a)*metric;float t=clamp(dot(q,v)/max(dot(v,v),.000001),0.0,1.0);if(length(q-v*t)<0.425000)return 240.0;}
  {vec2 a=vec2(29.010000,41.030000);vec2 v=(vec2(29.010000,40.980000)-a)*metric;vec2 q=(p-a)*metric;float t=clamp(dot(q,v)/max(dot(v,v),.000001),0.0,1.0);if(length(q-v*t)<0.425000)return 240.0;}
 }
 if(p.x>26.090000&&p.x<26.770000&&p.y>39.960000&&p.y<40.440000){
  vec2 metric=vec2(cos(p.y*.01745329252)*111.195,111.195);
  {vec2 a=vec2(26.720000,40.390000);vec2 v=(vec2(26.580000,40.290000)-a)*metric;vec2 q=(p-a)*metric;float t=clamp(dot(q,v)/max(dot(v,v),.000001),0.0,1.0);if(length(q-v*t)<0.800000)return 241.0;}
  {vec2 a=vec2(26.580000,40.290000);vec2 v=(vec2(26.470000,40.190000)-a)*metric;vec2 q=(p-a)*metric;float t=clamp(dot(q,v)/max(dot(v,v),.000001),0.0,1.0);if(length(q-v*t)<0.800000)return 241.0;}
  {vec2 a=vec2(26.470000,40.190000);vec2 v=(vec2(26.400000,40.150000)-a)*metric;vec2 q=(p-a)*metric;float t=clamp(dot(q,v)/max(dot(v,v),.000001),0.0,1.0);if(length(q-v*t)<0.800000)return 241.0;}
  {vec2 a=vec2(26.400000,40.150000);vec2 v=(vec2(26.350000,40.080000)-a)*metric;vec2 q=(p-a)*metric;float t=clamp(dot(q,v)/max(dot(v,v),.000001),0.0,1.0);if(length(q-v*t)<0.800000)return 241.0;}
  {vec2 a=vec2(26.350000,40.080000);vec2 v=(vec2(26.230000,40.030000)-a)*metric;vec2 q=(p-a)*metric;float t=clamp(dot(q,v)/max(dot(v,v),.000001),0.0,1.0);if(length(q-v*t)<0.800000)return 241.0;}
  {vec2 a=vec2(26.230000,40.030000);vec2 v=(vec2(26.140000,40.010000)-a)*metric;vec2 q=(p-a)*metric;float t=clamp(dot(q,v)/max(dot(v,v),.000001),0.0,1.0);if(length(q-v*t)<0.800000)return 241.0;}
 }
 return 0.0;
}
