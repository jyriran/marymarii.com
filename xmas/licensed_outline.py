import cv2, numpy as np, shapely
from shapely.geometry import MultiPoint, Point, box
REF = {'santa': (0, .54, .34, 1), 'snowman': (0, .57, .34, 1), 'bear': (0, .52, .37, 1), 'reindeer': (.6, 0, 1, .53)}
DOTS = {'santa': 48, 'snowman': 40, 'bear': 73, 'reindeer': 59}
def dots(k):
    im = cv2.imread(f'img_bw/{k}.png', 0); h, w = im.shape
    bw = (im < 110).astype(np.uint8) * 255
    bw = cv2.morphologyEx(bw, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31)))
    cs, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cand = []
    for c in cs:
        a = cv2.contourArea(c); p = cv2.arcLength(c, True)
        if a < 150 or p == 0: continue
        circ = 4 * np.pi * a / p / p
        x, y, cw, ch = cv2.boundingRect(c)
        mask = np.zeros((ch, cw), np.uint8); cv2.drawContours(mask, [c - [x, y]], -1, 255, -1)
        solid = (bw[y:y + ch, x:x + cw][mask > 0] > 0).mean()
        if circ > 0.7 and solid > 0.9 and 0.75 < cw / ch < 1.33:
            cand.append((x + cw / 2, y + ch / 2, a))
    areas = np.array([c[2] for c in cand]); med = np.median(areas)
    rx0, ry0, rx1, ry1 = REF[k]
    pts = [(x, y) for x, y, a in cand if 0.55 * med < a < 1.8 * med and not (rx0 * w < x < rx1 * w and ry0 * h < y < ry1 * h)]
    return pts, med
if __name__ == '__main__':
    out = []
    for k in REF:
        pts, med = dots(k)
        r = np.sqrt(med / np.pi)
        hull = shapely.concave_hull(MultiPoint(pts), ratio=0.12).buffer(r * 1.3).simplify(3)
        im = cv2.cvtColor(cv2.imread(f'img_bw/{k}.png', 0), cv2.COLOR_GRAY2BGR)
        for x, y in pts: cv2.circle(im, (int(x), int(y)), int(r) + 4, (0, 0, 255), 4)
        cv2.polylines(im, [np.array(hull.exterior.coords, np.int32)], True, (255, 0, 0), 6)
        print(k, 'dots found', len(pts), 'expected', DOTS[k], 'r', round(r, 1))
        out.append(cv2.resize(im, (600, 600)))
    cv2.imwrite('/tmp/lic_outline.png', np.hstack(out))

def ink_silhouette(k, dot_pts=None):
    """Outline of the whole printed drawing (dots, labels, lines), as a shapely Polygon in 2400px image coords."""
    from shapely.geometry import Polygon
    im = cv2.imread(f'img_bw/{k}.png', 0); h, w = im.shape
    ink = (im < 170).astype(np.uint8) * 255
    rx0, ry0, rx1, ry1 = REF[k]
    ink[int(ry0 * h):int(ry1 * h), int(rx0 * w):int(rx1 * w)] = 0
    m = cv2.dilate(ink, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (45, 45)))
    ff = m.copy(); mask = np.zeros((h + 2, w + 2), np.uint8); cv2.floodFill(ff, mask, (0, 0), 255)
    m = m | cv2.bitwise_not(ff)
    m = cv2.erode(m, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (29, 29)))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    big = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]); m = (lab == big).astype(np.uint8) * 255
    cs, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    c = max(cs, key=cv2.contourArea)[:, 0, :]
    return Polygon(c).buffer(0).simplify(4)

def full_silhouette(k):
    from shapely.ops import unary_union
    from shapely.geometry import Polygon
    pts, med = dots(k)
    r = np.sqrt(med / np.pi)
    hull = shapely.concave_hull(MultiPoint(pts), ratio=0.35).buffer(r * 1.3)
    u = unary_union([ink_silhouette(k), hull]).buffer(6).buffer(-6)
    if u.geom_type != 'Polygon': u = max(u.geoms, key=lambda g: g.area)
    return Polygon(u.exterior).simplify(4), pts, r
