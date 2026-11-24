"""Fixtures for the AR prototype: printable penguin page, kid-colored copy, part map, fake camera video."""
import json, math, random, re, subprocess, os, sys
import numpy as np, cv2
from shapely.geometry import LineString, Polygon, box, mapping
from shapely.ops import unary_union
from shapely import affinity
from engine import fit, path_d
from chars import penguin
import build
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as rl_canvas

OUT = '/home/claude/ar/fixtures'
os.makedirs(OUT, exist_ok=True)
random.seed(7)

ch = penguin()
P = ch['parts']
fl_l, fl_r, ft_l, ft_r, body, belly, hat, band, pom = [p.geom for p in P]
allg = unary_union([p.geom for p in P])
s, tx, ty = fit(allg.bounds, (660, 50, 1880, 1870), pad=70)   # same as engine.build_sheet

def to_canvas(g):
    return affinity.translate(affinity.scale(g, s, s, origin=(0, 0)), tx, ty)

# ---------- 1. kid-colored sheet (1920 canvas) ----------
svg = open('new/penguin.svg').read()
dots = [(float(a), float(b)) for a, b in re.findall(r'<circle cx="([\d.]+)" cy="([\d.]+)" r="21"', svg)]

def crayon(geom, color, ang, spill=5):
    g = to_canvas(geom).buffer(spill * random.uniform(.5, 1.4), resolution=6)
    out = f'<path d="{path_d(g, True)}" fill="{color}" fill-opacity="0.78" stroke="none"/>'
    minx, miny, maxx, maxy = g.bounds
    L = max(maxx - minx, maxy - miny) * 1.6
    cx, cy = (minx + maxx) / 2, (miny + maxy) / 2
    lines = []
    for k in range(-int(L / 13), int(L / 13)):
        off = k * 13 + random.uniform(-3, 3)
        a = math.radians(ang + random.uniform(-4, 4))
        dx, dy = math.cos(a), math.sin(a); nx, ny = -dy, dx
        p0 = (cx + nx * off - dx * L / 2, cy + ny * off - dy * L / 2); p1 = (cx + nx * off + dx * L / 2, cy + ny * off + dy * L / 2)
        lines.append(LineString([p0, p1]))
    h = unary_union(lines).intersection(g)
    out += f'<path d="{path_d(h)}" stroke="{color}" stroke-opacity="0.55" stroke-width="7" fill="none" stroke-linecap="round"/>'
    return out

kid = ''.join([
    crayon(fl_l, '#2f55b3', 35), crayon(fl_r, '#2f55b3', 35), crayon(body.difference(belly), '#2f55b3', 30),
    crayon(belly.difference(hat), '#ffe27a', -25, 2), crayon(ft_l, '#f08a24', 10), crayon(ft_r, '#f08a24', 10),
    crayon(hat, '#26a65b', 50), crayon(band, '#f4c2d7', 0, 2), crayon(pom, '#e8384f', 20, 2),
])
trace = 'M' + ' L'.join(f'{x + random.uniform(-3, 3):.1f},{y + random.uniform(-3, 3):.1f}' for x, y in dots + dots[:1])
kid += f'<path d="{trace}" fill="none" stroke="#4a4a4a" stroke-width="6" stroke-linejoin="round" stroke-linecap="round"/>'
# insert fills right after the colored reference group so they sit under the puzzle lines and dots
i = svg.index('<g transform', svg.index('<g transform') + 10)
open(f'{OUT}/penguin_kid_layer.svg', 'w').write('<svg xmlns="http://www.w3.org/2000/svg" width="1920" height="1920" viewBox="0 0 1920 1920">' + kid + '</svg>')
subprocess.run(['rsvg-convert', '-w', '2400', f'{OUT}/penguin_kid_layer.svg', '-o', f'{OUT}/penguin_kid_layer.png'], check=True)
_bw = cv2.imread('img_bw/penguin.png').astype(np.float32) / 255
_ly = cv2.imread(f'{OUT}/penguin_kid_layer.png', cv2.IMREAD_UNCHANGED).astype(np.float32) / 255
_a = _ly[..., 3:4]; _crayon = _ly[..., :3] * _a + (1 - _a)
cv2.imwrite(f'{OUT}/penguin_kid.png', (_bw * _crayon * 255).clip(0, 255).astype(np.uint8))

# ---------- 2. single printable pages (blank + kid) ----------
def page(img, path):
    c = rl_canvas.Canvas(path, pagesize=A4)
    build.sheet(c, *A4, 'penguin', 'Penguin', 42, 2, 7, img=img, total=15)
    c.save()
    return build.sheet.art_box

