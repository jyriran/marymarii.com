import sys, subprocess
sys.path.insert(0, '.')
from animals123 import ANIMALS123
from engine import render_colored, unary_union
from PIL import Image
keys = sys.argv[1:] or list(ANIMALS123)
ims = []
for k in keys:
    try:
        ch = ANIMALS123[k](); g = unary_union([p.geom for p in ch['parts']]); x0, y0, x1, y1 = g.bounds; sd = max(x1 - x0, y1 - y0) + 80
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{cx - sd / 2} {cy - sd / 2} {sd} {sd}" width="300" height="300"><rect x="{cx - sd / 2}" y="{cy - sd / 2}" width="{sd}" height="{sd}" fill="white"/>{render_colored(ch["parts"], ch["details"], 10)}</svg>'
        open(f'/tmp/pv_{k}.svg', 'w').write(svg); subprocess.run(['rsvg-convert', f'/tmp/pv_{k}.svg', '-o', f'/tmp/pv_{k}.png'], check=True)
        ims.append(Image.open(f'/tmp/pv_{k}.png').convert('RGB'))
    except Exception as e:
        print('FAIL', k, e); ims.append(Image.new('RGB', (300, 300), 'red'))
S = Image.new('RGB', (300 * 5, 300 * ((len(ims) + 4) // 5)), 'white')
for i, im in enumerate(ims): S.paste(im, ((i % 5) * 300, (i // 5) * 300))
S.save('/tmp/animals123.jpg', quality=80)
