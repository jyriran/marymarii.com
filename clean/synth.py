import json, numpy as np, cv2, sys
from build_bear import A4, chaikin
from shapely.geometry import Polygon
rng=np.random.default_rng(3)
g=cv2.imread('/home/claude/ar/gen/pages/a4/bear.png',0)
H,W=g.shape
col=np.full((H,W,3),255,np.float32)
def crayon(mask,rgb,density=0.85):
    layer=np.zeros((H,W),np.float32)
    ys,xs=np.where(mask>0); 
    if len(xs)==0: return
    for _ in range(int(len(xs)/40)):
        i=rng.integers(len(xs)); x,y=xs[i],ys[i]; a=rng.uniform(-0.5,0.5)+1.1
        L=rng.uniform(15,40); dx,dy=np.cos(a)*L,np.sin(a)*L
        cv2.line(layer,(int(x-dx),int(y-dy)),(int(x+dx),int(y+dy)),rng.uniform(0.6,1.0),2,cv2.LINE_AA)
    layer=np.clip(cv2.GaussianBlur(layer,(0,0),0.8)*1.4,0,1)*(mask>0)*density
    for c in range(3): col[...,c]=col[...,c]*(1-layer)+rgb[c]*layer
body=np.zeros((H,W),np.uint8)
poly=Polygon(chaikin(A4,1)).buffer(-14)
cv2.fillPoly(body,[np.array(poly.exterior.coords,np.int32)],1)
crayon(body,(60,150,245))
# scarf: flood from inside the printed scarf lines
lines=(g<140).astype(np.uint8); lines=cv2.dilate(lines,np.ones((3,3),np.uint8))
ff=lines.copy()*1; bb=np.ones_like(ff); bb[298+300:298+520,420+262:420+500]=0; ff[bb>0]=1; m=np.zeros((H+2,W+2),np.uint8)
for sx,sy in [(331+420,340+298),(455+420,340+298),(340+420,440+298),(440+420,440+298)]:
    cv2.floodFill(ff,m,(sx,sy),2)
scarf=((ff==2)).astype(np.uint8)
print('scarf px',scarf.sum())
crayon(scarf,(190,150,240),0.95)
out=(col*(g[...,None]/255.0)).clip(0,255).astype(np.uint8)
cv2.imwrite('bear_kid_flat.png',out)
# photo: perspective onto a desk
desk=np.zeros((2000,1500,3),np.uint8); desk[:]=(60,110,160)
desk=(desk+rng.normal(0,6,desk.shape)).clip(0,255).astype(np.uint8)
src=np.float32([[0,0],[W,0],[W,H],[0,H]]); dst=np.float32([[220,180],[1300,240],[1380,1800],[120,1760]])
M=cv2.getPerspectiveTransform(src,dst)
pw=cv2.warpPerspective(out,M,(1500,2000),borderValue=(0,0,0)); mk=cv2.warpPerspective(np.ones((H,W),np.uint8),M,(1500,2000))
ph=np.where(mk[...,None]>0,pw,desk)
ph=(ph*np.linspace(1.0,0.82,1500)[None,:,None]).astype(np.uint8)   # uneven light
ph=cv2.GaussianBlur(ph,(0,0),1.0)
cv2.imwrite('bear_kid_photo.jpg',ph,[cv2.IMWRITE_JPEG_QUALITY,88])
