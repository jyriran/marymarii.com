import sys, subprocess
sys.path.insert(0, '/home/claude/xmas')
from animals import ANIMALS
from engine import render_colored, unary_union, INK
from PIL import Image
keys = sys.argv[1:]
ims = []
for k in keys:
    ch = ANIMALS[k]()
    g = unary_union([p.geom for p in ch['parts']]); x0, y0, x1, y1 = g.bounds
    pad = 40; w = x1 - x0 + 2 * pad; h = y1 - y0 + 2 * pad
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0-pad} {y0-pad} {w} {h}" width="500" height="{500*h/w:.0f}"><rect x="{x0-pad}" y="{y0-pad}" width="{w}" height="{h}" fill="white"/>{render_colored(ch["parts"], ch["details"], 9)}</svg>'
    open(f'/tmp/c_{k}.svg', 'w').write(svg)
    subprocess.run(['rsvg-convert', '-h', '500', f'/tmp/c_{k}.svg', '-o', f'/tmp/c_{k}.png'], check=True)
    ims.append(Image.open(f'/tmp/c_{k}.png'))
W = sum(i.width for i in ims); S = Image.new('RGB', (W, 500), 'white'); x = 0
for i in ims: S.paste(i, (x, 0)); x += i.width
S.save('/tmp/contact.png')
