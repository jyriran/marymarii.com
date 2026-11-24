"""AR data for the ABC pages (A4 + Letter): page PNG at 150 dpi, rig json, kid-colored test still."""
import sys, json, math, os, random, subprocess
sys.path.insert(0, '/home/claude/abc'); sys.path.insert(1, '/home/claude/xmas')
import numpy as np, cv2
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
from shapely import affinity
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm
from engine import fit
from animals import ANIMALS
from letters import WORDS
src = open('/home/claude/xmas/gen_ar.py').read()
for fn in ('def polys', 'def paper_spots', 'def crayon_layer', 'def write_name', 'def perspective'):
    a = src.index(fn); b = src.index('\ndef ', a + 5); exec(src[a:b])
DPI = 150; K = DPI / 72; OUT = '/home/claude/ar/genabc'
for d in ('pages/a4', 'pages/letter', 'ardata', 'stills'): os.makedirs(f'{OUT}/{d}', exist_ok=True)
SIZES = {'a4': A4, 'letter': letter}
MOTION = {k: 'dance' for k in ('alligator', 'bear', 'cat', 'dog', 'elephant', 'hippo', 'koala', 'lion', 'mouse', 'pig', 'rabbit', 'vulture', 'quail')}
NAMES = ['MIA', 'Leo', 'OSKAR', 'Emma', 'NOAH', 'Lily', 'MAX', 'Sofia', 'ADA', 'Hugo', 'EVA', 'Liam', 'ROSE', 'Otto', 'ZOE']
PW, PH = 108 * 11.0, 146 * 11.0

def main(letters):
    for size, (W, H) in SIZES.items():
        m = 15 * mm; top = H - 40 * mm; bottom = 112 * mm; ax0 = m + 72 * mm; aw = W - m - ax0; ah = top - bottom
        sc = min(aw / PW, ah / PH); x0 = ax0 + (aw - PW * sc) / 2; y0 = bottom + (ah - PH * sc) / 2
        bw, bh, gap = 9 * mm, 11 * mm, 1.4 * mm; bx0, by0 = m + 22 * mm, H - 35 * mm
        nb = [[round((bx0 + i * (bw + gap)) * K, 1), round((H - (by0 + bh)) * K, 1), round((bx0 + i * (bw + gap) + bw) * K, 1), round((H - by0) * K, 1)] for i in range(10)]
        art_px = (x0 * K, (H - (y0 + PH * sc)) * K, (x0 + PW * sc) * K, (H - y0) * K)
        for ch in letters:
            key = WORDS[ch][0]; bundle = 'A-M' if ch <= 'M' else 'N-Z'; idx = (ord(ch) - (65 if ch <= 'M' else 78))
            pdf = f'/home/claude/abc/out/MaryMariiArt_ABC_Dot_to_Dot_{bundle}_{"A4" if size == "a4" else "Letter"}.pdf'
            png = f'{OUT}/pages/{size}/abc-{ch.lower()}.png'
            subprocess.run(['pdftoppm', '-r', str(DPI), '-png', '-singlefile', '-f', str(idx + 3), '-l', str(idx + 3), pdf, png[:-4]], check=True)
            blank = cv2.imread(png, 0); th, tw = blank.shape
            char = ANIMALS[key](); parts = char['parts']
            allg = unary_union([p.geom for p in parts])
            s, tx, ty = fit(allg.bounds, (10, 10, PW - 10, PH - 250), pad=70)
            def conv(g):
                g = affinity.translate(affinity.scale(g, s, s, origin=(0, 0)), tx, ty)          # panel units, y down
                g = affinity.scale(g, sc * K, sc * K, origin=(0, 0))                               # -> px scale
                return affinity.translate(g, x0 * K, (H - (y0 + PH * sc)) * K)                      # -> page px (y down)
            body = conv(allg.buffer(0))
            sil = body if body.geom_type == 'Polygon' else max(body.geoms, key=lambda g: g.area)
            sil = Polygon(sil.exterior)
            minx, miny, maxx, maxy = sil.bounds
            region = [round(minx - 12, 1), round(miny - 12, 1), round(maxx + 12, 1), round(maxy + 12, 1)]
            data = {'key': f'abc-{ch.lower()}', 'size': size, 'target': {'width': tw, 'height': th}, 'region': region,
                    'silhouette': polys(sil.buffer(10), 1.0), 'nameBoxes': nb,
                    'paper': [list(p) for p in paper_spots(blank, sil, region, art_px)],
                    'base': [round((minx + maxx) / 2, 1), round(maxy, 1)], 'top': [round((minx + maxx) / 2, 1), round(miny, 1)],
                    'motion': MOTION.get(key, 'bounce'), 'bodyPivot': None, 'body': polys(sil), 'parts': [], 'eyes': [], 'lid': [], 'smoke': None}
            json.dump(data, open(f'{OUT}/ardata/abc-{ch.lower()}_{size}.json', 'w'))
            rnd = random.Random(f'{ch}-{size}')
            pg = cv2.imread(png)
            layer = crayon_layer(pg.shape[:2], [conv(p.geom) for p in parts], rnd)
            kid = (pg.astype(np.float32) / 255 * layer.astype(np.float32)).astype(np.uint8)
            kid = write_name(kid, nb, NAMES[ord(ch) % len(NAMES)], rnd)
            cv2.imwrite(f'{OUT}/stills/abc-{ch.lower()}_{size}.jpg', perspective(kid, f'{ch}{size}'), [cv2.IMWRITE_JPEG_QUALITY, 92])
            print(size, ch, key, data['motion'], 'region', region, flush=True)

if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'ABCDEFGHIJKLMNOPQRSTUVWXYZ')
