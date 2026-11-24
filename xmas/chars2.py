from chars import *

def chaikin(pts, it=4):
    for _ in range(it):
        out = []
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            out += [(a[0] * .75 + b[0] * .25, a[1] * .75 + b[1] * .25), (a[0] * .25 + b[0] * .75, a[1] * .25 + b[1] * .75)]
        pts = out
    return Polygon(pts)

def ring_dot(x, y, r, c, col, sw):
    return fill_path(circle(x, y, r), col if c else 'white', INK, sw * .6)

def face(x, y, sw, c, gap=60, er=20, cheeks=True):
    s = eye(x - gap, y, er, sw) + eye(x + gap, y, er, sw) + smile(x, y + er * 1.8, gap * .8, sw)
    if cheeks:
        s += cheek(x - gap * 1.7, y + er * 1.6, er * 1.2, er * .7, c, sw) + cheek(x + gap * 1.7, y + er * 1.6, er * 1.2, er * .7, c, sw)
    return s

# ------------------------------------------------------------------ GIFT BOX
def gift():
    boxg = soften(box(240, 520, 760, 1060), 25)
    lid = soften(box(195, 420, 805, 545), 25)
    loop_l = ellipse(390, 370, 135, 85, -20); loop_r = ellipse(610, 370, 135, 85, 20)
    knot = circle(500, 415, 50)
    rib_v = box(455, 545, 545, 1060).intersection(boxg); rib_lid = box(455, 420, 545, 545).intersection(lid)
    parts = [Part(loop_l, RED), Part(loop_r, RED), Part(boxg, TEAL), Part(rib_v, RED, sil=False),
             Part(lid, TEAL), Part(rib_lid, RED, sil=False), Part(knot, RED)]

    def details(c, sw):
        s = ''
        for x, y in [(320, 640), (680, 640), (320, 960), (680, 960), (390, 800), (610, 800)]:
            s += ring_dot(x, y, 22, c, YELLOW, sw)
        s += face(500, 720, sw, c, gap=0.001, er=0) if False else ''
        # loop inner folds
        s += f'<path d="M455,365 Q400,330 340,330" fill="none" stroke="{INK}" stroke-width="{sw * .6}" stroke-linecap="round"/>'
        s += f'<path d="M545,365 Q600,330 660,330" fill="none" stroke="{INK}" stroke-width="{sw * .6}" stroke-linecap="round"/>'
        return s
    return dict(parts=parts, details=details, dots=32, start=(240, 1060))

# ------------------------------------------------------------------ BELL
def bell():
    body = chaikin([(500, 235), (615, 255), (680, 370), (705, 590), (760, 760), (840, 850), (160, 850), (240, 760), (295, 590), (320, 370), (385, 255)])
    rim = soften(box(165, 800, 835, 900), 40)
    clap = circle(500, 935, 55)
    leaf_l = poly([(500, 215), (430, 140), (330, 150), (365, 200), (320, 240), (420, 250)], 12)
    leaf_r = affinity.scale(leaf_l, -1, 1, origin=(500, 0))
    leaf_l = affinity.translate(leaf_l, -40, -95); leaf_r = affinity.translate(leaf_r, 40, -95)
    parts = [Part(clap, YELLOW), Part(body, YELLOW), Part(rim, RED, tex=lambda g: scallops(g, 46, 12)),
             Part(leaf_l, GREEN, sil=False), Part(leaf_r, GREEN, sil=False)] + [Part(circle(x, y, 24), RED, sil=False) for x, y in [(470, 110), (530, 110), (500, 75)]]

    def details(c, sw):
        s = ''
        s = f'<path d="M500,135 L500,222" stroke="{INK}" stroke-width="{sw * .9}" stroke-linecap="round"/>' + s
        s += face(500, 560, sw, c, gap=65, er=22)
        s += f'<path d="M360,420 Q370,330 430,300" fill="none" stroke="{"white" if c else INK}" stroke-width="{sw * .8}" stroke-linecap="round"/>'
        return s
    return dict(parts=parts, details=details, dots=34, start=(165, 900))

