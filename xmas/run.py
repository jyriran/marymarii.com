import sys, subprocess
from chars import CHARS
from chars2 import CHARS2
CHARS.update(CHARS2)
from engine import build_sheet
names = sys.argv[1:] or list(CHARS)
for n in names:
    c = CHARS[n]()
    cnt, bad = build_sheet(c, f'new/{n}.svg')
    subprocess.run(['rsvg-convert', '-w', '900', f'new/{n}.svg', '-o', f'new/{n}_pv.png'], check=True)
    print(n, 'dots', cnt, 'label conflicts', bad)
