"""Print-style digit skeletons in stroke order. Units: baseline y=0, top y=1, y up.
Each digit = (width, [stroke, ...]); a stroke is a list of (x, y) points in writing direction."""
import math
def L(*pts): return list(pts)
def arc(cx, cy, rx, ry, a0, a1, n=None):
    n = n or max(8, int(abs(a1 - a0) / 6))
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]
def cat(*parts):
    out = []
    for p in parts:
        if out and math.dist(out[-1], p[0]) < 1e-6: p = p[1:]
        out += p
    return out

DIGITS = {
    '0': (.62, [arc(.31, .5, .31, .5, 90, 450)]),
    '1': (.42, [L((.04, .78), (.34, 1), (.34, 0))]),
    '2': (.64, [cat(arc(.32, .7, .3, .3, 155, -35), L((.07, 0), (.64, 0)))]),
    '3': (.6, [cat(arc(.29, .75, .26, .25, 155, -90), arc(.29, .26, .31, .26, 90, -155))]),
    '4': (.64, [L((.47, 1), (0, .3), (.64, .3)), L((.47, .72), (.47, 0))]),
    '5': (.62, [cat(L((.1, 1), (.07, .55)), arc(.3, .3, .31, .29, 140, -155)), L((.1, 1), (.58, 1))]),
    '6': (.6, [cat([(.5, 1), (.31, .9), (.14, .68), (.04, .4)], arc(.3, .27, .28, .27, 195, 555))]),
    '7': (.6, [L((0, 1), (.6, 1), (.18, 0))]),
    '8': (.6, [cat(arc(.3, .76, .25, .24, 90, 270), arc(.3, .26, .3, .26, 90, -270), arc(.3, .76, .25, .24, -90, 90))]),
    '9': (.58, [cat(arc(.29, .71, .29, .29, 30, 360), L((.58, .71), (.52, 0)))]),
}
WORD = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve', 'thirteen',
        'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen', 'twenty']
def number(n, gap=.14):
    """width and strokes for a whole number (digits side by side)."""
    x = 0; strokes = []
    for i, d in enumerate(str(n)):
        w, S = DIGITS[d]
        strokes += [[(x + px, py) for px, py in s] for s in S]
        x += w + (gap if i < len(str(n)) - 1 else 0)
    return x, strokes
