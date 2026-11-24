"""123 Count & Connect – numbers 1–20. Same page system as the ABC bundles."""
import sys, os, math, random, subprocess, inspect, importlib.util
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, '/home/claude/xmas'); sys.path.insert(0, '/home/claude/abc'); sys.path.insert(0, HERE)
_spec = importlib.util.spec_from_file_location('abcb', '/home/claude/abc/build.py'); AB = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(AB)
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas
from digits import number, WORD
INK, GHOST, GUIDE, TRACE = AB.INK, AB.GHOST, AB.GUIDE, AB.TRACE
tf, resample, path_of, badges, footer, name_boxes, qr_strip, guide_lines = AB.tf, AB.resample, AB.path_of, AB.badges, AB.footer, AB.name_boxes, AB.qr_strip, AB.guide_lines
# border with little numbers instead of letters
exec(inspect.getsource(AB.deco_border).replace("'ABCDEFGHIJKLMNOPQRSTUVWXYZ'", "'0123456789'").replace('def deco_border', 'def deco_border123'), AB.__dict__)
deco_border = AB.deco_border123

# number -> (animal key, Animal name, counting object, plural)
PAGES = {1: ('dino', 'Dinosaur', 'egg', 'eggs'), 2: ('duck', 'Duck', 'fish', 'fish'), 3: ('crab', 'Crab', 'shell', 'shells'),
         4: ('ladybug', 'Ladybug', 'leaf', 'leaves'), 5: ('bee', 'Bee', 'flower', 'flowers'), 6: ('snail', 'Snail', 'drop', 'raindrops'),
         7: ('frog', 'Frog', 'fly', 'flies'), 8: ('panda', 'Panda', 'bamboo', 'bamboo sticks'), 9: ('monkey', 'Monkey', 'banana', 'bananas'),
         10: ('cow', 'Cow', 'flower', 'flowers'), 11: ('sheep', 'Sheep', 'cloud', 'clouds'), 12: ('chick', 'Chick', 'seed', 'seeds'),
         13: ('butterfly', 'Butterfly', 'flower', 'flowers'), 14: ('dolphin', 'Dolphin', 'fish', 'fish'), 15: ('seal', 'Seal', 'ball', 'balls'),
         16: ('flamingo', 'Flamingo', 'shell', 'shells'), 17: ('squirrel', 'Squirrel', 'acorn', 'acorns'), 18: ('parrot', 'Parrot', 'berry', 'berries'),
         19: ('tiger', 'Tiger', 'star', 'stars'), 20: ('dragon', 'Dragon', 'star', 'stars')}


def big_number(c, n, x0, y0, h, crayon=None):
    w, strokes = number(n)
    S = tf(strokes, x0, y0, h)
    c.setStrokeColor(GHOST); c.setLineWidth(h * .16); c.setLineCap(1); c.setLineJoin(1)
    for s in S: c.drawPath(path_of(c, s), fill=0, stroke=1)
    c.setFillColor(INK)
    for s in S:
        for p in resample(s, 5.2 * mm): c.circle(*p, 1.25 * mm, fill=1, stroke=0)
    badges(c, S, (x0 + w * h / 2, y0 + h / 2), 3.1 * mm, 6.2 * mm)
    if crayon:
        rr = random.Random(n); c.saveState(); c.setStrokeColor(HexColor(crayon)); c.setStrokeAlpha(.85); c.setLineWidth(2.6 * mm); c.setLineCap(1); c.setLineJoin(1)
        for s in S: c.drawPath(path_of(c, [(x + rr.uniform(-.5, .5) * mm, y + rr.uniform(-.5, .5) * mm) for x, y in resample(s, 3 * mm)]), fill=0, stroke=1)
        c.restoreState()
    return w * h


def trace_word(c, word, x, y, size, crayon=None):
    """the number word in outlined, dotted letters to trace."""
    t = c.beginText(); t.setTextOrigin(x, y); t.setFont('B', size); t.setTextRenderMode(1)
    c.saveState(); c.setStrokeColor(TRACE); c.setLineWidth(.9); c.setDash(1.2, 1.6); t.textOut(word); c.drawText(t); c.restoreState()
    if crayon:
        c.saveState(); c.setFillColor(HexColor(crayon)); c.setFillAlpha(.8); c.setFont('B', size); c.drawString(x, y, word); c.restoreState()


