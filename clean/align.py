import json, numpy as np, cv2, sys
from shapely.geometry import Polygon, Point, MultiPolygon
from shapely.ops import unary_union
def page(key,size):
    p=f'/home/claude/ar/genabc/pages/{size}/{key}.png' if key.startswith('abc-') else f'/home/claude/ar/gen/pages/{size}/{key}.png'
    return cv2.imread(p,0)
def dots(g):
    bw=(g<110).astype(np.uint8)
    op=cv2.morphologyEx(bw,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(11,11)))
    n,lab,st,cen=cv2.connectedComponentsWithStats(op,8)
    C=[(cen[i],st[i][2]) for i in range(1,n) if 12<=st[i][2]<=34 and 12<=st[i][3]<=34 and 0.7<st[i][2]/st[i][3]<1.4]
    return np.array([c for c,_ in C]), np.median([w for _,w in C])/2 if C else 0
keys=sys.argv[1:]
for key in keys:
    d=json.load(open(f'orig/{key}_a4.json')); g=page(key,'a4')
    polys=[Polygon(p) for p in d['body']]+[Polygon(p) for pt in d['parts'] for p in pt['polys']]
    U=unary_union([p.buffer(0) for p in polys])
    C,r=dots(g)
    near=[c for c in C if U.exterior.distance(Point(c)) <40] if U.geom_type=='Polygon' else [c for c in C if U.boundary.distance(Point(c))<40]
    dist=[U.boundary.distance(Point(c)) for c in near]
    inside=[U.contains(Point(c)) for c in near]
    print(key, U.geom_type, 'dots',len(C),'near',len(near),'r',r,'med dist',round(float(np.median(dist)),1),'inside frac',round(float(np.mean(inside)),2))
