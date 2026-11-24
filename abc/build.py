import sys, math, random, subprocess
sys.path.insert(0, '/home/claude/xmas')
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from letters import UPPER, LOWER, WORDS

pdfmetrics.registerFont(TTFont('B', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('R', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
INK = HexColor('#1E120C'); GHOST = HexColor('#E4E4E4'); GUIDE = HexColor('#9A9A9A'); TRACE = HexColor('#8C8C8C')


def footer(c, W, label):
    c.setFont('R', 7.5); c.setFillColor(HexColor('#444444'))
    c.drawString(15 * mm, 15.5 * mm - 7, '© MaryMariiArt · for personal and family use · marymariiart.etsy.com')
    c.drawRightString(W - 15 * mm, 15.5 * mm - 7, label)


def deco_border(c, W, H, seed):
    """Black stars, hearts, dots and little letters in the margin: a unique pattern per page
    for the magic camera to lock onto, even after the drawing has been colored in."""
    rnd = random.Random(seed)
    inner, outer = 15 * mm, 4.5 * mm
    placed = []
    def free(x, y, r): return all(math.hypot(x - px, y - py) > r + pr + 1.2 * mm for px, py, pr in placed)
    def star_path(p, x, y, r, n, k, rot):
        for i in range(2 * n):
            rr = r if i % 2 == 0 else r * k
            a = rot + math.pi / 2 + i * math.pi / n
            (p.moveTo if i == 0 else p.lineTo)(x + rr * math.cos(a), y + rr * math.sin(a))
        p.close()
    def icon(kind, x, y, r, rot):
        c.saveState(); c.setFillColor(black); c.setStrokeColor(black); p = c.beginPath()
        if kind == 'star': star_path(p, x, y, r, 5, .45, rot); c.drawPath(p, fill=1, stroke=0)
        elif kind == 'spark': star_path(p, x, y, r, 4, .28, rot); c.drawPath(p, fill=1, stroke=0)
        elif kind == 'dot': c.circle(x, y, r * .55, fill=1, stroke=0)
        elif kind == 'ring': c.setLineWidth(r * .3); c.circle(x, y, r * .6, fill=0, stroke=1)
        elif kind == 'heart':
            c.translate(x, y); c.rotate(math.degrees(rot) * .3)
            p.moveTo(0, -r * .8); p.curveTo(r * 1.2, 0, r * .5, r * .9, 0, r * .35)
            p.curveTo(-r * .5, r * .9, -r * 1.2, 0, 0, -r * .8); c.drawPath(p, fill=1, stroke=0)
        elif kind == 'letter':
            c.translate(x, y); c.rotate(math.degrees(rot) * .25)
            ch = rnd.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ'); fs = r * 2.3
            c.setFont('B', fs); c.drawCentredString(0, -fs * .36, ch)
        c.restoreState()
    kinds = ['star', 'spark', 'dot', 'ring', 'heart', 'letter', 'letter', 'letter']
    tries = 0
    while tries < 12000 and len(placed) < 150:
        tries += 1
        r = rnd.uniform(2.6, 5.2) * mm
        side = rnd.random() * (2 * (W + H))
        if side < W: x, y = side, rnd.uniform(H - inner + r, H - outer - r)
        elif side < W + H: x, y = rnd.uniform(W - inner + r, W - outer - r), side - W
        elif side < 2 * W + H: x, y = side - W - H, rnd.uniform(outer + r, inner - r)
        else: x, y = rnd.uniform(outer + r, inner - r), side - 2 * W - H
        if not (outer + r <= x <= W - outer - r and outer + r <= y <= H - outer - r): continue
        if inner - .5 * mm < x < W - inner + .5 * mm and inner - .5 * mm < y < H - inner + .5 * mm: continue
        if not free(x, y, r * 0.8): continue
        placed.append((x, y, r)); icon(rnd.choice(kinds), x, y, r, rnd.uniform(0, 2 * math.pi))


# ---------------- letters ----------------
def resample(pts, step):
    """evenly spaced points along a polyline, keeping both ends."""
    if len(pts) == 1: return list(pts)
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    total = sum(seg); n = max(1, round(total / step)); out = []
    for k in range(n + 1):
        d = total * k / n; i = 0
        while i < len(seg) - 1 and d > seg[i]: d -= seg[i]; i += 1
        t = d / seg[i] if seg[i] else 0
        out.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * t, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * t))
    return out


def tf(strokes, x0, y0, h):
    return [[(x0 + x * h, y0 + y * h) for x, y in s] for s in strokes]


def path_of(c, pts):
    p = c.beginPath(); p.moveTo(*pts[0])
    for q in pts[1:]: p.lineTo(*q)
    return p


def badges(c, strokes, center, r, gap, arrows=True):
    """numbered start badge for each stroke, set off toward the side the stroke heads, plus a direction arrow."""
    used = []
    for i, s in enumerate(strokes, 1):
        sx, sy = s[0]
        if len(s) > 1:
            j = 1
            while math.dist(s[j], s[0]) < r * 1.5 and j < len(s) - 1: j += 1
            dx, dy = s[j][0] - sx, s[j][1] - sy; Ld = math.hypot(dx, dy) or 1; dx, dy = dx / Ld, dy / Ld
        else: dx, dy = 0, -1
        ox, oy = sx - center[0], sy - center[1]; Lo = math.hypot(ox, oy) or 1; ox, oy = ox / Lo, oy / Lo
        vx, vy = ox + dx * .8, oy + dy * .8
        if math.hypot(vx, vy) < .25: vx, vy = -dy, dx
        Lv = math.hypot(vx, vy); vx, vy = vx / Lv, vy / Lv
        bx, by = sx + vx * gap, sy + vy * gap
        for (ux, uy) in used:
            if math.hypot(bx - ux, by - uy) < 2.3 * r: bx, by = bx + vx * 2.4 * r, by + vy * 2.4 * r
        used.append((bx, by))
        c.setFillColor(white); c.setStrokeColor(INK); c.setLineWidth(r * .22); c.circle(bx, by, r, fill=1, stroke=1)
        c.setFillColor(INK); c.setFont('B', r * 1.35); c.drawCentredString(bx, by - r * .48, str(i))
        if arrows and len(s) > 1:
            # arrow beside the start of the stroke, on the badge's side, pointing the way to go
            side = 1 if (-dy) * vx + dx * vy > 0 else -1
            px, py = -dy * side, dx * side
            a0 = (sx + px * r * 1.5 + dx * r * 1.2, sy + py * r * 1.5 + dy * r * 1.2)
            a1 = (a0[0] + dx * r * 3.4, a0[1] + dy * r * 3.4)
            c.setStrokeColor(INK); c.setLineWidth(r * .25); c.setLineCap(1); c.line(*a0, *a1)
            h = r * 1.0
            p = c.beginPath(); p.moveTo(a1[0] + dx * h * .45, a1[1] + dy * h * .45)
            p.lineTo(a1[0] - dx * h * .55 + px * h * .55, a1[1] - dy * h * .55 + py * h * .55)
            p.lineTo(a1[0] - dx * h * .55 - px * h * .55, a1[1] - dy * h * .55 - py * h * .55); p.close()
            c.setFillColor(INK); c.drawPath(p, fill=1, stroke=0)


def big_letter(c, ch, x0, y0, h, upper, crayon=None):
    w, strokes = (UPPER if upper else LOWER)[ch]
    S = tf(strokes, x0, y0, h)
    # soft grey body so the letter shape reads at a glance (prints light on any printer)
    c.setStrokeColor(GHOST); c.setLineWidth(h * .16); c.setLineCap(1); c.setLineJoin(1)
    for s in S:
        if len(s) == 1: c.setFillColor(GHOST); c.circle(*s[0], h * .08, fill=1, stroke=0)
        else: c.drawPath(path_of(c, s), fill=0, stroke=1)
    # dots to join
    c.setFillColor(INK)
    for s in S:
        for p in resample(s, 5.2 * mm):
            c.circle(*p, 1.25 * mm, fill=1, stroke=0)
    cx = x0 + w * h / 2; cy = y0 + (h / 2 if upper else h / 4)
    badges(c, S, (cx, cy), 3.1 * mm, 6.2 * mm if upper else 8.5 * mm)
    if crayon:
        import random as _r; rr = _r.Random(ch)
        c.saveState(); c.setStrokeColor(HexColor(crayon)); c.setStrokeAlpha(.85); c.setLineWidth(2.6 * mm); c.setLineCap(1); c.setLineJoin(1)
        for s_ in S:
            if len(s_) == 1: c.setFillColor(HexColor(crayon)); c.circle(*s_[0], 2 * mm, fill=1, stroke=0); continue
            pts = [(x + rr.uniform(-.5, .5) * mm, y + rr.uniform(-.5, .5) * mm) for x, y in resample(s_, 3 * mm)]
            c.drawPath(path_of(c, pts), fill=0, stroke=1)
        c.restoreState()


def guide_lines(c, x0, x1, base, h):
    c.setLineWidth(.6); c.setStrokeColor(GUIDE)
    c.line(x0, base + h, x1, base + h); c.line(x0, base, x1, base)
    c.setDash(2, 2); c.line(x0, base + h / 2, x1, base + h / 2); c.setDash()


def practice_row(c, ch, upper, x0, x1, base, h, crayon=None):
    guide_lines(c, x0, x1, base, h)
    w, strokes = (UPPER if upper else LOWER)[ch]
    gap = 7 * mm; lw = w * h
    x = x0 + 9 * mm
    # model: solid strokes + small numbered starts
    S = tf(strokes, x, base, h)
    c.setStrokeColor(INK); c.setLineWidth(1.6); c.setLineCap(1); c.setLineJoin(1)
    for s in S:
        if len(s) == 1: c.setFillColor(INK); c.circle(*s[0], 1.0, fill=1, stroke=0)
        else: c.drawPath(path_of(c, s), fill=0, stroke=1)
    x += lw + gap + 2 * mm
    # dotted copies to trace, then empty space
    n = 0
    while x + lw < x1 - 2 * mm and n < 4:
        c.setFillColor(TRACE)
        for s in tf(strokes, x, base, h):
            for p in resample(s, 1.9 * mm): c.circle(*p, .42 * mm, fill=1, stroke=0)
        if crayon and n < 3:
            c.saveState(); c.setStrokeColor(HexColor(crayon)); c.setLineWidth(1.3); c.setLineCap(1); c.setLineJoin(1)
            for s in tf(strokes, x, base, h):
                if len(s) == 1: c.setFillColor(HexColor(crayon)); c.circle(*s[0], .8, fill=1, stroke=0)
                else: c.drawPath(path_of(c, [(px + (k % 3 - 1) * .25, py) for k, (px, py) in enumerate(s)]), fill=0, stroke=1)
            c.restoreState()
        x += lw + gap; n += 1


def name_boxes(c, W, H, m):
    c.setFillColor(INK); c.setFont('B', 11); c.drawString(m, H - 31.5 * mm, 'My name:')
    bw, bh, gap = 9 * mm, 11 * mm, 1.4 * mm
    bx0, by0 = m + 22 * mm, H - 35 * mm
    c.setStrokeColor(INK); c.setLineWidth(.9)
    boxes = []
    for i in range(10):
        bx = bx0 + i * (bw + gap); c.roundRect(bx, by0, bw, bh, 1.2 * mm, fill=0, stroke=1); boxes.append((bx, by0, bw, bh))
    return boxes


def qr_strip(c, W, m, url, title, l1, l2):
    from reportlab.graphics.barcode.qr import QrCodeWidget
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics import renderPDF
    qr_h = 34 * mm; by = 18.5 * mm
    c.setStrokeColor(INK); c.setLineWidth(.8); c.roundRect(m, by, W - 2 * m, qr_h, 4 * mm, fill=0, stroke=1)
    q = qr_h - 8 * mm
    w = QrCodeWidget(url, barLevel='M'); x1, y1, x2, y2 = w.getBounds(); qs = q - 2 * mm
    d = Drawing(qs, qs, transform=[qs / (x2 - x1), 0, 0, qs / (y2 - y1), 0, 0]); d.add(w)
    renderPDF.draw(d, c, m + 5 * mm, by + 5 * mm)
    tx = m + q + 10 * mm
    c.setFillColor(INK); c.setFont('B', 14); c.drawString(tx, by + qr_h - 11 * mm, title)
    c.setFont('R', 10.5); c.drawString(tx, by + qr_h - 18 * mm, l1); c.drawString(tx, by + qr_h - 23.5 * mm, l2)


BORDER_SEED = {'C': 'abc-C-v2', 'U': 'abc-U-v2', 'V': 'abc-V-v2', 'Z': 'abc-Z-v2'}


def sheet(c, W, H, ch, idx, total, dots, done=None):
    key, animal = WORDS[ch]
    m = 15 * mm
    deco_border(c, W, H, BORDER_SEED.get(ch, 'abc-' + ch))
    # title: "A is for Alligator" with the big letter in red-free ink (B&W friendly)
    c.setFillColor(INK); c.setFont('B', 24); c.drawString(m, H - 21 * mm, f'{ch} is for {animal}')
    c.setFont('R', 12); c.drawRightString(W - m, H - 21 * mm, f'Dots 1–{dots}')
    boxes = name_boxes(c, W, H, m)

    # main area
    top = H - 40 * mm; bottom = 112 * mm
    # left: big upper + lower case letter
    uh = 60 * mm; lh = 56 * mm
    uw = UPPER[ch][0] * uh
    lx = m + 6 * mm + (62 * mm - uw) / 2
    cr = done and done.get('crayon')
    big_letter(c, ch, lx, top - uh - 9 * mm, uh, True, cr)
    desc = ch.lower() in 'gjpqy'
    if desc: lh = 42 * mm
    lw_ = LOWER[ch.lower()][0] * lh
    big_letter(c, ch.lower(), m + 6 * mm + (62 * mm - lw_) / 2, bottom + (8 * mm + lh * .32 if desc else 12 * mm), lh, False, cr)
    # right: animal dot-to-dot (square art from the engine)
    ax0 = m + 72 * mm; aw = W - m - ax0; ah = top - bottom
    c.drawImage(f'out/{key}{"_done" if done else ""}.png', ax0, bottom, aw, ah, preserveAspectRatio=True, anchor='c')

    # practice rows
    c.setFillColor(INK); c.setFont('B', 11); c.drawString(m, 104 * mm, 'Trace the dotted letters, then write your own:')
    practice_row(c, ch, True, m, W - m, 84 * mm, 13 * mm, cr)
    practice_row(c, ch.lower(), False, m, W - m, 63 * mm, 13 * mm, cr)
    if done and done.get('name'):
        c.saveState(); c.setFillColor(HexColor('#2B4C9B'))
        for i, L_ in enumerate(done['name']):
            bx, by, bw_, bh_ = boxes[i]; c.saveState(); c.translate(bx + bw_ / 2, by + 2.2 * mm); c.rotate((-1) ** i * 3)
            c.setFont('B', 19); c.drawCentredString(0, 0, L_); c.restoreState()
        c.restoreState()

    url = f'https://marymarii.com/scan/?s=abc-{ch.lower()}' + ('&size=letter' if abs(W - 612) < 1 else '')
    qr_strip(c, W, m, url, f'Finished? Make {ch} come alive!', 'Ask a grown-up to scan the QR code with a phone camera,',
             'then point the phone at this page. No app needed.')
    footer(c, W, f'Page {idx} of {total}')
    return boxes


def animal_panel(char, path_svg, wmm=108, hmm=146, done=False):
    """dot-to-dot panel sized for the right column: big puzzle, small colored picture in the lower-left corner."""
    from engine import (unary_union, Polygon, affinity, box, fit, sample_outline, order_points, place_labels,
                        render_colored, render_puzzle, INK as EINK)
    k = 11.0; PW, PH = wmm * k, hmm * k
    parts, details = char['parts'], char['details']
    sil_local = char.get('dotsil') or unary_union([p.geom for p in parts if p.sil])
    if sil_local.geom_type != 'Polygon': sil_local = max(sil_local.geoms, key=lambda g: g.area)
    sil_local = Polygon(sil_local.exterior)
    allg = unary_union([p.geom for p in parts])
    ref_region = (10, PH - 280, 300, PH - 10)
    pz_region = (10, 10, PW - 10, PH - 250)
    s, tx, ty = fit(allg.bounds, pz_region, pad=70)
    # keep the puzzle clear of the reference picture: shift right/up if the corner is crowded
    rs, rtx, rty = fit(allg.bounds, ref_region, pad=10)
    sw_p = 1.0 * k / s; sw_r = .7 * k / rs
    sil = affinity.translate(affinity.scale(sil_local, s, s, origin=(0, 0)), tx, ty)
    pts = sample_outline(sil.exterior, char['dots'])
    sx, sy = char['start']; pts = order_points(pts, (sx * s + tx, sy * s + ty))
    R, fs = 1.25 * k, 3.6 * k
    labels = place_labels(pts, sil, fs, R, [box(*ref_region)])
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{PW:.0f}" height="{PH:.0f}" viewBox="0 0 {PW:.0f} {PH:.0f}">', f'<rect width="{PW:.0f}" height="{PH:.0f}" fill="white"/>',
           f'<g transform="translate({rtx:.2f},{rty:.2f}) scale({rs:.5f})">{render_colored(parts, details, sw_r)}</g>',
           (f'<g transform="translate({tx:.2f},{ty:.2f}) scale({s:.5f})" opacity="0.9">{render_colored(parts, details, sw_p * 1.1)}</g>' if done else
            f'<g transform="translate({tx:.2f},{ty:.2f}) scale({s:.5f})">{render_puzzle(parts, details, sw_p, sil_local)}</g>')]
    for (x, y) in pts: out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{R}" fill="{EINK}"/>')
    for txt, cx, cy, _ in labels:
        out.append(f'<text x="{cx:.1f}" y="{cy + fs * .36:.1f}" font-family="DejaVu Sans, Arial, sans-serif" font-weight="700" font-size="{fs}" text-anchor="middle" fill="{EINK}">{txt}</text>')
    out.append('</svg>'); open(path_svg, 'w').write('\n'.join(out))
    return len(pts), sum(1 for l in labels if l[3] >= 4)