# ------------------------------------------------------------------ STOCKING
def stocking():
    leg = chaikin([(370, 280), (650, 280), (660, 760), (640, 900), (560, 990), (330, 1030), (200, 1000), (150, 920),
                   (190, 830), (330, 770), (380, 720)], 3)
    cuff = soften(box(320, 140, 710, 320), 35)
    heel = leg.intersection(circle(640, 930, 140))
    toe = leg.intersection(circle(165, 960, 150))
    stripes = unary_union([box(300, y, 700, y + 50) for y in (400, 520, 640)]).intersection(leg)
    parts = [Part(leg, RED), Part(stripes, CREAM, sil=False), Part(heel, CREAM, sil=False), Part(toe, CREAM, sil=False),
             Part(cuff, CREAM, tex=lambda g: scallops(g, 46, 12))]

    def details(c, sw):
        s = f'<path d="M640,150 Q700,40 770,110 Q790,150 705,175" fill="none" stroke="{INK}" stroke-width="{sw * .9}" stroke-linecap="round"/>'
        s += face(510, 780, sw, c, gap=55, er=20)
        return s
    return dict(parts=parts, details=details, dots=36, start=(330, 140), extra_bounds=box(620, 20, 800, 200))

# ------------------------------------------------------------------ GINGERBREAD HOUSE
def house():
    walls = box(230, 560, 770, 1070)
    roof = poly([(140, 640), (500, 250), (860, 640)], 30)
    chimney = box(635, 290, 725, 520)
    snow = chaikin([(150, 615), (500, 240), (850, 615), (845, 650), (800, 640), (760, 690), (710, 645), (650, 700), (590, 650), (530, 705),
                    (470, 650), (410, 705), (350, 650), (290, 695), (235, 645), (190, 680), (150, 650)], 3).intersection(roof.buffer(-2))
    door = unary_union([box(430, 840, 570, 1070), circle(500, 840, 70)])
    win_l = soften(box(290, 690, 400, 800), 12); win_r = soften(box(600, 690, 710, 800), 12)
    parts = [Part(chimney, DARK, sil=False), Part(walls, GINGER), Part(roof, GINGER), Part(snow, 'white'),
             Part(door, RED, sil=False), Part(win_l, YELLOW, sil=False), Part(win_r, YELLOW, sil=False)]

    def details(c, sw):
        s = ''
        for (x0, x1) in ((290, 400), (600, 710)):
            xm = (x0 + x1) / 2
            s += f'<path d="M{xm},690 L{xm},800 M{x0},745 L{x1},745" stroke="{INK}" stroke-width="{sw * .6}"/>'
        s += f'<circle cx="540" cy="960" r="10" fill="{INK}"/>'
        for x, y, col in [(300, 900, RED), (700, 900, GREEN), (300, 1000, GREEN), (700, 1000, RED), (500, 470, RED)]:
            s += ring_dot(x, y, 24, c, col, sw)
        # icing zigzag under roof edge
        pts = ' '.join(f'{x},{608 if i % 2 else 590}' for i, x in enumerate(range(245, 770, 35)))
        return s
    return dict(parts=parts, details=details, dots=48, start=(230, 1070))