art = page(None, f'{OUT}/penguin_page.pdf')
NAME_BOXES = list(build.sheet.name_boxes)
page(f'{OUT}/penguin_kid.png', f'{OUT}/penguin_kid_page.pdf')
DPI = 150
for n in ('penguin_page', 'penguin_kid_page'):
    subprocess.run(['pdftoppm', '-r', str(DPI), '-png', '-singlefile', f'{OUT}/{n}.pdf', f'{OUT}/{n}'], check=True)
tw, th = cv2.imread(f'{OUT}/penguin_page.png').shape[1::-1]

# ---------- 3. part map in target-image pixels (y down) ----------
W, H = A4
X0, Y0, S = art
k = DPI / 72
def to_px(g):
    g = to_canvas(g)
    g = affinity.scale(g, S / 1920 * k, S / 1920 * k, origin=(0, 0))
    return affinity.translate(g, X0 * k, (H - (Y0 + S)) * k)
def pt_px(x, y):
    p = to_px(LineString([(x, y), (x + 1, y)]))
    return list(p.coords[0])

hat_g = unary_union([hat, band, pom])
groups = {
    'body': unary_union([body, belly]).difference(hat_g),
    'flipL': fl_l.difference(body), 'flipR': fl_r.difference(body),
    'footL': ft_l.difference(body), 'footR': ft_r.difference(body),
    'hat': hat_g,
}
def poly_list(g):
    g = to_px(g).simplify(0.6)
    polys = [g] if g.geom_type == 'Polygon' else list(g.geoms)
    return [[[round(x, 1), round(y, 1)] for x, y in p.exterior.coords[:-1]] for p in polys if p.area > 30]
region = to_px(allg).bounds
pad = 12
region = [region[0] - pad, region[1] - pad, region[2] + pad, region[3] + pad]
data = {
    'target': {'width': tw, 'height': th},
    'region': [round(v, 1) for v in region],
    'parts': {n: poly_list(g) for n, g in groups.items()},
    'nameBoxes': [[round(bx * k, 1), round((H - (by + bh)) * k, 1), round((bx + bw) * k, 1), round((H - by) * k, 1)] for bx, by, bw, bh in NAME_BOXES],
    'silhouette': poly_list(unary_union([p.geom for p in P]).buffer(22)),
    'pivots': {
        'flipL': pt_px(255, 560), 'flipR': pt_px(745, 560),
        'footL': pt_px(440, 1085), 'footR': pt_px(560, 1085),
        'hat': pt_px(500, 470), 'base': pt_px(500, 1110),
    },
    'eyes': [pt_px(420, 548) + [24 * s * S / 1920 * k], pt_px(580, 548) + [24 * s * S / 1920 * k]],
    'lidSample': [pt_px(420, 590), pt_px(580, 590)],
}
json.dump(data, open(f'{OUT}/penguin_parts.json', 'w'))
if 'novideo' in sys.argv: raise SystemExit
print('target', tw, th, 'region', data['region'])

import sys
if 'nojson' in sys.argv: raise SystemExit
# ---------- 4. fake camera video of the kid page on a table ----------
kidpg = cv2.imread(f'{OUT}/penguin_kid_page.png')
FW, FH, N = 720, 960, 48
yy, xx = np.mgrid[0:FH, 0:FW]
wood = (np.stack([np.full((FH, FW), 92), np.full((FH, FW), 130), np.full((FH, FW), 168)], -1)
        + 18 * np.sin(xx[..., None] / 9.0 + np.sin(yy[..., None] / 40.0) * 3)).clip(0, 255).astype(np.uint8)
frames = []
for f in range(N):
    t = f / N * 2 * math.pi
    cx, cy = FW / 2 + 18 * math.sin(t), FH / 2 + 12 * math.cos(t)
    ph = 820 + 20 * math.sin(t * .5); pw = ph * tw / th
    ang = math.radians(4 * math.sin(t))
    tilt = 0.07 + 0.02 * math.sin(t)
    corners = np.array([[-pw / 2 * (1 - tilt), -ph / 2], [pw / 2 * (1 - tilt), -ph / 2], [pw / 2, ph / 2], [-pw / 2, ph / 2]])
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
        cv2.imwrite(f'{OUT}/cam_frame0.jpg', frame)
with open(f'{OUT}/cam.y4m', 'wb') as fh:
    fh.write(f'YUV4MPEG2 W{FW} H{FH} F15:1 Ip A1:1 C420jpeg\n'.encode())
    for fr in frames:
        yuv = cv2.cvtColor(fr, cv2.COLOR_BGR2YUV_I420)
        fh.write(b'FRAME\n'); fh.write(yuv.tobytes())
print('video', FW, FH, N)
