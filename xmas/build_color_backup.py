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
    for i in range(4):
        c.setFillColor(RED if i < n else HexColor('#E8DCDA'))
        c.setFont('B', size); c.drawString(x + i * size * 1.1, y, '★')

def footer(c, W, page_label):
    c.setFont('R', 7.5); c.setFillColor(GREY)
    c.drawString(15 * mm, 9 * mm, '© MaryMariiArt · for personal and family use · marymariiart.etsy.com')
    c.drawRightString(W - 15 * mm, 9 * mm, page_label)

def cover(c, W, H):
    c.setFillColor(SOFT); c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(RED); c.rect(0, H - 62 * mm, W, 62 * mm, fill=1, stroke=0)
    c.setFillColor(white); c.setFont('B', 34)
    c.drawCentredString(W / 2, H - 30 * mm, 'Christmas Dot to Dot')
    c.setFont('R', 14)
    c.drawCentredString(W / 2, H - 42 * mm, 'Connect the dots, color it in, then scan the QR')
    c.drawCentredString(W / 2, H - 50 * mm, 'and watch your picture come alive!')
    rows = -(-N // 3)
    g = 4 * mm; size = min((W - 30 * mm - 2 * g) / 3, (H - 72 * mm - 30 * mm - (rows - 1) * g) / rows)
    x0 = (W - 3 * size - 2 * g) / 2
    top = H - 70 * mm
    for i, (k, *_ ) in enumerate(SHEETS):
        col, row = i % 3, i // 3
        x = x0 + col * (size + g); y = top - (row + 1) * size - row * g
        c.setFillColor(white); c.roundRect(x, y, size, size, 4 * mm, fill=1, stroke=0)
        c.drawImage(f'img/{k}.jpg', x + 2 * mm, y + 2 * mm, size - 4 * mm, size - 4 * mm)
    c.setFillColor(INK); c.setFont('B', 13)
    c.drawCentredString(W / 2, 22 * mm, f'{N} activity pages · Ages 4–8 · easy to challenging')
    footer(c, W, '')

def how(c, W, H):
    c.setFillColor(RED); c.setFont('B', 24)
    c.drawString(20 * mm, H - 30 * mm, 'How the magic works')
    steps = [
        ('1', 'Connect the dots', 'Start at 1 and follow the numbers to the end. Use the small picture as a guide.'),
        ('2', 'Color it in', 'Crayons, markers or pencils all work. Bright colors look best in AR.'),
        ('3', 'Scan and watch', 'Point your phone camera at the QR code, open the link, then aim the camera at the page. No app needed.'),
    ]
    y = H - 50 * mm
    for n, t, d in steps:
        c.setFillColor(RED); c.circle(27 * mm, y + 2 * mm, 7 * mm, fill=1, stroke=0)
        c.setFillColor(white); c.setFont('B', 16); c.drawCentredString(27 * mm, y - 0.5 * mm, n)
        c.setFillColor(INK); c.setFont('B', 14); c.drawString(40 * mm, y + 3 * mm, t)
        c.setFont('R', 10.5)
        from reportlab.lib.utils import simpleSplit
        for i, line in enumerate(simpleSplit(d, 'R', 10.5, W - 60 * mm)):
            c.drawString(40 * mm, y - 3 * mm - i * 5 * mm, line)
        y -= 30 * mm
    y -= 4 * mm
    c.setFillColor(SOFT); c.roundRect(20 * mm, y - 52 * mm, W - 40 * mm, 58 * mm, 4 * mm, fill=1, stroke=0)
    c.setFillColor(INK); c.setFont('B', 13); c.drawString(27 * mm, y - 3 * mm, 'Print tips')
    c.setFont('R', 10.5)
    tips = ['Print at 100% / "Actual size" so the AR picture is recognized.',
            'Plain white paper is fine; slightly heavier paper is nicer for markers.',
            'Pages are ordered from easiest (30 dots) to hardest (73 dots).',
            'Print as many copies as you like for your own family.',
            'Grown-ups: please help younger children with scanning.']
    for i, t in enumerate(tips):
        c.drawString(27 * mm, y - 12 * mm - i * 7.5 * mm, '•  ' + t)
    footer(c, W, '')

def sheet(c, W, H, k, name, dots, lvl, idx, img=None, total=None):
    m = 15 * mm
    c.setFillColor(INK); c.setFont('B', 11)
    c.drawString(m, H - 18 * mm, 'Name:')
    c.setStrokeColor(GREY); c.setLineWidth(0.6); c.line(m + 14 * mm, H - 18.5 * mm, m + 80 * mm, H - 18.5 * mm)
    c.setFont('B', 20); c.setFillColor(RED)
    c.drawRightString(W - m, H - 19 * mm, f'{name} · Dots 1–{dots}')
    stars(c, W - m - 4 * 12.1, H - 27 * mm, lvl)
    # artwork
    qr_h = 34 * mm
    avail_h = H - 32 * mm - (qr_h + 18 * mm)
    s = min(W - 2 * m, avail_h)
    x = (W - s) / 2; y = qr_h + 18 * mm + (avail_h - s) / 2
    c.drawImage(img or f'img/{k}.jpg', x, y, s, s)
    sheet.art_box = (x, y, s)
    # QR strip
    by = 15 * mm
    c.setFillColor(SOFT); c.roundRect(m, by, W - 2 * m, qr_h, 4 * mm, fill=1, stroke=0)
    q = qr_h - 8 * mm
    c.setFillColor(white); c.setStrokeColor(RED); c.setLineWidth(1)
    c.roundRect(m + 4 * mm, by + 4 * mm, q, q, 2 * mm, fill=1, stroke=0)
    from reportlab.graphics.barcode.qr import QrCodeWidget
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics import renderPDF
    url = f'https://marymarii.com/scan/?s={k}'
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
    c.save()

if __name__ == '__main__':
    build(A4, 'MaryMariiArt_Christmas_Dot_to_Dot_A4.pdf')
    build(letter, 'MaryMariiArt_Christmas_Dot_to_Dot_Letter.pdf')
