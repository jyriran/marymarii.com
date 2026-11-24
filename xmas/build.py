import sys
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('B', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('R', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))

RED = HexColor('#E05A5F'); INK = HexColor('#2B1D16'); SOFT = HexColor('#FBEDEC'); GREY = HexColor('#8A7F7A')

_S = [('hedgehog', 'Hedgehog', 30), ('gift', 'Gift Box', 32), ('bell', 'Bell', 34), ('stocking', 'Stocking', 36),
      ('snowman', 'Snowman', 40), ('gingerbread', 'Gingerbread', 42), ('penguin', 'Penguin', 42), ('tree', 'Christmas Tree', 44),
      ('owl', 'Owl', 44), ('santa', 'Santa', 48), ('house', 'Gingerbread House', 48), ('bunny', 'Bunny', 52),
      ('fox', 'Fox', 56), ('reindeer', 'Reindeer', 59), ('bear', 'Polar Bear', 73)]
SHEETS = [(k, n, d, 1 if d <= 36 else 2 if d <= 44 else 3 if d <= 56 else 4) for k, n, d in _S]
N = len(SHEETS)

def stars(c, x, y, n, size=11):
    c.setFillColor(INK); c.setFont('B', size)
    c.drawString(x, y, '★' * n + '☆' * (4 - n))

def footer(c, W, page_label):
    c.setFont('R', 7.5); c.setFillColor(HexColor('#444444'))
    c.drawString(15 * mm, 15.5 * mm - 7, '© MaryMariiArt · for personal and family use · marymariiart.etsy.com')
    c.drawRightString(W - 15 * mm, 15.5 * mm - 7, page_label)

