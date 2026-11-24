"""Drawn-character data for every page: clean outline through the printed dots, parts clipped to it, crisp ink layer."""
import json, sys, numpy as np, cv2
from shapely.geometry import Polygon, Point, MultiPolygon
from shapely.ops import unary_union
from build_bear import chaikin
TG = '/home/claude/repo-marymarii/scan/targets'
LIC = {'santa', 'snowman', 'reindeer'}
def page(key, size):
    import re
    p = (f'/home/claude/ar/genabc/pages/{size}/{key}.png' if key.startswith('abc-') else f'/home/claude/ar/gen123/pages/{size}/{key}.png' if re.fullmatch(r'n\d+', key)
         else f'/home/claude/ar/gen/pages/{size}/{key}.png')
    return cv2.imread(p, 0)
def find_dots(g):
    bw = (g < 110).astype(np.uint8)
    op = cv2.morphologyEx(bw, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11)))
    n, lab, st, cen = cv2.connectedComponentsWithStats(op, 8)
    C = [(cen[i], st[i][2]) for i in range(1, n) if 12 <= st[i][2] <= 34 and 12 <= st[i][3] <= 34 and 0.7 < st[i][2] / st[i][3] < 1.4]
    return np.array([c for c, _ in C]), float(np.median([w for _, w in C])) / 2
def geoms(gm):
    gm = gm.buffer(0)
    if gm.is_empty: return []
    return [gm] if gm.geom_type == 'Polygon' else [p for p in gm.geoms if p.geom_type == 'Polygon']
def polys(gm):
    return [[[round(x, 1), round(y, 1)] for x, y in np.array(p.exterior.coords)[:-1]] for p in geoms(gm) if p.area > 60]

