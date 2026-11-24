import cv2, numpy as np, json, sys
# usage: python3 comp.py AM|NZ
Q=json.load(open('quads.json'))
A='pages/'
SET=sys.argv[1] if len(sys.argv)>1 else 'AM'
JOB={'AM':{'1':['color_A'],'2':['color_B'],'3':['bw_C','color_D'],'4':['bw_K'],'5':['color_E'],'6':['color_L'],'7':['color_F']},
     'NZ':{'1':['color_R'],'2':['color_P'],'3':['bw_O','color_T'],'4':['bw_W'],'5':['color_U'],'6':['color_Z'],'7':['color_N']}}[SET]
names={'AM':{'1':'desk-alligator','2':'kitchen-bear','3':'two-pages','4':'classroom-clipboard','5':'held-up-elephant','6':'playroom-lion','7':'fridge-fish'},
       'NZ':{'1':'desk-rabbit','2':'kitchen-pig','3':'two-pages','4':'classroom-clipboard','5':'held-up-unicorn','6':'playroom-zebra','7':'fridge-narwhal'}}[SET]
def place(scene, page, quad):
    H,W=scene.shape[:2]; ph,pw=page.shape[:2]
    M=cv2.getPerspectiveTransform(np.float32([[0,0],[pw,0],[pw,ph],[0,ph]]),np.float32(quad))
    warp=cv2.warpPerspective(page,M,(W,H),flags=cv2.INTER_AREA if pw>800 else cv2.INTER_CUBIC,borderValue=(255,255,255))
    quadm=np.zeros((H,W),np.uint8); cv2.fillConvexPoly(quadm,np.int32(quad),255)
    hsv=cv2.cvtColor(scene,cv2.COLOR_BGR2HSV)
    paper=((hsv[...,2]>150)&(hsv[...,1]<55)).astype(np.uint8)*255
    paper=cv2.morphologyEx(paper,cv2.MORPH_OPEN,np.ones((5,5),np.uint8))
    m=cv2.bitwise_and(paper,quadm)
    inv=cv2.bitwise_and(255-m,quadm); n,lab,st,_=cv2.connectedComponentsWithStats(inv)
    for i in range(1,n):
        if st[i,cv2.CC_STAT_AREA]<400: m[lab==i]=255
    m=cv2.erode(m,np.ones((3,3),np.uint8))
    mf=cv2.GaussianBlur(m.astype(np.float32)/255,(5,5),0)
    L=scene.astype(np.float32); k=(61,61)
    num=cv2.GaussianBlur(L*(m[...,None]/255.),k,0); den=cv2.GaussianBlur((m/255.).astype(np.float32),k,0)[...,None]+1e-4
    shade=num/den; ref=np.percentile(shade[m>0],97,axis=0); S=np.clip(shade/ref,0,1.08)
    res=L*(1-mf[...,None])+warp.astype(np.float32)*S*mf[...,None]
    return np.clip(res,0,255).astype(np.uint8)
for k,pages in JOB.items():
    sc=cv2.imread(f'scenes/s{k}.png')
    for pg,q in zip(pages,Q[k]): sc=place(sc,cv2.imread(A+pg+'.jpg'),q)
    cv2.imwrite(f'out/MaryMarii-ABC-{SET}-mockup-{k}-{names[k]}.jpg',sc,[cv2.IMWRITE_JPEG_QUALITY,93])
