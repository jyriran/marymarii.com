from engine import *

RED = '#E05A5F'; CREAM = '#EFE6D8'; PLUM = '#6B4A63'; BROWN = '#8C7366'; DARK = '#5A4A40'
PINK = '#F4B7B0'; ORANGE = '#F0963C'; GREEN = '#6FAE8E'; TEAL = '#8CC5C0'; YELLOW = '#F2C14E'
NAVY = '#4A4E66'; GINGER = '#C98A55'; FOX = '#E08A4B'; OWL = '#A67C63'

def eye(x, y, r, sw):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="{INK}"/>'
            f'<ellipse cx="{x + r * .3}" cy="{y - r * .35}" rx="{r * .35}" ry="{r * .28}" fill="white"/>')

def cheek(x, y, rx, ry, colored, sw):
    return fill_path(ellipse(x, y, rx, ry), PINK if colored else 'white', INK if not colored else 'none', sw * (0 if colored else 0.8)) if colored else \
        f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="none" stroke="{INK}" stroke-width="{sw * .7}"/>'

def smile(x, y, w, sw, depth=None):
    depth = depth or w * 0.45
    return f'<path d="M{x - w / 2},{y} Q{x},{y + depth} {x + w / 2},{y}" fill="none" stroke="{INK}" stroke-width="{sw * .8}" stroke-linecap="round"/>'

def shape(g, colored, fill, sw, k=1.0):
    return fill_path(g, fill if colored else 'white', INK, sw * k)

# ------------------------------------------------------------------ PENGUIN
def penguin():
    body = ellipse(500, 700, 320, 390)
    fl_l = ellipse(205, 720, 70, 190, 28); fl_r = ellipse(795, 720, 70, 190, -28)
    ft_l = ellipse(395, 1085, 115, 48, 8); ft_r = ellipse(605, 1085, 115, 48, -8)
    belly = unary_union([ellipse(500, 800, 235, 280), circle(410, 545, 100), circle(590, 545, 100)]).intersection(body.buffer(-35))
    hat = poly([(255, 450), (300, 260), (420, 150), (600, 125), (790, 215), (820, 275), (745, 450)], 30)
    band = soften(box(225, 395, 775, 490), 40)
    pom = circle(815, 255, 62)
    parts = [Part(fl_l, NAVY), Part(fl_r, NAVY), Part(ft_l, ORANGE), Part(ft_r, ORANGE),
             Part(body, NAVY), Part(belly, 'white', tex=lambda g: rings(ellipse(500, 820, 225, 265), 48, 3, 40), dash=True),
             Part(hat, RED), Part(band, CREAM, tex=lambda g: scallops(g, 46, 12)), Part(pom, CREAM, tex=lambda g: scallops(g, 40, 10))]

    def details(c, sw):
        beak = poly([(455, 600), (545, 600), (500, 665)], 8)
        return (eye(420, 548, 24, sw) + eye(580, 548, 24, sw) + shape(beak, c, ORANGE, sw, .8)
                + cheek(360, 610, 30, 18, c, sw) + cheek(640, 610, 30, 18, c, sw)
                + fill_path(circle(500, 900, 26), RED if c else 'white', INK, sw * .7)
                + fill_path(circle(500, 990, 26), RED if c else 'white', INK, sw * .7))
    return dict(parts=parts, details=details, dots=42, start=(225, 900))