def practice_numbers(c, n, x0, x1, base, h, crayon=None):
    guide_lines(c, x0, x1, base, h)
    w, strokes = number(n); lw = w * h; gap = 8 * mm
    x = x0 + 9 * mm
    c.setStrokeColor(INK); c.setLineWidth(1.6); c.setLineCap(1); c.setLineJoin(1)
    for s in tf(strokes, x, base, h): c.drawPath(path_of(c, s), fill=0, stroke=1)
    x += lw + gap + 2 * mm; k = 0
    while x + lw < x1 - 2 * mm and k < 6:
        c.setFillColor(TRACE)
        for s in tf(strokes, x, base, h):
            for p in resample(s, 1.9 * mm): c.circle(*p, .42 * mm, fill=1, stroke=0)
        if crayon and k < 3:
            c.saveState(); c.setStrokeColor(HexColor(crayon)); c.setLineWidth(1.3); c.setLineCap(1); c.setLineJoin(1)
            for s in tf(strokes, x, base, h): c.drawPath(path_of(c, s), fill=0, stroke=1)
            c.restoreState()
        x += lw + gap; k += 1


# ---------------- little things to count (simple outlines kids can color) ----------------
def icon(c, kind, x, y, r, fill=None):
    c.saveState(); c.setStrokeColor(INK); c.setLineWidth(max(.8, r * .09)); c.setLineJoin(1); c.setLineCap(1)
    c.setFillColor(HexColor(fill) if fill else white); F = 1
    p = c.beginPath()
    if kind == 'egg':
        c.ellipse(x - r * .72, y - r * .95, x + r * .72, y + r * .95, fill=F, stroke=1)
        c.setDash(r * .18, r * .14); c.line(x - r * .6, y, x - r * .2, y + r * .25); c.line(x - r * .2, y + r * .25, x + r * .2, y); c.line(x + r * .2, y, x + r * .6, y + r * .25)
    elif kind == 'fish':
        p.moveTo(x - r * .9, y); p.curveTo(x - r * .4, y + r * .75, x + r * .45, y + r * .65, x + r * .75, y); p.curveTo(x + r * .45, y - r * .65, x - r * .4, y - r * .75, x - r * .9, y); p.close()
        c.drawPath(p, fill=F, stroke=1)
        q = c.beginPath(); q.moveTo(x + r * .7, y); q.lineTo(x + r * 1.1, y + r * .45); q.lineTo(x + r * 1.1, y - r * .45); q.close(); c.drawPath(q, fill=F, stroke=1)
        c.setFillColor(INK); c.circle(x - r * .45, y + r * .12, r * .1, fill=1, stroke=0)
    elif kind == 'shell':
        p.moveTo(x - r * .9, y - r * .6); p.curveTo(x - r * 1.0, y + r * .7, x + r * 1.0, y + r * .7, x + r * .9, y - r * .6); p.close(); c.drawPath(p, fill=F, stroke=1)
        for a in (-.5, -.2, .2, .5): c.line(x, y - r * .6, x + a * r * 1.6, y + r * .35)
    elif kind == 'leaf':
        p.moveTo(x - r, y - r * .2); p.curveTo(x - r * .3, y + r * .9, x + r * .6, y + r * .6, x + r, y + r * .2); p.curveTo(x + r * .3, y - r * .8, x - r * .6, y - r * .7, x - r, y - r * .2); p.close()
        c.drawPath(p, fill=F, stroke=1); c.line(x - r * .9, y - r * .15, x + r * .9, y + r * .18)
    elif kind == 'flower':
        for i in range(5):
            a = math.radians(90 + i * 72); c.circle(x + math.cos(a) * r * .55, y + math.sin(a) * r * .55, r * .42, fill=F, stroke=1)
        c.circle(x, y, r * .32, fill=F, stroke=1)
    elif kind == 'drop':
        p.moveTo(x, y + r); p.curveTo(x + r * .2, y + r * .4, x + r * .75, y - r * .1, x + r * .7, y - r * .45)
        p.curveTo(x + r * .65, y - r * 1.05, x - r * .65, y - r * 1.05, x - r * .7, y - r * .45); p.curveTo(x - r * .75, y - r * .1, x - r * .2, y + r * .4, x, y + r); p.close()
        c.drawPath(p, fill=F, stroke=1)
    elif kind == 'fly':
        c.ellipse(x - r * .9, y + r * .05, x - r * .05, y + r * .65, fill=F, stroke=1); c.ellipse(x + r * .05, y + r * .05, x + r * .9, y + r * .65, fill=F, stroke=1)
        c.ellipse(x - r * .35, y - r * .75, x + r * .35, y + r * .35, fill=F, stroke=1)
        c.setFillColor(INK); c.circle(x - r * .12, y + r * .12, r * .07, fill=1, stroke=0); c.circle(x + r * .12, y + r * .12, r * .07, fill=1, stroke=0)
    elif kind == 'bamboo':
        c.roundRect(x - r * .25, y - r, r * .5, r * 2, r * .15, fill=F, stroke=1); c.line(x - r * .25, y - r * .25, x + r * .25, y - r * .25); c.line(x - r * .25, y + r * .45, x + r * .25, y + r * .45)
        q = c.beginPath(); q.moveTo(x + r * .25, y + r * .5); q.curveTo(x + r * .7, y + r * .7, x + r * .9, y + r, x + r * .6, y + r * 1.05); q.curveTo(x + r * .5, y + r * .8, x + r * .35, y + r * .7, x + r * .25, y + r * .5); c.drawPath(q, fill=F, stroke=1)
    elif kind == 'banana':
        p.moveTo(x - r * .9, y + r * .5); p.curveTo(x - r * .6, y - r * .9, x + r * .7, y - r * .9, x + r * .95, y + r * .1)
        p.curveTo(x + r * .5, y - r * .3, x - r * .4, y - r * .4, x - r * .9, y + r * .5); p.close(); c.drawPath(p, fill=F, stroke=1)
        c.line(x - r * .9, y + r * .5, x - r * 1.0, y + r * .7)
    elif kind == 'cloud':
        for dx, dy, rr in ((-.5, -.1, .42), (0, .2, .55), (.5, -.1, .42)): c.circle(x + dx * r, y + dy * r, rr * r, fill=F, stroke=1)
        c.setStrokeColor(white if not fill else HexColor(fill)); c.setFillColor(white if not fill else HexColor(fill)); c.rect(x - r * .62, y - r * .5, r * 1.24, r * .4, fill=1, stroke=0)
        c.setStrokeColor(INK); c.line(x - r * .92, y - r * .5, x + r * .92, y - r * .5)
    elif kind == 'seed':
        c.ellipse(x - r * .45, y - r * .7, x + r * .45, y + r * .7, fill=F, stroke=1); c.line(x, y - r * .5, x, y + r * .5)
    elif kind == 'ball':
        c.circle(x, y, r * .85, fill=F, stroke=1); c.line(x - r * .85, y, x + r * .85, y)
        q = c.beginPath(); q.arc(x - r * .4, y - r * .85, x + r * .4, y + r * .85, -90, 180); c.drawPath(q, fill=0, stroke=1)
    elif kind == 'acorn':
        c.ellipse(x - r * .55, y - r * .95, x + r * .55, y + r * .35, fill=F, stroke=1)
        q = c.beginPath(); q.moveTo(x - r * .72, y + r * .1); q.curveTo(x - r * .7, y + r * .8, x + r * .7, y + r * .8, x + r * .72, y + r * .1); q.close(); c.drawPath(q, fill=F, stroke=1)
        c.line(x, y + r * .65, x + r * .15, y + r * .95)
    elif kind == 'berry':
        for dx, dy in ((-.35, -.3), (.35, -.3), (0, .25)): c.circle(x + dx * r, y + dy * r, r * .42, fill=F, stroke=1)
        c.line(x, y + r * .65, x + r * .1, y + r * 1.0)
    elif kind == 'star':
        for i in range(10):
            rr = r * (1 if i % 2 == 0 else .45); a = math.radians(90 + i * 36)
            (p.moveTo if i == 0 else p.lineTo)(x + rr * math.cos(a), y + rr * math.sin(a))
        p.close(); c.drawPath(p, fill=F, stroke=1)
    c.restoreState()


