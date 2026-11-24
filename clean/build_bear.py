"""Clean character for the polar bear page: fixed outline through the printed dots, rig parts, and a crisp ink layer.
The camera only supplies the child's colors inside these shapes."""
import json, math, numpy as np, cv2
from shapely.geometry import Polygon, Point, box, LineString
from shapely.ops import unary_union
from shapely import affinity
TG = '/home/claude/repo-marymarii/scan/targets'
OX, OY = 420.7, 298.6                      # a4 region origin: dot list below is in crop coords
D = {1:(242,372),2:(241,348),3:(259,331),4:(256,306),5:(266,285),6:(243,234),7:(253,182),8:(269,136),9:(241,85),10:(259,49),
 11:(299,59),12:(312,91),13:(377,75),14:(449,91),15:(470,54),16:(508,53),17:(515,95),18:(489,133),19:(505,183),20:(503,247),
 21:(482,292),22:(493,308),23:(490,330),24:(499,349),25:(497,368),26:(536,350),27:(566,321),28:(596,276),29:(617,236),30:(654,225),
 31:(680,256),32:(680,308),33:(655,357),34:(628,398),35:(586,438),36:(540,471),37:(571,530),38:(584,588),39:(587,645),40:(579,701),
 41:(561,757),42:(539,811),43:(530,862),44:(539,905),45:(545,938),46:(508,942),47:(468,948),48:(443,920),49:(422,885),50:(412,853),
 51:(364,854),52:(318,853),53:(304,889),54:(289,921),55:(263,946),56:(225,942),57:(189,938),58:(188,910),59:(200,864),60:(190,806),
 61:(167,751),62:(150,698),63:(144,644),64:(151,591),65:(170,540),66:(132,556),67:(107,593),68:(62,600),69:(45,568),70:(55,516),
 71:(88,468),72:(143,432),73:(198,404)}
DOT_R = 10.5
A4 = np.array([(D[k][0] + OX, D[k][1] + OY) for k in range(1, 74)])

def chaikin(pts, it=2):
    for _ in range(it):
        q = []
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            q += [a * .75 + b * .25, a * .25 + b * .75]
        pts = np.array(q)
    return pts

def snap(pts, size):
    """refine each dot centre on the page itself (and carry the a4 list over to letter)"""
    g = cv2.imread(f'/home/claude/ar/gen/pages/{size}/bear.png', 0)
    bw = (g < 110).astype(np.uint8)
    op = cv2.morphologyEx(bw, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13)))
    n, lab, st, cen = cv2.connectedComponentsWithStats(op, 8)
    C = np.array([cen[i] for i in range(1, n) if 14 <= st[i][2] <= 34 and 14 <= st[i][3] <= 34])
    if size != 'a4':
        da = json.load(open(f'{TG}/bear_a4.json'))['region']; dl = json.load(open(f'{TG}/bear_{size}.json'))['region']
        s = (dl[2] - dl[0]) / (da[2] - da[0]); pts = (pts - [da[0], da[1]]) * s + [dl[0], dl[1]]
        for _ in range(3):   # nearest-dot matching, then a similarity fit
            m = np.array([C[np.argmin(((C - p) ** 2).sum(1))] for p in pts])
            ok = np.sqrt(((m - pts) ** 2).sum(1)) < 25
            M, _ = cv2.estimateAffinePartial2D(pts[ok].astype(np.float32), m[ok].astype(np.float32))
            pts = pts @ M[:, :2].T + M[:, 2]
            T = M
    out = []
    for p in pts:
        j = np.argmin(((C - p) ** 2).sum(1)); q = C[j]
        out.append(q if np.hypot(*(q - p)) < 9 else p)
    return np.array(out), g

