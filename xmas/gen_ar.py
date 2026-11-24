"""Generate AR data for every sheet and paper size:
   pages/<size>/<key>.png   printed page at 150 dpi (recognition target)
   ardata/<key>_<size>.json rig, silhouette, name boxes, paper samples (target px)
   stills/<key>_<size>.jpg  kid-colored, named test photo with real perspective"""
import json, math, os, random, subprocess, sys
import numpy as np, cv2
from shapely.geometry import Polygon, Point, box, LineString
from shapely.ops import unary_union
from shapely import affinity
from reportlab.lib.pagesizes import A4, letter
from reportlab.pdfgen import canvas as rl_canvas
import build
from engine import fit
from chars import CHARS
from chars2 import CHARS2
CHARS.update(CHARS2)
from licensed_outline import full_silhouette, ink_silhouette

DPI = 150
OUT = '/home/claude/ar/gen'
for d in ('pages/a4', 'pages/letter', 'ardata', 'stills'):
    os.makedirs(f'{OUT}/{d}', exist_ok=True)
SIZES = {'a4': A4, 'letter': letter}
ORDER = [s[0] for s in build.SHEETS]
LICENSED = {'santa': 'union', 'snowman': 'union', 'bear': 'ink', 'reindeer': 'ink'}

def page_geometry(size):
    c = rl_canvas.Canvas('/tmp/_probe.pdf', pagesize=SIZES[size])
    build.sheet(c, *SIZES[size], 'penguin', 'Penguin', 42, 2, 7)
    return build.sheet.art_box, list(build.sheet.name_boxes)

# ---------------- rigs for the sheets drawn by the engine (local coords) ----------------
def rig_for(key, P):
    U = unary_union
    if key == 'penguin':
        fl_l, fl_r, ft_l, ft_r, body, belly, hat, band, pom = P
        hatg = U([hat, band, pom]); bodyg = U([body, belly]).difference(hatg)
        return dict(motion='dance', body=bodyg, parts=[
            dict(name='flipL', geom=fl_l.difference(body), pivot=(255, 560), order=5, motion=dict(type='flap', amp=.45, base=.25, sign=-1, phase=0)),
            dict(name='flipR', geom=fl_r.difference(body), pivot=(745, 560), order=5, motion=dict(type='flap', amp=.45, base=.25, sign=1, phase=.6)),
            dict(name='footL', geom=ft_l.difference(body), pivot=(440, 1085), order=4, parent='root', motion=dict(type='tap', amp=.22, sign=1, phase=0)),
            dict(name='footR', geom=ft_r.difference(body), pivot=(560, 1085), order=4, parent='root', motion=dict(type='tap', amp=.22, sign=-1, phase=math.pi)),
            dict(name='hat', geom=hatg, pivot=(500, 470), order=8, motion=dict(type='rot', amp=.16, phase=1.2))],
            eyes=[(420, 548, 24), (580, 548, 24)], lid=[(420, 590), (580, 590)])
    if key == 'gingerbread':
        g, bow = P
        return dict(motion='dance', body=U([g, bow]), parts=[], eyes=[(430, 255, 26), (570, 255, 26)], lid=[(430, 205), (570, 205)])
    if key == 'tree':
        trunk, pot, t3, t2, t1, star = P
        return dict(motion='dance', body=U([trunk, pot, t3, t2, t1]).difference(star), parts=[
            dict(name='star', geom=star, pivot=(500, 85), order=8, motion=dict(type='twinkle'))],
            eyes=[(470, 345, 18), (530, 345, 18)], lid=[(500, 322), (500, 322)])
    if key == 'fox':
        tail, tip = P[0], P[1]; rest = U(P[2:])
        return dict(motion='dance', body=rest, parts=[
            dict(name='tail', geom=U([tail, tip]).difference(rest), pivot=(650, 985), order=4, motion=dict(type='rot', amp=.32, speed=1.6, phase=0))],
            eyes=[(420, 365, 24), (580, 365, 24)], lid=[(420, 318), (580, 318)])
    if key == 'owl':
        keep = [g for i, g in enumerate(P) if i not in (7, 8)]          # feet only exist in the color guide
        return dict(motion='dance', body=U(keep), parts=[], eyes=[(405, 475, 36), (595, 475, 36)], lid=[(405, 385), (595, 385)])
    if key == 'bunny':
        ear_l, ear_r, in_l, in_r = P[:4]; rest = U(P[4:]); head = P[8]
        return dict(motion='bounce', body=rest, parts=[
            dict(name='earL', geom=U([ear_l, in_l]).difference(head), pivot=(420, 335), order=4, motion=dict(type='rot', amp=.2, speed=1.3, phase=0)),
            dict(name='earR', geom=U([ear_r, in_r]).difference(head), pivot=(580, 335), order=4, motion=dict(type='rot', amp=.2, speed=1.3, phase=math.pi))],
            eyes=[(430, 470, 22), (570, 470, 22)], lid=[(430, 425), (570, 425)])
    if key == 'hedgehog':
        return dict(motion='bounce', body=U(P), parts=[], eyes=[(430, 730, 22), (570, 730, 22)], lid=[(430, 690), (570, 690)])
    if key == 'gift':
        loop_l, loop_r, boxg, rib_v, lid, rib_lid, knot = P
        lidg = U([loop_l, loop_r, lid, rib_lid, knot])
        return dict(motion='bounce', body=U([boxg, rib_v]).difference(lidg), parts=[
            dict(name='lid', geom=lidg, pivot=(195, 545), order=8, motion=dict(type='pop', amp=0.07))], eyes=[], lid=[])
    if key == 'bell':
        clap, bodyb, rim = P[0], P[1], P[2]; bell = U([bodyb, rim])
        return dict(motion='swing', pivot=(500, 240), body=bell, parts=[
            dict(name='clapper', geom=clap.difference(bell), pivot=(500, 885), order=4, motion=dict(type='rot', amp=.35, phase=-.7))],
            eyes=[(435, 560, 22), (565, 560, 22)], lid=[(500, 470), (500, 470)])
    if key == 'stocking':
        return dict(motion='swing', pivot=(515, 145), body=U(P), parts=[], eyes=[(455, 780, 20), (565, 780, 20)], lid=[(510, 730), (510, 730)])
    if key == 'house':
        return dict(motion='bounce', body=U(P), parts=[], eyes=[], lid=[], smoke=(680, 285))
    raise KeyError(key)