def ten_frames(c, n, x, y, cell, filled=0, fillcol=None):
    """one ten-frame (2 x 5) for 1–10, two for 11–20. Returns width."""
    frames = 1 if n <= 10 else 2
    for f in range(frames):
        fy = y; fx = x + f * (5 * cell + 3 * mm)   # side by side
        for r_ in range(2):
            for k in range(5):
                i = f * 10 + r_ * 5 + k
                cx, cy = fx + k * cell, fy - (r_ + 1) * cell
                c.setStrokeColor(INK); c.setLineWidth(1.1)
                c.setFillColor(HexColor(fillcol) if (fillcol and i < filled) else white)
                c.rect(cx, cy, cell, cell, fill=1, stroke=1)
    return 5 * cell


def count_box(c, W, n, kind, plural, x0, x1, y0, y1, done=None):
    c.setStrokeColor(INK); c.setLineWidth(.8); c.roundRect(x0, y0, x1 - x0, y1 - y0, 4 * mm, fill=0, stroke=1)
    c.setFillColor(INK); c.setFont('B', 12); c.drawString(x0 + 5 * mm, y1 - 7.5 * mm, f'Count the {plural}. How many?')
    # objects on the left, scattered in a loose grid so counting is easy
    gx0, gx1, gy0, gy1 = x0 + 5 * mm, x0 + (x1 - x0) * .56, y0 + 4 * mm, y1 - 11 * mm
    cols = 10 if n > 10 else (5 if n > 5 else max(3, n))
    rows = -(-n // cols)
    cw = (gx1 - gx0) / cols; rh = (gy1 - gy0) / max(rows, 2)
    r = min(cw * (.34 if n > 10 else .42), rh * .44, 6 * mm)
    rnd = random.Random(n * 7)
    k = 0
    fills = ['#F4B942', '#7FB7E0', '#E0503A', '#86C46A', '#C9A7E3']
    for row in range(rows):
        for col in range(cols):
            if k >= n: break
            ix = gx0 + (col + .5) * cw + rnd.uniform(-.12, .12) * cw
            iy = gy1 - (row + .5) * rh + rnd.uniform(-.08, .08) * rh
            icon(c, kind, ix, iy, r, fills[k % len(fills)] if done else None); k += 1
    # answer box
    ax = x0 + (x1 - x0) * .6; c.setFillColor(INK); c.setFont('B', 11); c.drawString(ax, y1 - 7.5 * mm, 'Write it:')
    c.setLineWidth(1.1); c.roundRect(ax + 20 * mm, y1 - 10.5 * mm, 16 * mm, 9 * mm, 1.5 * mm, fill=0, stroke=1)
    if done:
        c.saveState(); c.setFillColor(HexColor('#2B4C9B')); c.setFont('B', 17); c.drawCentredString(ax + 28 * mm, y1 - 9 * mm, str(n)); c.restoreState()
    c.setFillColor(INK); c.setFont('R', 10); c.drawString(ax, y1 - 15.5 * mm, f'Color {n} box{"es" if n > 1 else ""}:')
    cell = min(7.5 * mm, ((x1 - 5 * mm) - ax) / 5) if n <= 10 else min(6.4 * mm, ((x1 - 5 * mm) - ax - 3 * mm) / 10)
    ten_frames(c, n, ax, y1 - 19 * mm, cell, n if done else 0, '#F4B942' if done else None)


BORDER_SEED = {}


def sheet(c, W, H, n, idx, total, dots, done=None):
    key, animal, kind, plural = PAGES[n]
    m = 15 * mm
    deco_border(c, W, H, BORDER_SEED.get(n, f'123-{n}'))
    c.setFillColor(INK); c.setFont('B', 24); c.drawString(m, H - 21 * mm, f'{n} · {WORD[n]}')
    c.setFont('R', 12); c.drawRightString(W - m, H - 21 * mm, f'{animal} · Dots 1–{dots}')
    boxes = name_boxes(c, W, H, m)
    top = H - 40 * mm; bottom = 122 * mm
    cr = done and done.get('crayon')
    # big number, centred in the left column
    nh = 70 * mm if n < 10 else 52 * mm
    nw = number(n)[0] * nh
    big_number(c, n, m + 4 * mm + (64 * mm - nw) / 2, top - nh - 10 * mm, nh, cr)
    # number word to trace
    fs = 30 if len(WORD[n]) <= 6 else (24 if len(WORD[n]) <= 8 else 19)
    c.setFillColor(INK); c.setFont('R', 9.5); c.drawString(m + 4 * mm, bottom + 17 * mm, 'Trace the word:')
    trace_word(c, WORD[n], m + 4 * mm, bottom + 4 * mm, fs, cr)
    # animal dot-to-dot
    ax0 = m + 72 * mm; aw = W - m - ax0; ah = top - bottom
    c.drawImage(f'out/{key}{"_done" if done else ""}.png', ax0, bottom, aw, ah, preserveAspectRatio=True, anchor='c')
    # practice row + counting box
    c.setFillColor(INK); c.setFont('B', 11); c.drawString(m, 115 * mm, 'Trace the numbers, then write your own:')
    practice_numbers(c, n, m, W - m, 99 * mm, 12 * mm, cr)
    count_box(c, W, n, kind, plural, m, W - m, 55.5 * mm, 94 * mm, done)
    if done and done.get('name'):
        c.saveState(); c.setFillColor(HexColor('#2B4C9B'))
        for i, L_ in enumerate(done['name']):
            bx, by, bw_, bh_ = boxes[i]; c.saveState(); c.translate(bx + bw_ / 2, by + 2.2 * mm); c.rotate((-1) ** i * 3)
            c.setFont('B', 19); c.drawCentredString(0, 0, L_); c.restoreState()
        c.restoreState()
    url = f'https://marymarii.com/scan/?s=n{n}' + ('&size=letter' if abs(W - 612) < 1 else '')
    qr_strip(c, W, m, url, f'Finished? Watch {WORD[n]} come alive!', 'Ask a grown-up to scan the QR code with a phone camera,',
             'then point the phone at this page. No app needed.')
    footer(c, W, f'Page {idx} of {total}')


def panel(n, done=False):
    from animals123 import ANIMALS123
    key = PAGES[n][0]
    AB.animal_panel(ANIMALS123[key](), f'out/{key}{"_done" if done else ""}.svg', done=done)
    subprocess.run(['rsvg-convert', '-w', '1400', f'out/{key}{"_done" if done else ""}.svg', '-o', f'out/{key}{"_done" if done else ""}.png'], check=True)


def color_pngs():
    from animals123 import ANIMALS123
    from engine import render_colored, unary_union
    for n, (k, *_r) in PAGES.items():
        ch = ANIMALS123[k](); g = unary_union([p.geom for p in ch['parts']]); x0, y0, x1, y1 = g.bounds
        side = max(x1 - x0, y1 - y0) + 120; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{cx - side / 2} {cy - side / 2} {side} {side}" width="800" height="800">'
               f'<rect x="{cx - side / 2}" y="{cy - side / 2}" width="{side}" height="{side}" fill="white"/>{render_colored(ch["parts"], ch["details"], 10)}</svg>')
        open(f'out/col_{k}.svg', 'w').write(svg); subprocess.run(['rsvg-convert', f'out/col_{k}.svg', '-o', f'out/col_{k}.png'], check=True)