def build(size):
    P, g = snap(A4.copy(), size)
    k = json.load(open(f'/home/claude/clean/bear_{size}.orig.json'))
    x0, y0, x1, y1 = k['region']
    sc = (P[72] - P[0]); unit = np.hypot(*(P[29] - P[9])) / np.hypot(*(A4[29] - A4[9]))   # page scale vs a4
    to = lambda x, y: ((x + OX - 420.7) , (y + OY - 298.6))
    # a4 crop coords -> this page's target px, via the dot fit
    src = A4.astype(np.float32); M, _ = cv2.estimateAffinePartial2D(src, P.astype(np.float32))
    T = lambda pts: (np.array(pts, float).reshape(-1, 2) + [OX, OY]) @ M[:, :2].T + M[:, 2]
    path = chaikin(P, 2)
    full = Polygon(path).buffer(0)
    inset = (DOT_R - 1.5) * unit
    shape = full.buffer(-inset, join_style=1).buffer(3 * unit).buffer(-3 * unit)   # inner edge of the dots, gently rounded
    # rig cuts (a4 crop coords)
    neck = Polygon(T([(150, -50), (520, -50), (520, 300), (480, 296), (370, 314), (265, 298), (150, 300)]))
    neck_ov = Polygon(T([(150, -50), (522, -50), (522, 318), (480, 318), (370, 334), (265, 320), (150, 322)]))
    armR_cut = Polygon(T([(505, 150), (900, 150), (900, 520), (541, 490), (505, 340)]))   # shoulder line (520,340)-(560,480), 22 px overlap
    armR_core = Polygon(T([(527, 150), (900, 150), (900, 520), (563, 490), (527, 340)]))
    armL_cut = Polygon(T([(-100, 380), (238, 380), (192, 628), (-100, 628)]))
    armL_core = Polygon(T([(-100, 380), (218, 380), (172, 628), (-100, 628)]))
    head = shape.intersection(neck_ov)
    jR = Point(*T([(532, 405)])[0]).buffer(38 * unit)            # round shoulder joint, so the seam never shows
    armR = unary_union([shape.intersection(armR_cut), shape.intersection(jR)]).difference(neck)
    armL = shape.intersection(armL_cut)
    body = shape.difference(neck).difference(armR_core).difference(armL_core)
    def polys(gm):
        gm = gm.buffer(0)
        geoms = [gm] if gm.geom_type == 'Polygon' else list(gm.geoms)
        return [[[round(x, 1), round(y, 1)] for x, y in np.array(p.exterior.coords)[:-1]] for p in geoms if p.area > 50]
    piv = lambda x, y: [round(v, 1) for v in T([(x, y)])[0]]
    k['body'] = polys(body)
    k['parts'] = [
        dict(name='armL', polys=polys(armL), pivot=piv(205, 430), order=5, motion=dict(type='rot', amp=.07, phase=1.1, speed=.8)),
        dict(name='armR', polys=polys(armR), pivot=piv(532, 405), order=7, motion=dict(type='rot', amp=.16, sign=1, phase=0, speed=1.2)),
        dict(name='head', polys=polys(head), pivot=piv(372, 318), order=8, motion=dict(type='rot', amp=.06, phase=.8, speed=.8)),
    ]
    k['eyes'] = [[*piv(338, 165), 8 * unit], [*piv(415, 165), 8 * unit]]
    k['lid'] = [piv(338, 146), piv(415, 146)]
    k['bodyPivot'] = piv(372, 700)
    # ---- ink layer at 2x the target resolution, over the region ----
    S = 2; W = int(round((x1 - x0) * S)); H = int(round((y1 - y0) * S))
    up = cv2.resize(g, None, fx=S, fy=S, interpolation=cv2.INTER_CUBIC)
    ox, oy = int(round(x0 * S)), int(round(y0 * S))
    crop = up[oy:oy + H, ox:ox + W].astype(np.float32)
    ink = np.clip((200 - crop) / 120, 0, 1)                          # soft dark lines
    # keep only lines well inside the outline, away from dots and numbers
    keep = np.zeros((H, W), np.uint8)
    inner = shape.buffer(-5 * unit)
    cv2.fillPoly(keep, [((np.array(p.exterior.coords) - [x0, y0]) * S).astype(np.int32) for p in ([inner] if inner.geom_type == 'Polygon' else inner.geoms)], 1)
    for i, p in enumerate(P):  # numbers that fall inside the outline: hand and neck clusters
        if not (i + 1 in (1, 2, 3, 4, 5, 21, 22, 23, 24, 25) or 63 <= i + 1 <= 68): continue
        cv2.circle(keep, (int((p[0] - x0) * S), int((p[1] - y0) * S)), int(34 * unit * S), 0, -1)
    ink *= keep
    # the outline, drawn clean along the inner edge of the dots
    line = np.zeros((H, W), np.uint8)
    for p in ([shape] if shape.geom_type == 'Polygon' else shape.geoms):
        c = ((np.array(p.exterior.coords) - [x0, y0]) * S * 4).astype(np.int32)
        cv2.polylines(line, [c], True, 255, int(round(6 * unit * S)), cv2.LINE_AA, shift=2)
    ink = np.maximum(ink, line / 255.0)
    rgba = np.zeros((H, W, 4), np.uint8); rgba[..., 0] = 34; rgba[..., 1] = 26; rgba[..., 2] = 24; rgba[..., 3] = (ink * 255).astype(np.uint8)
    cv2.imwrite(f'{TG}/bear_{size}_ink.png', cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA))
    k['clean'] = dict(ink=f'bear_{size}_ink.png')
    json.dump(k, open(f'{TG}/bear_{size}.json', 'w'))
    # preview
    pv = cv2.cvtColor(g, cv2.COLOR_GRAY2BGR)
    for nm, gm, col in [('body', body, (0, 200, 0)), ('head', head, (255, 0, 0)), ('armR', armR, (0, 0, 255)), ('armL', armL, (255, 0, 255))]:
        for p in polys(gm): cv2.polylines(pv, [np.array(p, np.int32)], True, col, 2)
    cv2.imwrite(f'pv_{size}.png', pv[int(y0):int(y1), int(x0):int(x1)])
    print(size, 'ok', W, H, round(unit, 3))

if __name__ == '__main__':
    for s in ('a4', 'letter'):
        build(s)
