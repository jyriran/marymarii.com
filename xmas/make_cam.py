import math, numpy as np, cv2, sys
OUT='/home/claude/ar/fixtures'; SRC=sys.argv[1]; DST=sys.argv[2]; TILT=float(sys.argv[3]) if len(sys.argv)>3 else 0.07; FORE=float(sys.argv[4]) if len(sys.argv)>4 else 1.0
tw, th = cv2.imread(f'{OUT}/'+SRC).shape[1::-1]
# ---------- 4. fake camera video of the kid page on a table ----------
kidpg = cv2.imread(f'{OUT}/'+SRC)
import os
FW, FH, N = int(os.environ.get('FW', 720)), int(os.environ.get('FH', 960)), 48
yy, xx = np.mgrid[0:FH, 0:FW]
wood = (np.stack([np.full((FH, FW), 92), np.full((FH, FW), 130), np.full((FH, FW), 168)], -1)
        + 18 * np.sin(xx[..., None] / 9.0 + np.sin(yy[..., None] / 40.0) * 3)).clip(0, 255).astype(np.uint8)
frames = []
for f in range(N):
    t = f / N * 2 * math.pi
    cx, cy = FW / 2 + 18 * math.sin(t), FH / 2 + 12 * math.cos(t)
    ph = FH * 0.86 + 20 * math.sin(t * .5); pw = ph * tw / th
    ang = math.radians(4 * math.sin(t))
    tilt = TILT + 0.02 * math.sin(t)
    corners = np.array([[-pw / 2 * (1 - tilt), -ph / 2 * FORE], [pw / 2 * (1 - tilt), -ph / 2 * FORE], [pw / 2, ph / 2 * FORE], [-pw / 2, ph / 2 * FORE]])
    R = np.array([[math.cos(ang), -math.sin(ang)], [math.sin(ang), math.cos(ang)]])
    dst = (corners @ R.T + [cx, cy]).astype(np.float32)
    src = np.array([[0, 0], [tw, 0], [tw, th], [0, th]], np.float32)
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(kidpg, M, (FW, FH), borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
    mask = cv2.warpPerspective(np.full((th, tw), 255, np.uint8), M, (FW, FH))
    frame = np.where(mask[..., None] > 0, warped, wood)
    light = (0.82 + 0.25 * (1 - ((xx - FW * .3) ** 2 + (yy - FH * .2) ** 2) / (FW * FW * 1.2))).clip(.7, 1.1)
    frame = (frame * light[..., None]).clip(0, 255).astype(np.uint8)
    frame = cv2.GaussianBlur(frame, (3, 3), 0.8)
    frame = (frame + np.random.normal(0, 3, frame.shape)).clip(0, 255).astype(np.uint8)
    frames.append(frame)
    if f == 0:
        pass
with open(f'{OUT}/'+DST, 'wb') as fh:
    fh.write(f'YUV4MPEG2 W{FW} H{FH} F15:1 Ip A1:1 C420jpeg\n'.encode())
    for fr in frames:
        yuv = cv2.cvtColor(fr, cv2.COLOR_BGR2YUV_I420)
        fh.write(b'FRAME\n'); fh.write(yuv.tobytes())
print('video', FW, FH, N)
