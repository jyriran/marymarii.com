import sys
sys.path.insert(0, '.')
from engine import *
from engine import _lines
from chars import CHARS
from chars2 import CHARS2
CHARS.update(CHARS2)

def hero(name, out):
    ch = CHARS[name]()
    parts, details = ch['parts'], ch['details']
    sil_local = unary_union([p.geom for p in parts if p.sil])
    if sil_local.geom_type != 'Polygon':
        sil_local = max(sil_local.geoms, key=lambda g: g.area)
    sil_local = Polygon(sil_local.exterior)
    allg = unary_union([p.geom for p in parts])
    region = (0, 0, 1000, 1100)
    s, tx, ty = fit(allg.bounds, region, pad=70)
    sw = 7 / s
    sil = affinity.translate(affinity.scale(sil_local, s, s, origin=(0, 0)), tx, ty)
    pts = sample_outline(sil.exterior, ch['dots'])
    sx, sy = ch['start']
    pts = order_points(pts, (sx * s + tx, sy * s + ty))
    R, fs = 15, 30
    labels = place_labels(pts, sil, fs, R, [])
    g = f'translate({tx:.2f},{ty:.2f}) scale({s:.5f})'
    d = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts) + ' Z'
    svg = [f'<svg class="hero-sheet" viewBox="0 0 1000 1100" role="img" aria-labelledby="hero-art-title"><title id="hero-art-title">A penguin dot-to-dot that connects its own dots, colors itself in and starts to dance</title>',
           f'<g class="h-lines" transform="{g}">{render_puzzle(parts, details, sw, sil_local)}</g>',
           f'<path class="h-trace" d="{d}" pathLength="1000"/>',
           f'<g class="h-color" transform="{g}">{render_colored(parts, details, sw)}</g>',
           '<g class="h-dots">']
    for x, y in pts:
        svg.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{R}"/>')
    for t, cx, cy, _ in labels:
        svg.append(f'<text x="{cx:.1f}" y="{cy + fs * 0.36:.1f}">{t}</text>')
    svg.append('</g></svg>')
    open(out, 'w').write('\n'.join(svg))
    print(len(pts), 'dots', s)

hero('penguin', '/home/claude/site/hero_penguin.svg')