def grid(c, W, H, top, bottom, label, img_only=False):
    cols, rows, g = 4, 5, 3.5 * mm
    size = min((W - 30 * mm - (cols - 1) * g) / cols, (top - bottom - (rows - 1) * g) / rows)
    x0 = (W - cols * size - (cols - 1) * g) / 2
    for i, n in enumerate(range(1, 21)):
        col, row = i % cols, i // cols
        x = x0 + col * (size + g); y = top - (row + 1) * size - row * g
        im = size - 10 * mm
        c.drawImage(f'out/col_{PAGES[n][0]}.png', x + (size - im) / 2, y + 7 * mm, im, im)
        c.setStrokeColor(INK if not img_only else HexColor('#999999')); c.setLineWidth(.6); c.roundRect(x, y, size, size, 2.5 * mm, fill=0, stroke=1)
        c.setFillColor(INK); c.setFont('B', 10.5); c.drawCentredString(x + size / 2, y + 2.5 * mm, label(n))


def cover(c, W, H):
    c.setFillColor(INK); c.setFont('B', 32); c.drawCentredString(W / 2, H - 28 * mm, '123 Count & Connect · 1 to 20')
    c.setFont('R', 13)
    c.drawCentredString(W / 2, H - 38 * mm, 'Trace each number, count and color, connect the dots,')
    c.drawCentredString(W / 2, H - 44.5 * mm, 'then scan the QR code and watch the animal count along!')
    c.setStrokeColor(INK); c.setLineWidth(1.2); c.line(W / 2 - 40 * mm, H - 51 * mm, W / 2 + 40 * mm, H - 51 * mm)
    grid(c, W, H, H - 57 * mm, 30 * mm, lambda n: f'{n} · {PAGES[n][1]}')
    c.setFillColor(INK); c.setFont('B', 12); c.drawCentredString(W / 2, 21 * mm, '20 activity pages · Ages 3–6 · numbers, counting and coloring')
    footer(c, W, '')