# ------------------------------------------------------------------ BUNNY
def bunny():
    head = circle(500, 470, 205)
    ear_l = capsule((420, 330), (335, 70), 120); ear_r = capsule((580, 330), (665, 70), 120)
    in_l = capsule((415, 300), (348, 110), 55); in_r = capsule((585, 300), (652, 110), 55)
    body = ellipse(500, 860, 230, 250)
    ft_l = ellipse(395, 1095, 95, 45); ft_r = ellipse(605, 1095, 95, 45)
    muff_l = circle(300, 450, 75); muff_r = circle(700, 450, 75)
    belly = ellipse(500, 900, 135, 165)
    parts = [Part(ear_l, CREAM), Part(ear_r, CREAM), Part(in_l, PINK, sil=False), Part(in_r, PINK, sil=False),
             Part(ft_l, CREAM), Part(ft_r, CREAM), Part(body, CREAM), Part(belly, 'white', sil=False, tex=lambda g: rings(g, 40, 2, 30), dash=True),
             Part(head, CREAM), Part(muff_l, RED, tex=lambda g: scallops(g, 34, 10)), Part(muff_r, RED, tex=lambda g: scallops(g, 34, 10))]

    def details(c, sw):
        s = f'<path d="M300,380 Q500,170 700,380" fill="none" stroke="{INK}" stroke-width="{sw * 2.4}" stroke-linecap="round"/>'
        if c:
            s += f'<path d="M300,380 Q500,170 700,380" fill="none" stroke="{RED}" stroke-width="{sw * 1.2}" stroke-linecap="round"/>'
        s += eye(430, 470, 22, sw) + eye(570, 470, 22, sw)
        s += f'<path d="M485,525 L515,525 L500,545 Z" fill="{PINK if c else INK}" stroke="{INK}" stroke-width="{sw * .5}" stroke-linejoin="round"/>'
        s += f'<path d="M500,545 Q480,575 460,560 M500,545 Q520,575 540,560" fill="none" stroke="{INK}" stroke-width="{sw * .7}" stroke-linecap="round"/>'
        s += cheek(395, 540, 28, 16, c, sw) + cheek(605, 540, 28, 16, c, sw)
        return s
    return dict(parts=parts, details=details, dots=52, start=(300, 1100))

# ------------------------------------------------------------------ HEDGEHOG
def hedgehog():
    cx, cy, rx, ry = 500, 680, 330, 300
    pts = []
    n = 5  # spikes over the top arc
    a0, a1 = 198, 342
    for i in range(361):
        a = i
        r_o = 1.0
        if a0 <= a <= a1:
            t = (a - a0) / (a1 - a0) * n
            r_o = 1.0 + 0.55 * (1 - abs((t % 1) - 0.5) * 2)
        elif 160 <= a < a0 or a1 < a <= 380 - 360 + 360 and a <= 360 and a > a1:
            r_o = 1.0
        rad = math.radians(a)
        pts.append((cx + rx * r_o * math.cos(rad), cy + ry * r_o * math.sin(rad)))
    spikes = Polygon(pts).buffer(0)
    face_g = ellipse(500, 760, 230, 190)
    ft_l = ellipse(400, 975, 80, 42); ft_r = ellipse(600, 975, 80, 42)
    hat = poly([(320, 590), (400, 420), (560, 380), (690, 470), (690, 590)], 25).intersection(Polygon([(0, 0), (1000, 0), (1000, 580), (0, 580)]))
    parts = [Part(ft_l, DARK), Part(ft_r, DARK), Part(spikes, BROWN, tex=lambda g: dashes(g.buffer(-30), 52, 46, 70)),
             Part(face_g, CREAM, sil=False)]

    def details(c, sw):
        s = eye(430, 730, 22, sw) + eye(570, 730, 22, sw)
        s += f'<ellipse cx="500" cy="790" rx="30" ry="22" fill="{INK}"/><ellipse cx="508" cy="782" rx="9" ry="5" fill="white"/>'
        s += smile(500, 825, 60, sw, 22) + cheek(375, 790, 28, 16, c, sw) + cheek(625, 790, 28, 16, c, sw)
        # apple on back
        s += fill_path(circle(500, 470, 55), RED if c else 'white', INK, sw * .8)
        s += f'<path d="M500,420 L505,385" stroke="{INK}" stroke-width="{sw * .8}" stroke-linecap="round"/>'
        s += fill_path(ellipse(530, 390, 28, 13, -20), GREEN if c else 'white', INK, sw * .6)
        return s
    return dict(parts=parts, details=details, dots=30, start=(330, 990))

CHARS2 = {'gift': gift, 'bell': bell, 'stocking': stocking, 'house': house, 'bunny': bunny, 'hedgehog': hedgehog}
