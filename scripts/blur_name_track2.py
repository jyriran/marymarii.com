import cv2
cap=cv2.VideoCapture('trim.mp4'); F=[]
while True:
    ok,f=cap.read()
    if not ok: break
    F.append(f)
n=len(F); A=int(9.75*30); box=(198,302,152,46)
boxes={}
def track(rng):
    t=cv2.TrackerCSRT_create(); t.init(F[A],box); boxes[A]=box
    for i in rng:
        ok,b=t.update(F[i])
        if ok: boxes[i]=tuple(int(v) for v in b)
        else: break
track(range(A+1,n)); track(range(A-1,int(5.8*30),-1))
print(n, min(boxes), max(boxes), len(boxes))
for i,(x,y,w,h) in boxes.items():
    f=F[i]; p=16; x0,y0,x1,y1=max(0,x-p),max(0,y-p),min(f.shape[1],x+w+p),min(f.shape[0],y+h+p)
    roi=f[y0:y1,x0:x1]; f[y0:y1,x0:x1]=cv2.GaussianBlur(cv2.resize(cv2.resize(roi,(max(1,(x1-x0)//12),max(1,(y1-y0)//12))),(x1-x0,y1-y0)),(0,0),6)
out=cv2.VideoWriter('blur_raw.mp4',cv2.VideoWriter_fourcc(*'mp4v'),30,(F[0].shape[1],F[0].shape[0]))
for f in F: out.write(f)
out.release()
for t in [6.4,6.7,7.2,8,9,10.2]:
    cv2.imwrite(f'chk_{t}.jpg',cv2.resize(F[min(n-1,int(t*30))],(220,397)))