def how(c, W, H):
    from reportlab.lib.utils import simpleSplit
    c.setFillColor(INK); c.setFont('B', 24); c.drawString(20 * mm, H - 30 * mm, 'How each page works')
    steps = [('1', 'Write your name', 'One letter in each box, so everyone knows whose page it is.'),
             ('2', 'Trace the big number', 'Start at the circle with number 1 and follow the arrow, joining the dots. Then trace the number word.'),
             ('3', 'Practice', 'Trace the dotted numbers on the line, then write a few on your own.'),
             ('4', 'Count and color', 'Count the little pictures, write how many in the box, then color that many boxes in the ten-frame.'),
             ('5', 'Connect the dots and color', 'Join the animal\'s dots from 1 to the end, then color it in. The little picture shows one way to color it.'),
             ('6', 'Scan and watch', 'A grown-up scans the QR code with a phone camera, then points the phone at the page. The animal comes alive in your colors and counts with you. No app needed.')]
    y = H - 48 * mm
    for n, t, d in steps:
        c.setStrokeColor(INK); c.setLineWidth(1.4); c.setFillColor(white); c.circle(27 * mm, y + 2 * mm, 7 * mm, fill=1, stroke=1)
        c.setFillColor(INK); c.setFont('B', 16); c.drawCentredString(27 * mm, y - .5 * mm, n)
        c.setFont('B', 14); c.drawString(40 * mm, y + 3 * mm, t); c.setFont('R', 10.5)
        for i, line in enumerate(simpleSplit(d, 'R', 10.5, W - 60 * mm)): c.drawString(40 * mm, y - 3 * mm - i * 5 * mm, line)
        y -= 23 * mm
    c.setStrokeColor(INK); c.setLineWidth(.8); c.roundRect(20 * mm, y - 40 * mm, W - 40 * mm, 46 * mm, 4 * mm, fill=0, stroke=1)
    c.setFillColor(INK); c.setFont('B', 13); c.drawString(27 * mm, y - 3 * mm, 'Tips for grown-ups')
    c.setFont('R', 10.5)
    tips = ['Black-and-white printing is perfect. Every page is designed for it.',
            'Print at 100% / "Actual size" so the magic camera recognizes the page.',
            'Little ones can trace the big number with a finger first, then with a crayon.',
            'Print as many copies as you like for your own family.']
    for i, t in enumerate(tips): c.drawString(27 * mm, y - 12 * mm - i * 7 * mm, '•  ' + t)
    footer(c, W, '')


