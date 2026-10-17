"""Shared offline point classifier for the subpixel enclave override."""
from pathlib import Path
import json
from shapely.geometry import Polygon,Point

class MicroGeometry:
    def __init__(self,root):
        self.data=json.loads((Path(root)/'data/microstate_geometry.json').read_text())
        self.polygon=Polygon(self.data.get('polygon_uv',[]))
        self.bounds=self.polygon.bounds
    def resolve(self,lon,lat,coarse):
        if not self.data.get('enabled',True):return coarse
        u,v=(lon+180)/360,(90-lat)/180
        l,t,r,b=self.bounds
        if l<=u<=r and t<=v<=b and self.polygon.covers(Point(u,v)):
            return self.data['province']
        return self.data['host_province'] if coarse==self.data['province'] else coarse
