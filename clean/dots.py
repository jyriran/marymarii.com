import json, sys, numpy as np, cv2
from shapely.geometry import Polygon, Point
size=sys.argv[1]
d=json.load(open(f'/home/claude/repo-marymarii/scan/targets/bear_{size}.json'))
g=cv2.imread(f'/home/claude/ar/gen/pages/{size}/bear.png',0)
x0,y0,x1,y1=[int(round(v)) for v in d['region']]
bw=(g<110).astype(np.uint8)
bw=cv2.morphologyEx(bw,cv2.MORPH_OPEN,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(13,13)))
n,lab,st,cen=cv2.connectedComponentsWithStats(bw,8)
sil=Polygon(d['body'][0]); ext=sil.exterior
dots=[]
for i in range(1,n):
    x,y,w,h,a=st[i]
    if not (x0-20<x<x1+20 and y0-20<y<y1+20): continue
    if 0.7<w/h<1.4 and 14<=w<=34 and a>0.55*w*h:
        c=Point(cen[i]); 
        if sil.buffer(5).contains(c): dots.append((cen[i][0],cen[i][1],w,i))
print(len(dots), 'dot w med', np.median([t[2] for t in dots]))
dots.sort(key=lambda t: ext.project(Point(t[0],t[1])))
json.dump([[round(t[0],1),round(t[1],1)] for t in dots], open(f'dots_{size}.json','w'))
im=cv2.cvtColor(g,cv2.COLOR_GRAY2BGR)
pts=np.array([[t[0],t[1]] for t in dots],np.int32)
cv2.polylines(im,[pts],True,(0,0,255),2)
for k,t in enumerate(dots): cv2.putText(im,str(k),(int(t[0])+6,int(t[1])-6),0,0.45,(255,0,0),1)
cv2.imwrite(f'chk_{size}.png',im[y0:y1,x0:x1])