def engine_mapping(key):
    ch = CHARS[key]()
    allg = unary_union([p.geom for p in ch['parts']] + [ch.get('extra_bounds', Polygon())])
    s, tx, ty = fit(allg.bounds, (660, 50, 1880, 1870), pad=70)
    return ch, (lambda g: affinity.translate(affinity.scale(g, s, s, origin=(0, 0)), tx, ty)), (lambda x, y: (x * s + tx, y * s + ty))

def to_page(art, H):
    X0, Y0, S = art; k = DPI / 72
    def f(g):   # 1920-canvas geometry -> page px
        g = affinity.scale(g, S / 1920 * k, S / 1920 * k, origin=(0, 0))
        return affinity.translate(g, X0 * k, (H - (Y0 + S)) * k)
    def fp(x, y):
        return (X0 * k + x * S / 1920 * k, (H - (Y0 + S)) * k + y * S / 1920 * k)
    return f, fp

def polys(g, tol=0.6):
    g = g.buffer(0).simplify(tol)
    ps = [g] if g.geom_type == 'Polygon' else [q for q in getattr(g, 'geoms', []) if q.geom_type == 'Polygon']
    return [[[round(x, 1), round(y, 1)] for x, y in p.exterior.coords[:-1]] for p in ps if p.area > 30]

def paper_spots(blank, sil, region, art_px):
    """four blank patches of paper around the drawing, used to white-balance the camera image"""
    x0, y0, x1, y1 = region; ax0, ay0, ax1, ay1 = art_px
    keep = sil.buffer(28)
    spots = []
    for cx, cy in ((x0, y0), (x1, y0), (x0, y1), (x1, y1)):
        best = None
        for r in range(0, 260, 6):
            for a in range(0, 360, 20):
                x = cx + r * math.cos(math.radians(a)); y = cy + r * math.sin(math.radians(a))
                if not (ax0 + 10 < x < ax1 - 10 and ay0 + 10 < y < ay1 - 10): continue
                if keep.contains(Point(x, y)): continue
                patch = blank[int(y) - 9:int(y) + 10, int(x) - 9:int(x) + 10]
                if patch.size and patch.min() > 235: best = (round(x, 1), round(y, 1)); break
            if best: break
        spots.append(best or (cx, cy))
    return spots

def crayon_layer(shape_px, parts_px, rnd):
    """kid coloring: a color per part, slightly outside the lines, with hatching"""
    h, w = shape_px
    layer = np.full((h, w, 3), 255, np.uint8)
    pal = [(226, 87, 76), (47, 85, 179), (38, 166, 91), (240, 138, 36), (147, 92, 196), (242, 193, 78), (233, 56, 79), (88, 172, 220)]
    for g in parts_px:
        col = pal[rnd.randrange(len(pal))]
        g = g.buffer(rnd.uniform(1, 4))
        for p in ([g] if g.geom_type == 'Polygon' else list(g.geoms)):
            if p.geom_type != 'Polygon' or p.area < 40: continue
            m = np.zeros((h, w), np.uint8)
            cv2.fillPoly(m, [np.array(p.exterior.coords, np.int32)], 255)
            for hole in p.interiors: cv2.fillPoly(m, [np.array(hole.coords, np.int32)], 0)
            ang = rnd.uniform(0, 180); hatch = np.zeros((h, w), np.uint8)
            dx, dy = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            for t in range(-max(h, w), max(h, w), 7):
                cx, cy = w / 2 - dy * t, h / 2 + dx * t
                cv2.line(hatch, (int(cx - dx * 3000), int(cy - dy * 3000)), (int(cx + dx * 3000), int(cy + dy * 3000)), 255, 3)
            fill = np.array(col, np.float32)
            a = (m > 0)[..., None] * 0.72
            layer = (layer * (1 - a) + fill * a).astype(np.uint8)
            hb = ((m > 0) & (hatch > 0))[..., None] * 0.25
            layer = (layer * (1 - hb) + (fill * 0.75) * hb).astype(np.uint8)
    return layer

