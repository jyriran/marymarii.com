"""Dot-to-dot sheet engine: one shape model -> colored reference + numbered-dot puzzle."""
import math
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union
from shapely import affinity

INK = '#1E120C'
W = H = 1920

# ---------- shape helpers (local coords, y down) ----------
def ellipse(cx, cy, rx, ry, rot=0):
    p = Point(0, 0).buffer(1, resolution=48)
    p = affinity.scale(p, rx, ry, origin=(0, 0))
    p = affinity.rotate(p, rot, origin=(0, 0))
    return affinity.translate(p, cx, cy)

def circle(cx, cy, r): return ellipse(cx, cy, r, r)

def poly(pts, round_r=0):
    g = Polygon(pts)
    if round_r:
        g = g.buffer(-round_r, join_style=1).buffer(round_r, join_style=1)
    return g

def capsule(p1, p2, w):
    return LineString([p1, p2]).buffer(w / 2, resolution=24)

def soften(g, r):
    return g.buffer(r, resolution=24).buffer(-r, resolution=24)

def star(cx, cy, ro, ri, n=5, rot=-90):
    pts = []
    for i in range(2 * n):
        r = ro if i % 2 == 0 else ri
        a = math.radians(rot + i * 180 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return Polygon(pts)

# ---------- svg helpers ----------
def _lines(g):
    if g.is_empty: return []
    t = g.geom_type
    if t == 'LineString' or t == 'LinearRing': return [list(g.coords)]
    if t == 'Polygon': return [list(g.exterior.coords)] + [list(r.coords) for r in g.interiors]
    if hasattr(g, 'geoms'):
        out = []
        for s in g.geoms: out += _lines(s)
        return out
    return []

def path_d(g, closed=False):
    d = []
    for pts in _lines(g):
        if len(pts) < 2: continue
        d.append('M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + (' Z' if closed else ''))
    return ' '.join(d)

def fill_path(g, fill, stroke, sw):
    polys = [g] if g.geom_type == 'Polygon' else [p for p in getattr(g, 'geoms', []) if p.geom_type == 'Polygon']
    out = ''
    for p in polys:
        d = path_d(p, closed=True)
        out += f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="round" fill-rule="evenodd"/>'
    return out

def stroke_path(g, sw, color=INK, dash=None, min_len=0):
    if min_len and hasattr(g, 'geoms'):
        g = unary_union([s for s in g.geoms if s.length >= min_len]) if any(s.length >= min_len for s in g.geoms) else LineString()
    d = path_d(g)
    if not d: return ''
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"{da}/>'

# ---------- textures ----------
def rings(geom, step, n, start=None):
    out = []
    start = start or step
    for i in range(n):
        g = geom.buffer(-(start + i * step))
        if g.is_empty: break
        out.append(g.boundary)
    return unary_union(out) if out else LineString()

def scallops(geom, sp, r):
    """little 'u' marks on a staggered grid inside geom (fur / knit texture)."""
    minx, miny, maxx, maxy = geom.bounds
    inner = geom.buffer(-r * 1.6)
    arcs = []
    row = 0
    y = miny + sp * 0.6
    while y < maxy:
        x = minx + (sp / 2 if row % 2 else 0) + sp * 0.4
        while x < maxx:
            if inner.contains(Point(x, y)):
                pts = [(x + r * math.cos(math.radians(a)), y + r * 0.8 * math.sin(math.radians(a))) for a in range(0, 181, 20)]
                arcs.append(LineString(pts))
            x += sp
        y += sp * 0.8; row += 1
    return unary_union(arcs) if arcs else LineString()

def dashes(geom, sp, ln, ang=80, jitter=True):
    """short fur strokes on a grid."""
    minx, miny, maxx, maxy = geom.bounds
    inner = geom.buffer(-ln * 0.8)
    out = []; row = 0; y = miny
    while y < maxy:
        x = minx + (sp / 2 if row % 2 else 0)
        while x < maxx:
            if inner.contains(Point(x, y)):
                a = math.radians(ang + (((int(x * 7 + y * 3)) % 21) - 10 if jitter else 0))
                dx, dy = math.cos(a) * ln / 2, math.sin(a) * ln / 2
                out.append(LineString([(x - dx, y - dy), (x + dx, y + dy)]))
            x += sp
        y += sp * 0.75; row += 1
    return unary_union(out) if out else LineString()

# ---------- character model ----------
class Part:
    def __init__(self, geom, fill, tex=None, sil=True, tex_color=None, dash=False, puzzle=True):
        self.geom, self.fill, self.tex, self.sil, self.dash, self.puzzle = geom, fill, tex, sil, dash, puzzle
        self.tex_color = tex_color

def textures(parts, i, sw):
    p = parts[i]
    if p.tex is None: return LineString()
    above = unary_union([q.geom for q in parts[i + 1:]]) if i + 1 < len(parts) else Polygon()
    region = p.geom.difference(above)
    t = p.tex(p.geom) if callable(p.tex) else p.tex
    return t.intersection(region.buffer(-sw))

def render_colored(parts, details, sw):
    s = ''
    for i, p in enumerate(parts):
        s += fill_path(p.geom, p.fill, INK, sw)
        above_parts = parts[i + 1:]
        t = textures(parts, i, sw)
        if not t.is_empty:
            s += stroke_path(t, sw * 0.45, p.tex_color or INK, dash=f'{sw*2.4:.1f} {sw*2.2:.1f}' if p.dash else None)
    s += details(True, sw)
    return s

def render_puzzle(parts, details, sw, sil):
    s = ''
    edge = sil.exterior.buffer(sw * 0.9)
    for i, p in enumerate(parts):
        if not p.puzzle: continue
        above = unary_union([q.geom for q in parts[i + 1:]]) if i + 1 < len(parts) else Polygon()
        vis = p.geom.boundary.difference(above).difference(edge)
        s += stroke_path(vis, sw, min_len=sw * 5)
        t = textures(parts, i, sw)
        if not t.is_empty:
            s += stroke_path(t, sw * 0.55, dash=f'{sw*2.4:.1f} {sw*2.2:.1f}' if p.dash else None)
    s += details(False, sw)
    return s

# ---------- dots ----------
def sample_outline(ring, target):
    line = LineString(ring.coords)
    total = line.length
    simp = list(line.simplify(10).coords)[:-1]
    n = len(simp)
    corners = []
    for i in range(n):
        a, b, c = simp[i - 1], simp[i], simp[(i + 1) % n]
        a1 = math.atan2(b[1] - a[1], b[0] - a[0]); a2 = math.atan2(c[1] - b[1], c[0] - b[0])
        turn = abs((a2 - a1 + math.pi) % (2 * math.pi) - math.pi)
        if turn > math.radians(38):
            corners.append(line.project(Point(b)))
    corners = sorted(set(round(d, 1) for d in corners)) or [0.0]

    def gen(g):
        pts = []  # (d, is_corner)
        m = len(corners)
        for i in range(m):
            d0 = corners[i]; d1 = corners[(i + 1) % m] + (total if i + 1 == m else 0)
            L = d1 - d0
            k = max(1, round(L / g))
            for j in range(k):
                pts.append(((d0 + L * j / k) % total, j == 0))
        # merge close points, keep corners
        out = []
        for d, c in pts:
            p = line.interpolate(d).coords[0]
            if out and math.dist(p, out[-1][0]) < g * 0.62:
                if c and not out[-1][1]: out[-1] = (p, c)
                continue
            out.append((p, c))
        while len(out) > 2 and math.dist(out[-1][0], out[0][0]) < g * 0.62:
            out.pop()
        return [p for p, _ in out]

    lo, hi = 5.0, total / 6
    best = None
    for _ in range(60):
        g = (lo + hi) / 2
        p = gen(g)
        if best is None or abs(len(p) - target) < abs(len(best) - target): best = p
        if len(p) > target: lo = g
        elif len(p) < target: hi = g
        else: break
    return best

def order_points(pts, start_xy):
    area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
    if area < 0:  # make clockwise on screen (y down)
        pts = pts[::-1]
    k = min(range(len(pts)), key=lambda i: math.dist(pts[i], start_xy))
    return pts[k:] + pts[:k]

def place_labels(pts, sil, fs, R, keepout):
    placed = []
    dots = [Point(p).buffer(R + 4) for p in pts]
    sil_in = sil.buffer(-6)
    n = len(pts)
    labels = []
    for i, p in enumerate(pts):
        txt = str(i + 1)
        w = 0.58 * fs * len(txt); h = 0.74 * fs
        a, b = pts[i - 1], pts[(i + 1) % n]
        tx, ty = b[0] - a[0], b[1] - a[1]
        L = math.hypot(tx, ty) or 1
        nx, ny = ty / L, -tx / L
        if sil.contains(Point(p[0] + nx * 15, p[1] + ny * 15)): nx, ny = -nx, -ny
        base = math.atan2(ny, nx)
        best = None
        for off in (0, 25, -25, 50, -50, 75, -75, 105, -105, 140, -140):
            for extra in (6, 20):
                ang = base + math.radians(off)
                ux, uy = math.cos(ang), math.sin(ang)
                d = R + extra + abs(ux) * w / 2 + abs(uy) * h / 2
                cx, cy = p[0] + ux * d, p[1] + uy * d
                rect = box(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
                score = 0
                score += sum(10 for j, dt in enumerate(dots) if rect.intersects(dt))
                score += sum(10 for r in placed if rect.buffer(3).intersects(r))
                score += 4 * rect.intersection(sil_in).area / rect.area * 10
                score += 10 if any(rect.intersects(k) for k in keepout) else 0
                score += abs(off) / 200 + (extra - 6) / 100
                if best is None or score < best[0]: best = (score, cx, cy, rect)
        placed.append(best[3]); labels.append((txt, best[1], best[2], best[0]))
    return labels

# ---------- sheet ----------
def fit(bounds, region, pad=0):
    minx, miny, maxx, maxy = bounds
    rx0, ry0, rx1, ry1 = region
    s = min((rx1 - rx0 - 2 * pad) / (maxx - minx), (ry1 - ry0 - 2 * pad) / (maxy - miny))
    tx = rx0 + (rx1 - rx0 - (maxx - minx) * s) / 2 - minx * s
    ty = ry0 + (ry1 - ry0 - (maxy - miny) * s) / 2 - miny * s
    return s, tx, ty

def build_sheet(char, path_svg, layout='right'):
    parts, details = char['parts'], char['details']
    sil_local = char.get('dotsil') or unary_union([p.geom for p in parts if p.sil])
    if sil_local.geom_type != 'Polygon':
        sil_local = max(sil_local.geoms, key=lambda g: g.area)
    sil_local = Polygon(sil_local.exterior)
    allg = unary_union([p.geom for p in parts] + [char.get('extra_bounds', Polygon())])
    if layout == 'right':
        pz_region = (660, 50, 1880, 1870); ref_region = (40, 1080, 640, 1880)
    else:
        pz_region = (40, 50, 1260, 1870); ref_region = (1280, 40, 1880, 840)
    s, tx, ty = fit(allg.bounds, pz_region, pad=70)
    rs, rtx, rty = fit(allg.bounds, ref_region, pad=20)
    sw_p = 9 / s; sw_r = 6 / rs

    sil = affinity.translate(affinity.scale(sil_local, s, s, origin=(0, 0)), tx, ty)
    pts = sample_outline(sil.exterior, char['dots'])
    sx, sy = char['start']
    pts = order_points(pts, (sx * s + tx, sy * s + ty))
    R, fs = 21, 42
    ref_box = box(*ref_region)
    ko = [ref_box]
    for p in parts:
        if not p.sil and p.puzzle:
            out = p.geom.difference(sil_local)
            if out.area > 50:
                ko.append(affinity.translate(affinity.scale(out, s, s, origin=(0, 0)), tx, ty).buffer(4))
    labels = place_labels(pts, sil, fs, R, ko)
    bad = [l for l in labels if l[3] >= 4]

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
           '<rect width="100%" height="100%" fill="white"/>',
           f'<g transform="translate({rtx:.2f},{rty:.2f}) scale({rs:.5f})">{render_colored(parts, details, sw_r)}</g>',
           f'<g transform="translate({tx:.2f},{ty:.2f}) scale({s:.5f})">{render_puzzle(parts, details, sw_p, sil_local)}</g>']
    for (x, y) in pts:
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{R}" fill="{INK}"/>')
    for txt, cx, cy, _ in labels:
        out.append(f'<text x="{cx:.1f}" y="{cy + fs * 0.36:.1f}" font-family="Liberation Sans, Arial, sans-serif" font-weight="700" font-size="{fs}" text-anchor="middle" fill="{INK}">{txt}</text>')
    out.append('</svg>')
    open(path_svg, 'w').write('\n'.join(out))
    return len(pts), len(bad)