def color_pngs(keys):
    """colored reference pictures (square, white background) for the cover and color-ideas pages."""
    from animals import ANIMALS
    from engine import render_colored, unary_union
    for k in keys:
        ch = ANIMALS[k](); g = unary_union([p.geom for p in ch['parts']]); x0, y0, x1, y1 = g.bounds
        side = max(x1 - x0, y1 - y0) + 120; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{cx - side / 2} {cy - side / 2} {side} {side}" width="800" height="800">'
               f'<rect x="{cx - side / 2}" y="{cy - side / 2}" width="{side}" height="{side}" fill="white"/>{render_colored(ch["parts"], ch["details"], 10)}</svg>')
        open(f'out/col_{k}.svg', 'w').write(svg)
        subprocess.run(['rsvg-convert', f'out/col_{k}.svg', '-o', f'out/col_{k}.png'], check=True)


def cover(c, W, H, letters):
    c.setFillColor(INK); c.setFont('B', 32); c.drawCentredString(W / 2, H - 30 * mm, f'ABC Dot to Dot · {letters[0]} to {letters[-1]}')
    c.setFont('R', 13)
    c.drawCentredString(W / 2, H - 40 * mm, 'Learn to write each letter, connect the dots, color it in,')
    c.drawCentredString(W / 2, H - 46.5 * mm, 'then scan the QR code and watch it come alive!')
    c.setStrokeColor(INK); c.setLineWidth(1.2); c.line(W / 2 - 40 * mm, H - 53 * mm, W / 2 + 40 * mm, H - 53 * mm)
    cols = 4; rows = -(-len(letters) // cols); g = 4 * mm
    size = min((W - 30 * mm - (cols - 1) * g) / cols, (H - 62 * mm - 30 * mm - (rows - 1) * g) / rows)
    top = H - 60 * mm
    for i, ch in enumerate(letters):
        col, row = i % cols, i // cols
        n_in_row = min(cols, len(letters) - row * cols)
        x0 = (W - n_in_row * size - (n_in_row - 1) * g) / 2
        x = x0 + col * (size + g); y = top - (row + 1) * size - row * g
        im = size - 12 * mm
        c.drawImage(f'out/col_{WORDS[ch][0]}.png', x + (size - im) / 2, y + 1.5 * mm, im, im)
        c.setStrokeColor(INK); c.setLineWidth(.6); c.roundRect(x, y, size, size, 2.5 * mm, fill=0, stroke=1)
        c.setFillColor(INK); c.setFont('B', 18); c.drawCentredString(x + size / 2, y + size - 8.5 * mm, ch + ch.lower())
    c.setFillColor(INK); c.setFont('B', 12)
    c.drawCentredString(W / 2, 21 * mm, f'{len(letters)} activity pages · Ages 3–6 · letters, counting and coloring')
    footer(c, W, '')


def how(c, W, H, letters):
    from reportlab.lib.utils import simpleSplit
    c.setFillColor(INK); c.setFont('B', 24); c.drawString(20 * mm, H - 30 * mm, 'How each page works')
    steps = [('1', 'Write your name', 'One letter in each box. The magic camera may say hello to you!'),
             ('2', 'Trace the big letter', 'Start at the circle with number 1 and follow the arrow, joining the dots. Then do 2, then 3. That is the order we write the letter.'),
             ('3', 'Practice', 'Trace the dotted letters in the two rows at the bottom, then write a few on your own.'),
             ('4', 'Connect the dots and color', 'Join the animal\'s dots from 1 to the end, then color it in. The little picture shows one way to color it.'),
             ('5', 'Scan and watch', 'A grown-up scans the QR code with a phone camera, opens the link, then points the phone at the page. No app needed.')]
    y = H - 50 * mm
    for n, t, d in steps:
        c.setStrokeColor(INK); c.setLineWidth(1.4); c.setFillColor(white); c.circle(27 * mm, y + 2 * mm, 7 * mm, fill=1, stroke=1)
        c.setFillColor(INK); c.setFont('B', 16); c.drawCentredString(27 * mm, y - .5 * mm, n)
        c.setFont('B', 14); c.drawString(40 * mm, y + 3 * mm, t); c.setFont('R', 10.5)
        for i, line in enumerate(simpleSplit(d, 'R', 10.5, W - 60 * mm)): c.drawString(40 * mm, y - 3 * mm - i * 5 * mm, line)
        y -= 25 * mm
    y -= 2 * mm
    c.setStrokeColor(INK); c.setLineWidth(.8); c.roundRect(20 * mm, y - 46 * mm, W - 40 * mm, 52 * mm, 4 * mm, fill=0, stroke=1)
    c.setFillColor(INK); c.setFont('B', 13); c.drawString(27 * mm, y - 3 * mm, 'Tips for grown-ups')
    c.setFont('R', 10.5)
    tips = ['Black-and-white printing is perfect. Every page is designed for it.',
            'Print at 100% / "Actual size" so the magic camera recognizes the page.',
            'Little ones can trace the big letter with a finger first, then with a crayon.',
            'Print as many copies as you like for your own family.',
            'The last page has color ideas. It is optional and looks best in color.']
    for i, t in enumerate(tips): c.drawString(27 * mm, y - 12 * mm - i * 7 * mm, '•  ' + t)
    footer(c, W, '')


def color_ideas(c, W, H, letters):
    c.setFillColor(INK); c.setFont('B', 22); c.drawString(15 * mm, H - 22 * mm, 'Color ideas')
    c.setFont('R', 10.5); c.drawString(15 * mm, H - 29 * mm, 'Optional page: print it in color or look at it on a screen. Any colors are fine!')
    cols = 4; rows = -(-len(letters) // cols); g = 4 * mm
    size = min((W - 30 * mm - (cols - 1) * g) / cols, (H - 40 * mm - 20 * mm - (rows - 1) * g) / rows)
    x0 = (W - cols * size - (cols - 1) * g) / 2; top = H - 36 * mm
    for i, ch in enumerate(letters):
        col, row = i % cols, i // cols
        x = x0 + col * (size + g); y = top - (row + 1) * size - row * g
        im = size - 9 * mm
        c.drawImage(f'out/col_{WORDS[ch][0]}.png', x + (size - im) / 2, y + 8 * mm, im, im)
        c.setStrokeColor(HexColor('#999999')); c.setLineWidth(.5); c.rect(x, y, size, size, fill=0, stroke=1)
        c.setFillColor(INK); c.setFont('B', 11); c.drawCentredString(x + size / 2, y + 3 * mm, f'{ch} is for {WORDS[ch][1]}')
    footer(c, W, '')


def bundle(letters, tag):
    from animals import ANIMALS
    color_pngs([WORDS[ch][0] for ch in letters])
    name = f'MaryMariiArt_ABC_Dot_to_Dot_{letters[0]}-{letters[-1]}'
    for size, sz in ((A4, 'A4'), (letter, 'Letter')):
        c = canvas.Canvas(f'out/{name}_{sz}.pdf', pagesize=size)
        c.setTitle(f'ABC Dot to Dot {letters[0]} to {letters[-1]} – MaryMariiArt'); c.setAuthor('MaryMariiArt')
        cover(c, *size, letters); c.showPage(); how(c, *size, letters); c.showPage()
        for i, ch in enumerate(letters, 1):
            sheet(c, *size, ch, i, len(letters), ANIMALS[WORDS[ch][0]]()['dots']); c.showPage()
        color_ideas(c, *size, letters); c.showPage(); c.save()
    return name


def done_pages(specs):
    """finished-looking pages (traced + colored + a made-up name) as PNGs for mockups."""
    from animals import ANIMALS
    for ch, name, crayon in specs:
        key = WORDS[ch][0]
        animal_panel(ANIMALS[key](), f'out/{key}_done.svg', done=True)
        subprocess.run(['rsvg-convert', '-w', '1400', f'out/{key}_done.svg', '-o', f'out/{key}_done.png'], check=True)
        for d, tag in ((dict(name=name, crayon=crayon), 'color'), (None, 'bw')):
            c = canvas.Canvas(f'out/mk_{tag}_{ch}.pdf', pagesize=A4)
            sheet(c, *A4, ch, ('ABCDEFGHIJKLM' if ch < 'N' else 'NOPQRSTUVWXYZ').index(ch) + 1, 13, ANIMALS[key]()['dots'], done=d); c.showPage(); c.save()
            subprocess.run(['pdftoppm', '-r', '200', '-png', '-singlefile', f'out/mk_{tag}_{ch}.pdf', f'out/mk_{tag}_{ch}'], check=True)


if __name__ == '__main__' and sys.argv[1:2] == ['done2']:
    done_pages([('R', 'MIA', '#E0503A'), ('P', 'LIAM', '#3D7BD8'), ('O', 'EVA', '#8E44AD'), ('T', 'OTTO', '#2E9E5B'),
                ('W', 'MAX', '#3D7BD8'), ('U', 'LILY', '#D6408A'), ('Z', 'ROSE', '#E58A1F'), ('N', 'MAX', '#1F8FB8')]); sys.exit()

if __name__ == '__main__' and sys.argv[1:2] == ['done']:
    done_pages([('A', 'MIA', '#E0503A'), ('B', 'LIAM', '#3D7BD8'), ('E', 'EVA', '#8E44AD'), ('L', 'OTTO', '#E58A1F'),
                ('D', 'MAX', '#2E9E5B'), ('C', 'LILY', '#D6408A'), ('F', 'ROSE', '#1F8FB8'), ('K', 'MAX', '#3D7BD8')]); sys.exit()

if __name__ == '__main__' and sys.argv[1:2] == ['bundle']:
    print(bundle(list(sys.argv[2] if len(sys.argv) > 2 else 'ABCDEFGHIJKLM'), '')); sys.exit()

if __name__ == '__main__':
    import os
    from animals import ANIMALS
    from engine import build_sheet
    letters = sys.argv[1:] or ['A']
    for ch in letters:
        key = WORDS[ch][0]
        cnt, bad = animal_panel(ANIMALS[key](), f'out/{key}.svg')
        subprocess.run(['rsvg-convert', '-w', '1400', f'out/{key}.svg', '-o', f'out/{key}.png'], check=True)
        print(ch, key, 'dots', cnt, 'label conflicts', bad)
    for size, tag in ((A4, 'A4'), (letter, 'Letter')):
        c = canvas.Canvas(f'out/sample_{"".join(letters)}_{tag}.pdf', pagesize=size)
        for i, ch in enumerate(letters, 1):
            from animals import ANIMALS
            sheet(c, *size, ch, i, 13, ANIMALS[WORDS[ch][0]]()['dots']); c.showPage()
        c.save()
