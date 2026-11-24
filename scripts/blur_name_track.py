import cv2, numpy as np
cap=cv2.VideoCapture('/mnt/user-data/uploads/81a22cc7-my-bear-came-alive_4.mp4')
F=[]
while True:
    ok,f=cap.read()
    if not ok: break
    F.append(f)
n=len(F); fps=30; print(n)
boxes=[None]*n
def track(start, box, rng):
    t=cv2.TrackerCSRT_create(); t.init(F[start], box); boxes[start]=box
    for i in rng:
        ok,b=t.update(F[i])
        if ok: boxes[i]=tuple(int(v) for v in b)
A=int(10*fps); B=int(5*fps)
track(A,(55,345,150,48),range(A+1,n)); track(A,(55,345,150,48),range(A-1,int(8.4*fps),-1))
track(B,(620,1108,148,95),range(B+1,int(8.4*fps))); track(B,(620,1108,148,95),range(B-1,int(1.9*fps),-1))
miss=0
for i,f in enumerate(F):
    b=boxes[i]
    if b is None:
        if 1.9*fps<=i: miss+=1
        continue
    x,y,w,h=b; p=18
    x0,y0=max(0,x-p),max(0,y-p); x1,y1=min(f.shape[1],x+w+p),min(f.shape[0],y+h+p)
    if x1>x0 and y1>y0:
        roi=f[y0:y1,x0:x1]; f[y0:y1,x0:x1]=cv2.GaussianBlur(cv2.resize(cv2.resize(roi,(max(1,(x1-x0)//12),max(1,(y1-y0)//12))),(x1-x0,y1-y0)),(0,0),6)
print('missing',miss)
h,w=F[0].shape[:2]; ch=int(w*16/9)  # 1365
out=cv2.VideoWriter('/home/claude/bear4/blur.mp4',cv2.VideoWriter_fourcc(*'mp4v'),fps,(w,h))
for f in F: out.write(f)
out.release()
for t in [3,5,7.9,8.6,9.5,10,12,14]:
    cv2.imwrite(f'/home/claude/bear4/chk_{t}.jpg', cv2.resize(F[min(n-1,int(t*fps))],(256,494)))