def write_name(img, boxes, name, rnd):
    from PIL import Image, ImageDraw, ImageFont
    F = '/home/claude/listing/node_modules/@fontsource/'
    font = rnd.choice([F + 'schoolbell/files/schoolbell-latin-400-normal.woff', F + 'gochi-hand/files/gochi-hand-latin-400-normal.woff'])
    im = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    for ch, (x0, y0, x1, y1) in zip(name, boxes):
        f = ImageFont.truetype(font, int((y1 - y0) * 0.78) + rnd.randint(-4, 4))
        L = Image.new('RGBA', (int(x1 - x0) * 2, int(y1 - y0) * 2), (0, 0, 0, 0)); g = ImageDraw.Draw(L)
        g.text((L.width / 2, L.height / 2), ch, font=f, fill=(55, 55, 65, 255), anchor='mm', stroke_width=1, stroke_fill=(55, 55, 65, 255))
        L = L.rotate(rnd.uniform(-8, 8), resample=Image.BICUBIC)
        im.paste(L, (int((x0 + x1) / 2 + rnd.uniform(-3, 3) - L.width / 2), int((y0 + y1) / 2 + rnd.uniform(-3, 3) - L.height / 2)), L)
    return cv2.cvtColor(np.array(im), cv2.COLOR_RGB2BGR)

def perspective(pg, seed):
    th, tw = pg.shape[:2]; rnd = random.Random(seed)
    FW, FH = 720, 960; f = 900.; ang = math.radians(rnd.uniform(14, 26)); scale = 0.00055 * 1754 / th; d = 1.05
    roll = math.radians(rnd.uniform(-5, 5))
    def proj(X, Y):
        x = (X - tw / 2) * scale; y = (Y - th / 2) * scale
        x, y = x * math.cos(roll) - y * math.sin(roll), x * math.sin(roll) + y * math.cos(roll)
        return [FW / 2 + f * x / (d - y * math.sin(ang)), FH / 2 + f * y * math.cos(ang) / (d - y * math.sin(ang))]
    src = np.float32([[0, 0], [tw, 0], [tw, th], [0, th]]); dst = np.float32([proj(0, 0), proj(tw, 0), proj(tw, th), proj(0, th)])
    M = cv2.getPerspectiveTransform(src, dst); bg = np.full((FH, FW, 3), (92, 130, 168), np.uint8)
    w = cv2.warpPerspective(pg, M, (FW, FH)); m = cv2.warpPerspective(np.full((th, tw), 255, np.uint8), M, (FW, FH))
    fr = np.where(m[..., None] > 0, w, bg)
    yy, xx = np.mgrid[0:FH, 0:FW]
    light = (0.86 + 0.18 * (1 - ((xx - FW * .35) ** 2 + (yy - FH * .25) ** 2) / (FW * FW * 1.3))).clip(.75, 1.05)
    fr = (fr * light[..., None]).clip(0, 255).astype(np.uint8)
    return cv2.GaussianBlur(fr, (3, 3), 0.7)

NAMES = ['MIA', 'Leo', 'OSKAR', 'Emma', 'NOAH', 'Lily', 'MAX', 'Sofia', 'ADA', 'Hugo', 'EVA', 'Liam', 'ROSE', 'Otto', 'ZOE']

