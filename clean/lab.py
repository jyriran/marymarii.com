import json, sys, numpy as np, cv2
from build_clean import page, find_dots
key=sys.argv[1]
d=json.load(open(f'orig/{key}_a4.json')); g=page(key,'a4'); x0,y0,x1,y1=[int(v) for v in d['region']]
C,r=find_dots(g)
im=cv2.cvtColor(g,cv2.COLOR_GRAY2BGR)
idx=[i for i,c in enumerate(C) if x0-10<c[0]<x1+10 and y0-10<c[1]<y1+10]
for i in idx:
    c=C[i]; cv2.circle(im,(int(c[0]),int(c[1])),int(r),(0,0,255),2); cv2.putText(im,str(i),(int(c[0])-10,int(c[1])+28),0,0.6,(255,0,0),2)
json.dump({str(i):[float(C[i][0]),float(C[i][1])] for i in idx},open(f'C_{key}.json','w'))
cv2.imwrite(f'/tmp/lab_{key}.png',im[y0-10:y1+10,x0-10:x1+10])
print(len(idx))