def cover(c, W, H):
    c.setFillColor(INK); c.setFont('B', 34)
    c.drawCentredString(W / 2, H - 30 * mm, 'Christmas Dot to Dot')
    c.setFont('R', 13)
    c.drawCentredString(W / 2, H - 40 * mm, 'Connect the dots, color it in, then scan the QR code')
    c.drawCentredString(W / 2, H - 46.5 * mm, 'and watch your picture come alive!')
    c.setStrokeColor(INK); c.setLineWidth(1.2); c.line(W / 2 - 40 * mm, H - 53 * mm, W / 2 + 40 * mm, H - 53 * mm)
    rows = -(-N // 3)
    g = 4 * mm; size = min((W - 30 * mm - 2 * g) / 3, (H - 62 * mm - 30 * mm - (rows - 1) * g) / rows)
    x0 = (W - 3 * size - 2 * g) / 2
    top = H - 60 * mm
    for i, (k, *_ ) in enumerate(SHEETS):
        col, row = i % 3, i // 3
        x = x0 + col * (size + g); y = top - (row + 1) * size - row * g
        c.drawImage(f'img_bw/{k}.png', x + 1 * mm, y + 1 * mm, size - 2 * mm, size - 2 * mm)
        c.setStrokeColor(INK); c.setLineWidth(0.6); c.roundRect(x, y, size, size, 2.5 * mm, fill=0, stroke=1)
    c.setFillColor(INK); c.setFont('B', 12)
    c.drawCentredString(W / 2, 21 * mm, f'{N} activity pages · Ages 4–8 · easy to challenging')
    footer(c, W, '')

def how(c, W, H):
    from reportlab.lib.utils import simpleSplit
    c.setFillColor(INK); c.setFont('B', 24)
    c.drawString(20 * mm, H - 30 * mm, 'How the magic works')
    steps = [
        ('1', 'Write your name', 'One letter in each box. The magic camera may say hello to you!'),
        ('2', 'Connect the dots', 'Start at 1 and follow the numbers to the end. The little picture shows what you are drawing.'),
        ('3', 'Color it in', 'Crayons, markers or pencils all work. Bright colors look best when it comes alive.'),
        ('4', 'Scan and watch', 'A grown-up scans the QR code with a phone camera, opens the link, then points the phone at the page. No app needed.'),
    ]
    y = H - 50 * mm
    for n, t, d in steps:
        c.setStrokeColor(INK); c.setLineWidth(1.4); c.setFillColor(white); c.circle(27 * mm, y + 2 * mm, 7 * mm, fill=1, stroke=1)
        c.setFillColor(INK); c.setFont('B', 16); c.drawCentredString(27 * mm, y - 0.5 * mm, n)
        c.setFont('B', 14); c.drawString(40 * mm, y + 3 * mm, t)
        c.setFont('R', 10.5)
        for i, line in enumerate(simpleSplit(d, 'R', 10.5, W - 60 * mm)):
            c.drawString(40 * mm, y - 3 * mm - i * 5 * mm, line)
        y -= 26 * mm
    y -= 2 * mm
    c.setStrokeColor(INK); c.setLineWidth(0.8); c.roundRect(20 * mm, y - 52 * mm, W - 40 * mm, 58 * mm, 4 * mm, fill=0, stroke=1)
    c.setFillColor(INK); c.setFont('B', 13); c.drawString(27 * mm, y - 3 * mm, 'Print tips')
    c.setFont('R', 10.5)
    tips = ['Black-and-white printing is perfect. Every page is designed for it.',
            'Print at 100% / "Actual size" so the magic camera recognizes the page.',
            'Pages are ordered from easiest (30 dots) to hardest (73 dots).',
            'Print as many copies as you like for your own family.',
            'The last page has color ideas. It is optional and looks best in color.']
    for i, t in enumerate(tips):
        c.drawString(27 * mm, y - 12 * mm - i * 7.5 * mm, '•  ' + t)
    footer(c, W, '')

def color_ideas(c, W, H):
    c.setFillColor(INK); c.setFont('B', 22)
    c.drawString(15 * mm, H - 22 * mm, 'Color ideas')
    c.setFont('R', 10.5)
    c.drawString(15 * mm, H - 29 * mm, 'Optional page: print it in color or look at it on a screen. Any colors are fine!')
    cols = 3; rows = -(-N // cols); g = 4 * mm
    size = min((W - 30 * mm - (cols - 1) * g) / cols, (H - 40 * mm - 20 * mm - (rows - 1) * g) / rows)
    x0 = (W - cols * size - (cols - 1) * g) / 2; top = H - 36 * mm
    for i, (k, name, *_ ) in enumerate(SHEETS):
        col, row = i % cols, i // cols
        x = x0 + col * (size + g); y = top - (row + 1) * size - row * g
        c.drawImage(f'img/{k}.jpg', x, y, size, size)
        c.setStrokeColor(HexColor('#999999')); c.setLineWidth(0.5); c.rect(x, y, size, size, fill=0, stroke=1)
    footer(c, W, '')


def deco_border(c, W, H, seed):
    """Scattered black Christmas icons in the page margin: a unique, high-contrast pattern the
    magic camera can lock onto even after the drawing has been colored in."""
    import random, math
    from reportlab.lib.colors import black
    rnd = random.Random(seed)
    inner, outer = 15 * mm, 5.5 * mm          # band between page edge + 5.5mm and the content margin
    placed = []
    def free(x, y, r):
        return all(math.hypot(x - px, y - py) > r + pr + 1.2 * mm for px, py, pr in placed)
    def star_path(p, x, y, r, n=5, inner_k=0.45, rot=0):
        for i in range(2 * n):
            rr = r if i % 2 == 0 else r * inner_k
            a = rot + math.pi / 2 + i * math.pi / n
            px, py = x + rr * math.cos(a), y + rr * math.sin(a)
            (p.moveTo if i == 0 else p.lineTo)(px, py)
        p.close()
    def icon(kind, x, y, r, rot):
        c.saveState(); c.setFillColor(black); c.setStrokeColor(black)
        p = c.beginPath()
        if kind == 'star':
            star_path(p, x, y, r, 5, 0.45, rot); c.drawPath(p, fill=1, stroke=0)
        elif kind == 'spark':
            star_path(p, x, y, r, 4, 0.28, rot); c.drawPath(p, fill=1, stroke=0)
        elif kind == 'flake':
            c.setLineWidth(r * 0.22); c.setLineCap(1)
            for i in range(3):
                a = rot + i * math.pi / 3
                c.line(x - r * math.cos(a), y - r * math.sin(a), x + r * math.cos(a), y + r * math.sin(a))
            c.circle(x, y, r * 0.22, fill=1, stroke=0)
        elif kind == 'tree':
            c.translate(x, y)
            p.moveTo(0, r); p.lineTo(r * 0.55, r * 0.15); p.lineTo(-r * 0.55, r * 0.15); p.close()
            p.moveTo(0, r * 0.45); p.lineTo(r * 0.8, -r * 0.55); p.lineTo(-r * 0.8, -r * 0.55); p.close()
            c.drawPath(p, fill=1, stroke=0); c.rect(-r * 0.16, -r, r * 0.32, r * 0.48, fill=1, stroke=0)
        elif kind == 'dot':
            c.circle(x, y, r * 0.55, fill=1, stroke=0)
        elif kind == 'ring':
            c.setLineWidth(r * 0.3); c.circle(x, y, r * 0.6, fill=0, stroke=1)
        elif kind == 'heart':
            c.translate(x, y); c.rotate(math.degrees(rot) * 0.3)
            p.moveTo(0, -r * 0.8); p.curveTo(r * 1.2, 0, r * 0.5, r * 0.9, 0, r * 0.35)
            p.curveTo(-r * 0.5, r * 0.9, -r * 1.2, 0, 0, -r * 0.8); c.drawPath(p, fill=1, stroke=0)
        c.restoreState()
    kinds = ['star', 'star', 'spark', 'flake', 'flake', 'tree', 'dot', 'ring', 'heart']
    tries = 0
    while tries < 6000 and len(placed) < 90:
        tries += 1
        r = rnd.uniform(2.4, 4.6) * mm
        side = rnd.random() * (2 * (W + H))
        if side < W:                      x, y = side, rnd.uniform(H - inner + r, H - outer - r)
        elif side < W + H:                x, y = rnd.uniform(W - inner + r, W - outer - r), side - W
        elif side < 2 * W + H:            x, y = side - W - H, rnd.uniform(outer + r, inner - r)
        else:                             x, y = rnd.uniform(outer + r, inner - r), side - 2 * W - H
        if not (outer + r <= x <= W - outer - r and outer + r <= y <= H - outer - r): continue
        if inner - 0.5 * mm < x < W - inner + 0.5 * mm and inner - 0.5 * mm < y < H - inner + 0.5 * mm: continue
        if not free(x, y, r): continue
        placed.append((x, y, r)); icon(rnd.choice(kinds), x, y, r, rnd.uniform(0, 2 * math.pi))

def sheet(c, W, H, k, name, dots, lvl, idx, img=None, total=None):
    deco_border(c, W, H, 'mm-' + k)
    m = 15 * mm
    c.setFillColor(INK); c.setFont('B', 22)
    c.drawString(m, H - 20 * mm, name)
    c.setFont('R', 13); c.drawString(m + c.stringWidth(name, 'B', 22) + 4 * mm, H - 20 * mm, f'Dots 1–{dots}')
    stars(c, W - m - 4 * 13 * 0.62 - 20, H - 20 * mm, lvl, size=13)
    # name: one letter per box (helps the magic camera read it)
    c.setFont('B', 11); c.drawString(m, H - 31.5 * mm, 'My name:')
    bw_, bh_, gap = 9 * mm, 11 * mm, 1.4 * mm
    bx0, by0 = m + 22 * mm, H - 35 * mm
    boxes = []
    c.setStrokeColor(INK); c.setLineWidth(0.9)
    for i in range(10):
        bx = bx0 + i * (bw_ + gap)
        c.roundRect(bx, by0, bw_, bh_, 1.2 * mm, fill=0, stroke=1)
        boxes.append((bx, by0, bw_, bh_))
    sheet.name_boxes = boxes
    # artwork
    qr_h = 34 * mm
    avail_h = H - 39 * mm - (qr_h + 21 * mm)
    s = min(W - 2 * m, avail_h)
    x = (W - s) / 2; y = qr_h + 21 * mm + (avail_h - s) / 2
    c.drawImage(img or f'img_bw/{k}.png', x, y, s, s)
    sheet.art_box = (x, y, s)
    # QR strip
    by = 18.5 * mm
    c.setStrokeColor(INK); c.setLineWidth(0.8); c.roundRect(m, by, W - 2 * m, qr_h, 4 * mm, fill=0, stroke=1)
    q = qr_h - 8 * mm
    from reportlab.graphics.barcode.qr import QrCodeWidget
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics import renderPDF
    url = f'https://marymarii.com/scan/?s={k}' + ('&size=letter' if abs(W - 612) < 1 else '')
    w = QrCodeWidget(url, barLevel='M')
    x1, y1, x2, y2 = w.getBounds(); qs = q - 2 * mm
    d = Drawing(qs, qs, transform=[qs / (x2 - x1), 0, 0, qs / (y2 - y1), 0, 0]); d.add(w)
    renderPDF.draw(d, c, m + 4 * mm + 1 * mm, by + 4 * mm + 1 * mm)
    tx = m + q + 10 * mm
    c.setFillColor(INK); c.setFont('B', 14)
    c.drawString(tx, by + qr_h - 11 * mm, 'Finished? Make it come alive!')
    c.setFont('R', 10.5)
    c.drawString(tx, by + qr_h - 18 * mm, 'Ask a grown-up to scan the QR code with a phone camera,')
    c.drawString(tx, by + qr_h - 23.5 * mm, 'then point the phone at this page. No app needed.')
    footer(c, W, f'Page {idx} of {total or N}')

def build(size, path):
    W, H = size
    c = canvas.Canvas(path, pagesize=size)
    c.setTitle('Christmas Dot to Dot – MaryMariiArt'); c.setAuthor('MaryMariiArt')
    cover(c, W, H); c.showPage()
    how(c, W, H); c.showPage()
    for i, s in enumerate(SHEETS, 1):
        sheet(c, W, H, *s, i); c.showPage()
    color_ideas(c, W, H); c.showPage()
    c.save()

if __name__ == '__main__':
    build(A4, 'MaryMariiArt_Christmas_Dot_to_Dot_A4.pdf')
    build(letter, 'MaryMariiArt_Christmas_Dot_to_Dot_Letter.pdf')