def main(sizes=('a4', 'letter'), keys=None, pdf_pages=True):
    keys = keys or ORDER
    pdfs = {'a4': 'MaryMariiArt_Christmas_Dot_to_Dot_A4.pdf', 'letter': 'MaryMariiArt_Christmas_Dot_to_Dot_Letter.pdf'}
    for size in sizes:
        W, H = SIZES[size]
        art, name_boxes = page_geometry(size)
        k = DPI / 72
        art_px = (art[0] * k, (H - (art[1] + art[2])) * k, (art[0] + art[2]) * k, (H - art[1]) * k)
        nb = [[round(bx * k, 1), round((H - (by + bh)) * k, 1), round((bx + bw) * k, 1), round((H - by) * k, 1)] for bx, by, bw, bh in name_boxes]
        to_px, to_px_pt = to_page(art, H)
        for key in keys:
            idx = ORDER.index(key)
            png = f'{OUT}/pages/{size}/{key}.png'
            if pdf_pages or not os.path.exists(png):
                subprocess.run(['pdftoppm', '-r', str(DPI), '-png', '-singlefile', '-f', str(idx + 3), '-l', str(idx + 3), pdfs[size], png[:-4]], check=True)
            blank = cv2.imread(png, 0); th, tw = blank.shape
            if key in LICENSED:
                img_scale = 1920 / 2400
                if LICENSED[key] == 'union': sil2400, _, _ = full_silhouette(key)
                else: sil2400 = ink_silhouette(key)
                sil = to_px(affinity.scale(sil2400, img_scale, img_scale, origin=(0, 0)))
                rig = dict(motion={'santa': 'dance', 'snowman': 'bounce', 'bear': 'dance', 'reindeer': 'bounce'}[key], body=sil, parts=[], eyes=[], lid=[])
                rig_px = rig; parts_for_color = [sil]
                body_pivot = None
            else:
                ch, to_canvas, pt_canvas = engine_mapping(key)
                r = rig_for(key, [p.geom for p in ch['parts']])
                conv = lambda g: to_px(to_canvas(g))
                convp = lambda x, y: to_px_pt(*pt_canvas(x, y))
                sil = unary_union([conv(r['body'])] + [conv(p['geom']) for p in r['parts']])
                rig_px = dict(motion=r['motion'], body=conv(r['body']), parts=[dict(p, geom=conv(p['geom']), pivot=convp(*p['pivot'])) for p in r['parts']],
                              eyes=[], lid=[list(convp(x, y)) for x, y in r['lid']])
                es = (pt_canvas(1, 0)[0] - pt_canvas(0, 0)[0]) * (to_px_pt(1, 0)[0] - to_px_pt(0, 0)[0])
                rig_px['eyes'] = [list(convp(x, y)) + [rr * es] for x, y, rr in r['eyes']]
                body_pivot = convp(*r['pivot']) if 'pivot' in r else None
                if 'smoke' in r: rig_px['smoke'] = convp(*r['smoke'])
                parts_for_color = [rig_px['body']] + [p['geom'] for p in rig_px['parts']]
            if sil.geom_type != 'Polygon': sil = max(sil.geoms, key=lambda g: g.area)
            sil = Polygon(sil.exterior)
            minx, miny, maxx, maxy = sil.bounds
            region = [round(minx - 12, 1), round(miny - 12, 1), round(maxx + 12, 1), round(maxy + 12, 1)]
            base = ((minx + maxx) / 2, maxy)
            data = {
                'key': key, 'size': size, 'target': {'width': tw, 'height': th}, 'region': region,
                'silhouette': polys(sil.buffer(10), 1.0), 'nameBoxes': nb,
                'paper': [list(p) for p in paper_spots(blank, sil, region, art_px)],
                'base': [round(base[0], 1), round(base[1], 1)], 'top': [round((minx + maxx) / 2, 1), round(miny, 1)],
                'motion': rig_px['motion'], 'bodyPivot': [round(v, 1) for v in body_pivot] if body_pivot else None,
                'body': polys(rig_px['body']),
                'parts': [dict(name=p['name'], polys=polys(p['geom']), pivot=[round(v, 1) for v in p['pivot']], order=p['order'], parent=p.get('parent', 'body'), motion=p['motion']) for p in rig_px['parts']],
                'eyes': [[round(v, 1) for v in e] for e in rig_px['eyes']], 'lid': [[round(v, 1) for v in l] for l in rig_px['lid']],
                'smoke': [round(v, 1) for v in rig_px['smoke']] if rig_px.get('smoke') else None,
            }
            json.dump(data, open(f'{OUT}/ardata/{key}_{size}.json', 'w'))
            # kid-colored test photo with a handwritten name
            rnd = random.Random(f'{key}-{size}')
            pg = cv2.imread(png)
            layer = crayon_layer(pg.shape[:2], parts_for_color, rnd)
            kid = (pg.astype(np.float32) / 255 * layer.astype(np.float32)).astype(np.uint8)
            kid = write_name(kid, nb, NAMES[idx], rnd)
            cv2.imwrite(f'{OUT}/stills/{key}_{size}_flat.png', kid)
            cv2.imwrite(f'{OUT}/stills/{key}_{size}.jpg', perspective(kid, f'{key}{size}'), [cv2.IMWRITE_JPEG_QUALITY, 92])
            print(size, key, 'parts', len(data['parts']), 'eyes', len(data['eyes']), 'paper', data['paper'])

if __name__ == '__main__':
    main()