from spec import SPEC
def spec_shape(key, size, d, g, C, r):
    """licensed art: the dot paths (read off the page), plus closed art regions and stick arms outside them"""
    da = json.load(open(f'orig/{key}_a4.json'))['region']; dr = d['region']
    k = (dr[2] - dr[0]) / (da[2] - da[0])
    ox, oy = int(da[0]) - 10, int(da[1]) - 10
    to = lambda pts: [((x + ox - da[0]) * k + dr[0], (y + oy - da[1]) * k + dr[1]) for x, y in pts]
    def snapP(pts):
        out = []
        for p in to(pts):
            p = np.array(p); j = np.argmin(((C - p) ** 2).sum(1)); out.append(C[j] if np.hypot(*(C[j] - p)) < 10 * k else p)
        return np.array(out)
    S = SPEC[key]; H, W = g.shape
    path = np.zeros((H, W), np.uint8)
    for pts in S['paths']: cv2.fillPoly(path, [chaikin(snapP(pts), 1).astype(np.int32)], 1)
    for pts in S['fills']: cv2.fillPoly(path, [snapP(pts).astype(np.int32)], 1)
    e = int(round(r - 1.5)); path = cv2.erode(path, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * e + 1, 2 * e + 1)))
    extra = np.zeros((H, W), np.uint8)
    lines = (g < 150).astype(np.uint8)
    for pts in S['paths']: cv2.polylines(lines, [snapP(pts).astype(np.int32)], True, 1, 3)   # floods stop at the dot path
    spec_shape.dots = np.vstack([snapP(p) for p in S['paths']])
    reg = (dr[2] - dr[0]) * (dr[3] - dr[1])
    for sx, sy in to(S['seeds']):
        ff = lines.copy(); m = np.zeros((H + 2, W + 2), np.uint8)
        if ff[int(sy), int(sx)]: continue
        cv2.floodFill(ff, m, (int(sx), int(sy)), 2)
        reg_m = (ff == 2).astype(np.uint8)
        if reg_m.sum() < 0.08 * reg: extra |= cv2.dilate(reg_m, np.ones((7, 7), np.uint8))
    for bx in S['sticks']:
        (ax, ay), (bx2, by2) = to([(bx[0], bx[1]), (bx[2], bx[3])])
        m = np.zeros((H, W), np.uint8); m[int(ay):int(by2), int(ax):int(bx2)] = (g < 150)[int(ay):int(by2), int(ax):int(bx2)]
        n2, l2, s2, _ = cv2.connectedComponentsWithStats(m, 8)
        m = np.isin(l2, [i for i in range(1, n2) if s2[i][4] > 400]).astype(np.uint8)   # the stick, not dots or numbers
        extra |= cv2.dilate(m, np.ones((5, 5), np.uint8))
    allm = cv2.morphologyEx(path | extra, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
    cs, _ = cv2.findContours(allm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    ps = [Polygon(c[:, 0, :]).buffer(0) for c in cs if cv2.contourArea(c) > 200]
    return unary_union(ps).buffer(1.5).buffer(-1.5).simplify(0.6)

def inset(U, e):
    core = U.buffer(-e, join_style=1)
    thin = U.difference(core.buffer(e + 1.5, join_style=1)).buffer(-0.8)   # horns, tails, whiskers: too thin to pull in, keep them whole
    return unary_union([core, thin]).buffer(2.5).buffer(-2.5)

def build(key, size):
    d = json.load(open(f'orig/{key}_{size}.json')); g = page(key, size)
    x0, y0, x1, y1 = d['region']
    body = unary_union([Polygon(p).buffer(0) for p in d['body']])
    parts = [(pt, unary_union([Polygon(p).buffer(0) for p in pt['polys']])) for pt in d['parts']]
    U = unary_union([body] + [p for _, p in parts])
    C, r = find_dots(g)
    unit = r / 11.0 if not (key.startswith('abc-') or key[:1] == 'n') else r / 7.0
    if key in LIC:
        base = None
    else:
        base = U
    shape = spec_shape(key, size, d, g, C, r) if key in LIC else inset(base, r - 1.5)
    new_body = body.intersection(shape)
    d['body'] = polys(new_body)
    nparts = []
    for pt, gm in parts:
        cl = gm.intersection(shape) if key not in LIC else gm.intersection(shape)
        if cl.is_empty or cl.area < 60: continue
        pt = dict(pt); pt['polys'] = polys(cl); nparts.append(pt)
    d['parts'] = nparts
    allshape = unary_union([Polygon(p) for p in d['body']] + [Polygon(p) for pt in nparts for p in pt['polys']])
    # ink at 2x over the region
    S = 2; W = int(round((x1 - x0) * S)); H = int(round((y1 - y0) * S))
    up = cv2.resize(g, None, fx=S, fy=S, interpolation=cv2.INTER_CUBIC)
    ox, oy = int(round(x0 * S)), int(round(y0 * S))
    crop = np.full((H, W), 255, np.float32)
    sy0, sx0 = max(0, oy), max(0, ox); sy1, sx1 = min(up.shape[0], oy + H), min(up.shape[1], ox + W)
    crop[sy0 - oy:sy1 - oy, sx0 - ox:sx1 - ox] = up[sy0:sy1, sx0:sx1]
    ink = np.clip((200 - crop) / 120, 0, 1)
    keep = np.zeros((H, W), np.uint8)
    inner = shape.buffer(-4 * unit)
    for p in geoms(inner):
        cv2.fillPoly(keep, [((np.array(p.exterior.coords) - [x0, y0]) * S).astype(np.int32)], 1)
        for h in p.interiors: cv2.fillPoly(keep, [((np.array(h.coords) - [x0, y0]) * S).astype(np.int32)], 0)
    # printed dots and their numbers that land inside the outline (inner dot paths, concave spots)
    bw = (g < 140).astype(np.uint8)
    n, lab, st, cen = cv2.connectedComponentsWithStats(bw, 8)
    small = [i for i in range(1, n) if max(st[i][2], st[i][3]) <= 26 * unit and 7 * unit <= st[i][3] <= 24 * unit and x0 - 5 < st[i][0] < x1 + 5 and y0 - 5 < st[i][1] < y1 + 5]
    def erase(i):
        x, y, w, h, a = st[i]
        m = (lab[y:y + h, x:x + w] == i).astype(np.uint8)
        m = cv2.dilate(cv2.resize(m, None, fx=S, fy=S, interpolation=cv2.INTER_NEAREST), np.ones((5, 5), np.uint8))
        yy, xx = int(y * S - oy), int(x * S - ox)
        if yy < 0 or xx < 0 or yy + m.shape[0] > H or xx + m.shape[1] > W: return
        keep[yy:yy + m.shape[0], xx:xx + m.shape[1]][m > 0] = 0
    for c in (spec_shape.dots if key in LIC else C):
        lbl = [i for i in small if np.hypot(*(cen[i] - c)) < 2.4 * r + 16 * unit and np.hypot(*(cen[i] - c)) > r * 0.8]
        if not lbl: continue
        cv2.circle(keep, (int((c[0] - x0) * S), int((c[1] - y0) * S)), int((r + 3) * S), 0, -1)
        for i in lbl: erase(i)
    if key in LIC:
        da = json.load(open(f'orig/{key}_a4.json'))['region']; kk = (x1 - x0) / (da[2] - da[0])
        for ex, ey, er in SPEC[key].get('erase', []):
            px = ((ex + int(da[0]) - 10 - da[0]) * kk + x0 - x0) * S; py = ((ey + int(da[1]) - 10 - da[1]) * kk) * S
            cv2.circle(keep, (int(px), int(py)), int(er * kk * S), 0, -1)
    ink *= keep
    line = np.zeros((H, W), np.uint8)
    for p in geoms(shape):
        for ring in [p.exterior] + list(p.interiors):
            c = ((np.array(ring.coords) - [x0, y0]) * S * 4).astype(np.int32)
            cv2.polylines(line, [c], True, 255, max(4, int(round(0.55 * r * S))), cv2.LINE_AA, shift=2)
    ink = np.maximum(ink, line / 255.0)
    rgba = np.zeros((H, W, 4), np.uint8); rgba[..., 0] = 34; rgba[..., 1] = 26; rgba[..., 2] = 24; rgba[..., 3] = (ink * 255).astype(np.uint8)
    cv2.imwrite(f'{TG}/{key}_{size}_ink.png', cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA), [cv2.IMWRITE_PNG_COMPRESSION, 9])
    d['clean'] = dict(ink=f'{key}_{size}_ink.png')
    json.dump(d, open(f'{TG}/{key}_{size}.json', 'w'))
    # preview: page + parts + ink side by side
    pv = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
    cols = [(0, 200, 0), (255, 0, 0), (0, 0, 255), (255, 0, 255), (0, 160, 255), (160, 0, 160)]
    for p in d['body']: cv2.polylines(pv, [np.array(p, np.int32)], True, cols[0], 2)
    for j, pt in enumerate(nparts):
        for p in pt['polys']: cv2.polylines(pv, [np.array(p, np.int32)], True, cols[1 + j % 5], 2)
    a = ink[..., None]; w = (255 * (1 - a)).astype(np.uint8).repeat(3, 2)
    w = cv2.resize(w, (int(x1 - x0), int(y1 - y0)))
    left = pv[int(max(0, y0)):int(y0) + w.shape[0], int(max(0, x0)):int(x0) + w.shape[1]]
    h = min(left.shape[0], w.shape[0]); ww = min(left.shape[1], w.shape[1])
    cv2.imwrite(f'pv/{key}_{size}.jpg', cv2.resize(np.hstack([left[:h, :ww], w[:h, :ww]]), None, fx=0.5, fy=0.5))
    return key

if __name__ == '__main__':
    import os; os.makedirs('pv', exist_ok=True)
    for key in sys.argv[1:]:
        for size in ('a4', 'letter'):
            try: build(key, size)
            except Exception as e: print('FAIL', key, size, e)
        print(key, flush=True)