def color_ideas(c, W, H):
    c.setFillColor(INK); c.setFont('B', 22); c.drawString(15 * mm, H - 22 * mm, 'Color ideas')
    c.setFont('R', 10.5); c.drawString(15 * mm, H - 29 * mm, 'Optional page: print it in color or look at it on a screen. Any colors are fine!')
    grid(c, W, H, H - 35 * mm, 22 * mm, lambda n: f'{n} · {PAGES[n][1]}', img_only=True)
    footer(c, W, '')


def bundle():
    from animals123 import ANIMALS123
    color_pngs()
    for n in PAGES: panel(n)
    name = 'MaryMariiArt_123_Count_and_Connect_1-20'
    for size, sz in ((A4, 'A4'), (letter, 'Letter')):
        c = canvas.Canvas(f'out/{name}_{sz}.pdf', pagesize=size)
        c.setTitle('123 Count & Connect 1 to 20 – MaryMariiArt'); c.setAuthor('MaryMariiArt')
        cover(c, *size); c.showPage(); how(c, *size); c.showPage()
        for n in range(1, 21): sheet(c, *size, n, n, 20, ANIMALS123[PAGES[n][0]]()['dots']); c.showPage()
        color_ideas(c, *size); c.showPage(); c.save()
    return name


if __name__ == '__main__' and sys.argv[1:2] == ['bundle']:
    os.chdir(HERE); print(bundle()); sys.exit()

if __name__ == '__main__':
    os.chdir(HERE)
    nums = [int(a) for a in sys.argv[1:]] or [7]
    from animals123 import ANIMALS123
    for n in nums:
        panel(n); panel(n, True)
        for d, tag in ((None, 'bw'), (dict(name='MAX', crayon='#3D7BD8'), 'color')):
            c = canvas.Canvas(f'out/sample_{n}_{tag}.pdf', pagesize=A4)
            sheet(c, *A4, n, n, 20, ANIMALS123[PAGES[n][0]]()['dots'], d); c.showPage(); c.save()
            subprocess.run(['pdftoppm', '-r', '110', '-png', '-singlefile', f'out/sample_{n}_{tag}.pdf', f'out/sample_{n}_{tag}'], check=True)