# ------------------------------------------------------------------ GINGERBREAD
def gingerbread():
    g = unary_union([circle(500, 270, 195), soften(box(330, 410, 670, 830), 60),
                     capsule((360, 520), (140, 400), 165), capsule((640, 520), (860, 400), 165),
                     capsule((425, 800), (290, 1100), 175), capsule((575, 800), (710, 1100), 175)])
    g = soften(g, 65)
    bow = unary_union([poly([(500, 470), (420, 425), (420, 515)], 10), poly([(500, 470), (580, 425), (580, 515)], 10), circle(500, 470, 24)])
    parts = [Part(g, GINGER), Part(bow, RED, sil=False)]

    def wavy(x0, y0, x1, y1, amp=14, waves=4):
        pts = []
        for i in range(41):
            t = i / 40
            x = x0 + (x1 - x0) * t; y = y0 + (y1 - y0) * t
            L = math.hypot(x1 - x0, y1 - y0); nx, ny = -(y1 - y0) / L, (x1 - x0) / L
            o = amp * math.sin(t * waves * 2 * math.pi)
            pts.append((x + nx * o, y + ny * o))
        return LineString(pts)

    def details(c, sw):
        icing = unary_union([wavy(165, 335, 115, 455), wavy(835, 335, 885, 455),
                             wavy(220, 1070, 360, 1125), wavy(640, 1125, 780, 1070),
                             wavy(370, 140, 630, 140, 12, 5)])
        s = stroke_path(icing, sw * (1.1 if c else .8), 'white' if c else INK)
        if c:  # outline icing so it reads on cookie
            s = stroke_path(icing, sw * 1.9, INK) + s
        for y in (600, 690, 780):
            s += fill_path(circle(500, y, 30), [RED, GREEN, RED][(y // 90) % 3] if c else 'white', INK, sw * .7)
            s += f'<circle cx="490" cy="{y - 7}" r="5" fill="{INK}"/><circle cx="510" cy="{y + 7}" r="5" fill="{INK}"/>'
        s += eye(430, 255, 26, sw) + eye(570, 255, 26, sw) + smile(500, 325, 110, sw)
        s += cheek(390, 320, 30, 18, c, sw) + cheek(610, 320, 30, 18, c, sw)
        return s
    return dict(parts=parts, details=details, dots=42, start=(290, 1180))

# ------------------------------------------------------------------ CHRISTMAS TREE
def tree():
    def tier(top, half, y1):
        return poly([(500, top), (500 + half, y1), (500 - half, y1)], 18)
    t3 = tier(600, 370, 930); t2 = tier(385, 290, 690); t1 = tier(195, 190, 450)
    trunk = box(430, 900, 570, 1060)
    pot = poly([(350, 1040), (650, 1040), (615, 1190), (385, 1190)], 12)
    st = soften(star(500, 85, 105, 46), 6)
    parts = [Part(trunk, DARK), Part(pot, RED, tex=lambda g: scallops(g, 46, 12)),
             Part(t3, GREEN), Part(t2, GREEN), Part(t1, GREEN), Part(st, YELLOW, sil=False)]

    def details(c, sw):
        s = ''
        gar = [LineString([(415, 505), (500, 520), (585, 505)]), LineString([(365, 748), (500, 765), (635, 748)])]
        for gl in gar:
            pts = list(gl.coords)
            d = f'M{pts[0][0]},{pts[0][1]} Q{pts[1][0]},{pts[1][1] + 40} {pts[2][0]},{pts[2][1]}'
            s += f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="{sw * .8}" stroke-dasharray="{sw * 2.2} {sw * 1.6}" stroke-linecap="round"/>'
        balls = [(390, 615, RED), (500, 630, TEAL), (610, 615, YELLOW),
                 (320, 860, TEAL), (440, 872, YELLOW), (560, 872, RED), (680, 860, YELLOW)]
        for x, y, col in balls:
            s += fill_path(circle(x, y, 30), col if c else 'white', INK, sw * .75)
            s += f'<path d="M{x - 12},{y - 8} q8,-10 16,-4" fill="none" stroke="{"white" if c else INK}" stroke-width="{sw * .5}" stroke-linecap="round"/>'
        s += eye(470, 345, 18, sw) + eye(530, 345, 18, sw) + smile(500, 382, 50, sw)
        return s
    return dict(parts=parts, details=details, dots=44, start=(385, 1190))

# ------------------------------------------------------------------ FOX
def fox():
    head = poly([(250, 320), (330, 240), (500, 215), (670, 240), (750, 320), (700, 470), (500, 565), (300, 470)], 55)
    ear_l = poly([(275, 330), (300, 70), (460, 250)], 22); ear_r = poly([(725, 330), (700, 70), (540, 250)], 22)
    in_l = poly([(310, 290), (318, 150), (410, 255)], 14); in_r = poly([(690, 290), (682, 150), (590, 255)], 14)
    body = ellipse(500, 820, 225, 270)
    neck = soften(box(370, 460, 630, 660), 30)
    def chaikin(pts, it=4):
        for _ in range(it):
            out = []
            for i in range(len(pts)):
                a, b = pts[i], pts[(i + 1) % len(pts)]
                out += [(a[0] * .75 + b[0] * .25, a[1] * .75 + b[1] * .25), (a[0] * .25 + b[0] * .75, a[1] * .25 + b[1] * .75)]
            pts = out
        return Polygon(pts)
    tail = chaikin([(600, 1085), (800, 1080), (935, 975), (995, 810), (975, 650), (915, 535), (880, 520),
                    (865, 585), (800, 650), (690, 720), (620, 900)])
    fluff = Polygon([(760, 380), (1100, 380), (1100, 700), (1010, 672), (975, 712), (940, 662), (902, 702),
                     (866, 650), (830, 680), (760, 640)])
    tip = tail.intersection(fluff)
    ft_l = ellipse(420, 1080, 85, 48); ft_r = ellipse(580, 1080, 85, 48)
    muzzle = unary_union([ellipse(415, 470, 110, 75, -12), ellipse(585, 470, 110, 75, 12)]).intersection(head.buffer(-20))
    belly = ellipse(500, 870, 130, 175)
    scarf = soften(box(300, 515, 700, 610), 40)
    tail_end = poly([(560, 580), (650, 590), (640, 800), (560, 785)], 20)
    stripes = lambda g: dashes(g, 40, 34, 0, jitter=False)
    nk = unary_union([head, body, neck]).buffer(-4)
    scarf = scarf.intersection(nk); tail_end = tail_end.intersection(nk)
    parts = [Part(tail, FOX), Part(tip, CREAM, sil=False), Part(ft_l, DARK), Part(ft_r, DARK), Part(neck, FOX), Part(body, FOX),
             Part(belly, CREAM, sil=False), Part(tail_end, RED, tex=stripes, sil=False), Part(ear_l, FOX), Part(ear_r, FOX),
             Part(in_l, DARK, sil=False), Part(in_r, DARK, sil=False), Part(head, FOX), Part(muzzle, CREAM, sil=False),
             Part(scarf, RED, tex=lambda g: dashes(g, 36, 40, 90, jitter=False), sil=False)]

    def details(c, sw):
        s = eye(420, 365, 24, sw) + eye(580, 365, 24, sw)
        s += f'<ellipse cx="500" cy="470" rx="34" ry="24" fill="{INK}"/><ellipse cx="510" cy="462" rx="10" ry="6" fill="white"/>'
        s += smile(500, 505, 60, sw, 22) + cheek(365, 420, 26, 16, c, sw) + cheek(635, 420, 26, 16, c, sw)
        return s
    return dict(parts=parts, details=details, dots=56, start=(415, 1130))

# ------------------------------------------------------------------ OWL
def owl():
    body = ellipse(500, 640, 320, 420)
    tuft_l = poly([(240, 430), (210, 70), (440, 290)], 22); tuft_r = poly([(760, 430), (790, 70), (560, 290)], 22)
    wing_l = ellipse(270, 720, 75, 200, 10).intersection(body.buffer(-25)); wing_r = ellipse(730, 720, 75, 200, -10).intersection(body.buffer(-25))
    belly = ellipse(500, 790, 180, 235)
    face = unary_union([circle(405, 470, 125), circle(595, 470, 125)])
    ft = ellipse(415, 1102, 66, 30); ft2 = ellipse(585, 1102, 66, 30)
    scarf = soften(box(290, 590, 710, 675), 40)
    scarf_end = poly([(330, 640), (420, 640), (400, 860), (315, 840)], 20)
    scarf = scarf.intersection(body.buffer(-4)); scarf_end = scarf_end.intersection(body.buffer(-4))
    parts = [Part(tuft_l, OWL), Part(tuft_r, OWL), Part(body, OWL),
             Part(wing_l, BROWN, tex=lambda g: scallops(g, 46, 12), sil=False),
             Part(wing_r, BROWN, tex=lambda g: scallops(g, 46, 12), sil=False),
             Part(belly, CREAM, tex=lambda g: scallops(g, 52, 14)), Part(face, CREAM),
             Part(ft, ORANGE, sil=False, puzzle=False), Part(ft2, ORANGE, sil=False, puzzle=False),
             Part(scarf_end, TEAL, tex=lambda g: dashes(g, 36, 40, 0, jitter=False), sil=False),
             Part(scarf, TEAL, tex=lambda g: dashes(g, 36, 44, 90, jitter=False), sil=False)]

    def details(c, sw):
        s = ''
        for x in (405, 595):
            s += f'<circle cx="{x}" cy="470" r="70" fill="{"white" if c else "white"}" stroke="{INK}" stroke-width="{sw * .7}"/>'
            s += eye(x, 475, 36, sw)
        beak = poly([(470, 535), (530, 535), (500, 590)], 8)
        s += shape(beak, c, ORANGE, sw, .8)
        s += cheek(320, 560, 28, 16, c, sw) + cheek(680, 560, 28, 16, c, sw)
        for fx in ((415, 585) if c else ()):
            for dx in (-25, 25):
                s += f'<path d="M{fx + dx},{1090} L{fx + dx},{1118}" stroke="{INK}" stroke-width="{sw * .6}" stroke-linecap="round"/>'
        return s
    return dict(parts=parts, details=details, dots=44, start=(300, 1000))

CHARS = {'penguin': penguin, 'gingerbread': gingerbread, 'tree': tree, 'fox': fox, 'owl': owl}
