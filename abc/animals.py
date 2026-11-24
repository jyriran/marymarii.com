import sys, math
sys.path.insert(0, '/home/claude/xmas')
from engine import *
from chars import eye, cheek, smile, shape, CREAM, PINK, RED, YELLOW

GATOR = '#7DB66A'; GATOR_D = '#5E9450'; BELLY = '#E9E6B8'


def chaikin(pts, it=4):
    for _ in range(it):
        out = []
        for i in range(len(pts)):
            a, b = pts[i], pts[(i + 1) % len(pts)]
            out += [(a[0] * .75 + b[0] * .25, a[1] * .75 + b[1] * .25), (a[0] * .25 + b[0] * .75, a[1] * .25 + b[1] * .75)]
        pts = out
    return Polygon(pts)


# ------------------------------------------------------------------ ALLIGATOR (standing, 3/4 to the right)
def alligator():
    skull = circle(400, 330, 170)
    snout = soften(unary_union([capsule((420, 360), (800, 375), 190), circle(790, 360, 100)]), 30)
    bump_l = circle(330, 185, 72); bump_r = circle(475, 172, 72)
    head = soften(unary_union([skull, snout, bump_l, bump_r]), 25)
    body = ellipse(430, 760, 225, 280)
    tail = chaikin([(250, 900), (120, 980), (40, 1060), (60, 1110), (200, 1090), (330, 1040), (380, 930)])
    arm_l = capsule((250, 640), (150, 760), 95); arm_r = capsule((610, 640), (720, 720), 95)
    leg_l = capsule((340, 960), (320, 1070), 120); leg_r = capsule((530, 960), (560, 1070), 120)
    ft_l = ellipse(310, 1095, 95, 45); ft_r = ellipse(580, 1095, 95, 45)
    belly = ellipse(470, 790, 140, 215)
    neck = soften(box(300, 450, 580, 560), 40)
    spikes = unary_union([poly([(x - 34, y + 10), (x, y - 48), (x + 34, y + 10)], 10)
                          for x, y in [(105, 1010), (175, 975), (245, 935)]])
    parts = [Part(tail, GATOR), Part(spikes, GATOR_D, sil=False), Part(leg_l, GATOR), Part(leg_r, GATOR),
             Part(ft_l, GATOR_D), Part(ft_r, GATOR_D), Part(arm_l, GATOR), Part(neck, GATOR), Part(body, GATOR),
             Part(belly, BELLY, tex=lambda g: unary_union([LineString([(300, y), (640, y)]) for y in range(640, 1000, 55)]), sil=False),
             Part(arm_r, GATOR), Part(head, GATOR)]

    def details(c, sw):
        s = eye(330, 190, 30, sw) + eye(478, 178, 30, sw)
        # long smile along the snout + a few friendly teeth
        s += f'<path d="M300,430 Q560,500 860,410" fill="none" stroke="{INK}" stroke-width="{sw * .9}" stroke-linecap="round"/>'
        for x in (430, 520, 700):
            y = 430 + 0.0009 * (x - 580) ** 2 * -1 + (500 - 430) * (1 - ((x - 580) / 280) ** 2) * 0.62
            s += fill_path(poly([(x - 16, y - 2), (x + 16, y - 4), (x, y + 24)]), 'white', INK, sw * .6)
        s += f'<ellipse cx="830" cy="300" rx="13" ry="9" fill="{INK}"/><ellipse cx="780" cy="292" rx="13" ry="9" fill="{INK}"/>'
        s += cheek(330, 380, 34, 20, c, sw)
        # back scales on the head
        for x, y in ((560, 250), (640, 262), (720, 278)):
            s += f'<circle cx="{x}" cy="{y}" r="14" fill="none" stroke="{INK}" stroke-width="{sw * .6}"/>'
        # toes
        for fx in (285, 330, 555, 600):
            s += f'<path d="M{fx},1112 L{fx},1135" stroke="{INK}" stroke-width="{sw * .6}" stroke-linecap="round"/>'
        return s
    return dict(parts=parts, details=details, dots=36, start=(400, 110))



BROWN = '#B07A52'; BROWN_D = '#7E5536'; TAN = '#F0D6B5'; GREY = '#A9A9B4'; GREY_D = '#7C7C8A'; ORANGE = '#F2A253'
PINKY = '#F6B9B5'; BLUE = '#7FB7E0'; BLUE_D = '#4F8FC4'; GOLD = '#E9B949'; GOLD_D = '#C98A2E'; LILAC = '#C9A7E3'
HIPPO = '#9FA6C8'; HIPPO_D = '#7F86AA'; GIRAFFE = '#F2C66D'; SPOT = '#C8843F'


def nose(x, y, rx, ry):
    return (f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{INK}"/>'
            f'<ellipse cx="{x + rx * .3}" cy="{y - ry * .35}" rx="{rx * .3}" ry="{ry * .25}" fill="white"/>')


def chibi(head, body, arms, legs, feet, col, dark=None, belly=None, belly_col=None):
    """common upright body: legs, feet, body, (belly), arms. Returns parts (without head)."""
    out = [Part(l, col) for l in legs] + [Part(f, dark or col) for f in feet] + [Part(body, col)]
    if belly is not None: out.append(Part(belly, belly_col or CREAM, sil=False))
    return out + [Part(a, col) for a in arms]


# ------------------------------------------------------------------ BEAR
def bear():
    head = circle(500, 400, 250)
    ear_l = circle(300, 190, 90); ear_r = circle(700, 190, 90)
    in_l = circle(305, 200, 48); in_r = circle(695, 200, 48)
    body = ellipse(500, 860, 210, 230)
    belly = ellipse(500, 900, 130, 150)
    arms = [capsule((320, 760), (250, 900), 110), capsule((680, 760), (750, 900), 110)]
    legs = [capsule((420, 980), (410, 1060), 130), capsule((580, 980), (590, 1060), 130)]
    feet = [ellipse(400, 1085, 95, 50), ellipse(600, 1085, 95, 50)]
    muzzle = ellipse(500, 490, 115, 85)
    parts = [Part(ear_l, BROWN), Part(ear_r, BROWN), Part(in_l, TAN, sil=False), Part(in_r, TAN, sil=False)] + \
        chibi(head, body, arms, legs, feet, BROWN, BROWN_D, belly, TAN) + [Part(head, BROWN), Part(muzzle, TAN, sil=False)]

    def details(c, sw):
        return (eye(410, 380, 26, sw) + eye(590, 380, 26, sw) + nose(500, 455, 42, 28)
                + smile(470, 505, 60, sw, 22) + smile(530, 505, 60, sw, 22)
                + cheek(355, 470, 32, 19, c, sw) + cheek(645, 470, 32, 19, c, sw))
    return dict(parts=parts, details=details, dots=32, start=(500, 150))


# ------------------------------------------------------------------ CAT
def cat():
    head = ellipse(500, 420, 270, 225)
    ear_l = poly([(260, 380), (285, 110), (450, 230)], 30); ear_r = poly([(740, 380), (715, 110), (550, 230)], 30)
    in_l = poly([(300, 300), (310, 175), (400, 240)], 16); in_r = poly([(700, 300), (690, 175), (600, 240)], 16)
    body = ellipse(500, 860, 190, 220)
    tail = chaikin([(640, 960), (800, 950), (900, 860), (920, 720), (880, 640), (830, 660), (850, 760), (820, 860), (720, 890), (630, 880)])
    arms = [capsule((360, 760), (380, 930), 100), capsule((640, 760), (620, 930), 100)]
    legs = [capsule((420, 990), (415, 1060), 120), capsule((580, 990), (585, 1060), 120)]
    feet = [ellipse(405, 1085, 85, 45), ellipse(595, 1085, 85, 45)]
    belly = ellipse(500, 900, 110, 140)
    stripes = lambda g: unary_union([LineString([(x, 190), (x, 280)]) for x in (450, 500, 550)])
    parts = [Part(tail, ORANGE), Part(ear_l, ORANGE), Part(ear_r, ORANGE), Part(in_l, PINKY, sil=False), Part(in_r, PINKY, sil=False)] + \
        chibi(head, body, arms, legs, feet, ORANGE, None, belly, CREAM) + [Part(head, ORANGE, tex=stripes)]

    def details(c, sw):
        s = eye(400, 420, 28, sw) + eye(600, 420, 28, sw)
        s += fill_path(poly([(475, 480), (525, 480), (500, 510)], 8), PINKY if c else 'white', INK, sw * .7)
        s += smile(475, 515, 50, sw, 20) + smile(525, 515, 50, sw, 20)
        for dy in (-12, 18):
            s += f'<path d="M330,{500 + dy} L230,{490 + dy * 2}" stroke="{INK}" stroke-width="{sw * .6}" stroke-linecap="round"/>'
            s += f'<path d="M670,{500 + dy} L770,{490 + dy * 2}" stroke="{INK}" stroke-width="{sw * .6}" stroke-linecap="round"/>'
        return s + cheek(345, 480, 30, 18, c, sw) + cheek(655, 480, 30, 18, c, sw)
    return dict(parts=parts, details=details, dots=34, start=(285, 120))


# ------------------------------------------------------------------ DOG
def dog():
    head = ellipse(500, 400, 245, 225)
    ear_l = ellipse(270, 450, 85, 170, 18); ear_r = ellipse(730, 450, 85, 170, -18)
    body = ellipse(500, 845, 200, 235)
    tail = capsule((660, 900), (800, 760), 60)
    arms = [capsule((350, 760), (370, 930), 100), capsule((650, 760), (630, 930), 100)]
    legs = [capsule((420, 990), (415, 1060), 120), capsule((580, 990), (585, 1060), 120)]
    feet = [ellipse(405, 1085, 85, 45), ellipse(595, 1085, 85, 45)]
    muzzle = ellipse(500, 495, 120, 85)
    patch = ellipse(600, 370, 75, 70)
    collar = soften(box(330, 640, 670, 700), 20).intersection(unary_union([body, head]).buffer(-3))
    parts = [Part(tail, TAN), Part(ear_l, BROWN_D), Part(ear_r, BROWN_D)] + chibi(head, body, arms, legs, feet, TAN) + \
        [Part(head, TAN), Part(patch, BROWN, sil=False), Part(muzzle, 'white', sil=False), Part(collar, RED, sil=False)]

    def details(c, sw):
        s = eye(410, 380, 26, sw) + eye(600, 380, 26, sw) + nose(500, 465, 40, 28)
        s += fill_path(ellipse(500, 545, 30, 36), PINKY if c else 'white', INK, sw * .7)
        s += smile(470, 510, 60, sw, 20) + smile(530, 510, 60, sw, 20)
        s += fill_path(circle(500, 712, 22), GOLD if c else 'white', INK, sw * .6)
        return s
    return dict(parts=parts, details=details, dots=34, start=(500, 175))


# ------------------------------------------------------------------ ELEPHANT
def elephant():
    head = circle(500, 400, 230)
    ear_l = ellipse(250, 400, 170, 200, -10); ear_r = ellipse(750, 400, 170, 200, 10)
    in_l = ellipse(255, 410, 110, 140, -10); in_r = ellipse(745, 410, 110, 140, 10)
    trunk = chaikin([(450, 480), (550, 480), (560, 600), (590, 680), (660, 700), (690, 650), (720, 660), (700, 740), (620, 760), (520, 700), (460, 600)])
    body = ellipse(500, 860, 230, 210)
    legs = [capsule((390, 950), (390, 1050), 140), capsule((610, 950), (610, 1050), 140)]
    feet = [ellipse(390, 1085, 100, 42), ellipse(610, 1085, 100, 42)]
    arms = [capsule((310, 780), (290, 920), 105), capsule((690, 780), (710, 920), 105)]
    parts = [Part(ear_l, GREY), Part(ear_r, GREY), Part(in_l, PINKY, sil=False), Part(in_r, PINKY, sil=False)] + \
        chibi(head, body, arms, legs, feet, GREY, GREY_D) + [Part(head, GREY), Part(trunk, GREY)]

    def details(c, sw):
        s = eye(420, 380, 26, sw) + eye(580, 380, 26, sw) + cheek(380, 450, 28, 17, c, sw) + cheek(620, 450, 28, 17, c, sw)
        for y in (560, 610, 655):
            s += f'<path d="M{505 + (y - 560) * .5},{y} q25,8 45,0" fill="none" stroke="{INK}" stroke-width="{sw * .5}" stroke-linecap="round"/>'
        return s
    return dict(parts=parts, details=details, dots=36, start=(500, 170))



# ------------------------------------------------------------------ FISH (side view)
def fish():
    body = ellipse(560, 560, 320, 230)
    tail = poly([(290, 560), (70, 320), (150, 560), (70, 800)], 45)
    top = poly([(380, 420), (540, 160), (760, 400)], 45)
    bot = poly([(500, 740), (580, 880), (660, 750)], 30)
    side = ellipse(470, 640, 80, 48, -20)
    stripe = ellipse(620, 560, 30, 240).intersection(body.buffer(-8))
    tail_lines = lambda g: unary_union([LineString([(260, 560), (110, y)]) for y in (420, 560, 700)])
    parts = [Part(tail, BLUE_D, tex=tail_lines), Part(top, BLUE_D), Part(bot, BLUE_D),
             Part(body, BLUE, tex=lambda g: scallops(ellipse(520, 560, 230, 160), 55, 14)),
             Part(side, BLUE_D, sil=False)]

    def details(c, sw):
        s = fill_path(circle(760, 500, 62), 'white', INK, sw * .8) + eye(775, 500, 32, sw)
        s += smile(830, 615, 70, sw, 24) + cheek(745, 605, 30, 18, c, sw)
        return s
    return dict(parts=parts, details=details, dots=32, start=(470, 170))


# ------------------------------------------------------------------ GIRAFFE
def giraffe():
    head = ellipse(560, 270, 150, 115)
    snout = ellipse(660, 310, 110, 85)
    horns = unary_union([capsule((500, 180), (480, 70), 34), capsule((590, 175), (610, 65), 34), circle(480, 70, 30), circle(610, 65, 30)])
    ear_l = ellipse(400, 230, 70, 35, 20); ear_r = ellipse(705, 185, 60, 30, -30)
    neck = capsule((540, 330), (470, 720), 150)
    body = ellipse(430, 800, 250, 160)
    legs = [capsule((270, 880), (270, 1070), 75), capsule((380, 900), (380, 1080), 75),
            capsule((500, 900), (500, 1080), 75), capsule((600, 870), (610, 1070), 75)]
    hooves = [ellipse(x, 1090, 48, 28) for x in (270, 380, 500, 610)]
    tail = capsule((190, 780), (130, 900), 30)
    tuft = ellipse(125, 915, 30, 40)
    spots = lambda g: unary_union([ellipse(x, y, rx, ry, r) for x, y, rx, ry, r in
                                   [(470, 450, 35, 28, 20), (500, 580, 38, 30, -10), (450, 680, 34, 28, 15), (330, 760, 45, 35, 0),
                                    (450, 800, 42, 32, 20), (560, 760, 38, 30, -15), (300, 850, 35, 26, 10), (520, 870, 34, 25, 0)]])
    parts = [Part(tail, GIRAFFE), Part(tuft, SPOT, sil=False), Part(horns, SPOT)] + [Part(l, GIRAFFE) for l in legs] + \
            [Part(h, BROWN_D) for h in hooves] + [Part(body, GIRAFFE), Part(neck, GIRAFFE), Part(ear_l, GIRAFFE), Part(ear_r, GIRAFFE),
            Part(head, GIRAFFE), Part(snout, TAN)]

    def details(c, sw):
        s = ''
        for x, y, rx, ry, r in [(470, 450, 35, 28, 20), (500, 580, 38, 30, -10), (450, 680, 34, 28, 15), (330, 760, 45, 35, 0),
                                (450, 800, 42, 32, 20), (560, 760, 38, 30, -15), (300, 850, 35, 26, 10), (520, 870, 34, 25, 0), (520, 210, 26, 20, 0)]:
            s += fill_path(ellipse(x, y, rx, ry, r), SPOT if c else 'white', INK, sw * .6)
        s += eye(560, 250, 24, sw) + f'<ellipse cx="700" cy="300" rx="10" ry="7" fill="{INK}"/>' + smile(680, 345, 60, sw, 20)
        s += cheek(590, 320, 26, 16, c, sw)
        return s
    return dict(parts=parts, details=details, dots=38, start=(480, 40))


# ------------------------------------------------------------------ HIPPO
def hippo():
    head = ellipse(500, 380, 230, 200)
    snout = ellipse(500, 520, 260, 150)
    ear_l = circle(330, 220, 55); ear_r = circle(670, 220, 55)
    body = ellipse(500, 880, 260, 220)
    arms = [capsule((300, 800), (260, 930), 115), capsule((700, 800), (740, 930), 115)]
    legs = [capsule((380, 1000), (380, 1060), 140), capsule((620, 1000), (620, 1060), 140)]
    feet = [ellipse(380, 1090, 100, 40), ellipse(620, 1090, 100, 40)]
    belly = ellipse(500, 920, 150, 150)
    parts = [Part(ear_l, HIPPO), Part(ear_r, HIPPO)] + chibi(head, body, arms, legs, feet, HIPPO, HIPPO_D, belly, PINKY) + \
            [Part(head, HIPPO), Part(snout, HIPPO)]

    def details(c, sw):
        s = eye(420, 330, 26, sw) + eye(580, 330, 26, sw)
        s += f'<ellipse cx="430" cy="490" rx="22" ry="14" fill="{INK}"/><ellipse cx="570" cy="490" rx="22" ry="14" fill="{INK}"/>'
        s += smile(500, 580, 200, sw, 45) + cheek(320, 540, 34, 20, c, sw) + cheek(680, 540, 34, 20, c, sw)
        s += fill_path(circle(330, 220, 25), PINKY if c else 'white', INK, sw * .6) + fill_path(circle(670, 220, 25), PINKY if c else 'white', INK, sw * .6)
        return s
    return dict(parts=parts, details=details, dots=36, start=(500, 180))


# ------------------------------------------------------------------ IGUANA (side view, curly tail)
def iguana():
    body = ellipse(480, 640, 260, 140, -5)
    head = soften(unary_union([ellipse(800, 520, 170, 85, 8), circle(700, 510, 100)]), 30)
    neck = ellipse(680, 580, 110, 100)
    tail = chaikin([(250, 650), (120, 720), (60, 840), (100, 950), (220, 980), (300, 920), (280, 850), (220, 860), (200, 900),
                    (150, 890), (140, 820), (190, 760), (290, 730)])
    legs = [capsule((330, 720), (270, 860), 85), capsule((450, 740), (470, 880), 85),
            capsule((610, 700), (580, 850), 85), capsule((690, 680), (740, 830), 85)]
    feet = [ellipse(260, 880, 60, 30), ellipse(480, 900, 60, 30), ellipse(575, 870, 60, 30), ellipse(755, 850, 60, 30)]
    spikes = unary_union([poly([(x - 30, y + 15), (x, y - 50), (x + 30, y + 15)], 8)
                          for x, y in [(300, 525), (380, 505), (460, 500), (540, 505), (620, 470), (690, 425)]])
    dewlap = ellipse(720, 640, 60, 60)
    GREEN2 = '#8BC46A'; GREEN3 = '#5C9A45'
    parts = [Part(tail, GREEN2), Part(spikes, GREEN3)] + [Part(l, GREEN2) for l in legs] + [Part(f, GREEN3) for f in feet] + \
            [Part(body, GREEN2, tex=lambda g: unary_union([LineString([(x, 560), (x - 20, 720)]) for x in (360, 440, 520, 600)])),
             Part(dewlap, ORANGE), Part(neck, GREEN2), Part(head, GREEN2)]

    def details(c, sw):
        s = eye(780, 480, 28, sw) + smile(860, 570, 90, sw, 20) + cheek(760, 570, 28, 16, c, sw)
        s += f'<ellipse cx="910" cy="500" rx="9" ry="6" fill="{INK}"/>'
        return s
    return dict(parts=parts, details=details, dots=38, start=(690, 380))



# ------------------------------------------------------------------ JELLYFISH
def jellyfish():
    dome = unary_union([ellipse(500, 470, 330, 290).intersection(box(0, 0, 1000, 520)),
                        unary_union([circle(x, 515, 55) for x in (225, 335, 445, 555, 665, 775)])])
    dome = soften(dome, 20)
    def wavy(x0, y0, L, amp, ph, w):
        pts = [(x0 + amp * math.sin(ph + t * 0.018), y0 + t) for t in range(0, L, 20)]
        return LineString(pts).buffer(w / 2, resolution=12)
    tents = [wavy(x, 540, L, 32, ph, 62) for x, L, ph in ((300, 440, 0), (430, 520, 1.5), (570, 500, 3), (700, 420, 4.5))]
    parts = [Part(t, LILAC) for t in tents] + [Part(dome, PINKY, tex=lambda g: unary_union([circle(x, y, 22).exterior for x, y in ((330, 330), (680, 320), (420, 250), (600, 230), (260, 430), (740, 430))]))]

    def details(c, sw):
        return (eye(420, 420, 30, sw) + eye(580, 420, 30, sw) + smile(500, 470, 70, sw, 26)
                + cheek(360, 470, 32, 19, c, sw) + cheek(640, 470, 32, 19, c, sw))
    return dict(parts=parts, details=details, dots=36, start=(500, 180))


# ------------------------------------------------------------------ KOALA
def koala():
    head = ellipse(500, 400, 250, 220)
    ear_l = circle(270, 250, 120); ear_r = circle(730, 250, 120)
    in_l = circle(275, 260, 70); in_r = circle(725, 260, 70)
    body = ellipse(500, 840, 200, 235)
    arms = [capsule((350, 760), (370, 930), 100), capsule((650, 760), (630, 930), 100)]
    legs = [capsule((420, 990), (415, 1060), 120), capsule((580, 990), (585, 1060), 120)]
    feet = [ellipse(405, 1085, 85, 45), ellipse(595, 1085, 85, 45)]
    belly = ellipse(500, 890, 115, 140)
    parts = [Part(ear_l, GREY), Part(ear_r, GREY), Part(in_l, 'white', sil=False, tex=lambda g: dashes(g, 30, 22, 60)), Part(in_r, 'white', sil=False, tex=lambda g: dashes(g, 30, 22, 120))] + \
            chibi(head, body, arms, legs, feet, GREY, GREY_D, belly, '#E4E4EA') + [Part(head, GREY)]

    def details(c, sw):
        s = eye(400, 390, 26, sw) + eye(600, 390, 26, sw)
        s += fill_path(ellipse(500, 460, 55, 75), '#5A4E58' if c else 'white', INK, sw * .8)
        s += smile(500, 545, 60, sw, 18) + cheek(350, 470, 30, 18, c, sw) + cheek(650, 470, 30, 18, c, sw)
        return s
    return dict(parts=parts, details=details, dots=38, start=(270, 130))


# ------------------------------------------------------------------ LION
def lion():
    mane = soften(unary_union([circle(500 + 300 * math.cos(a), 400 + 290 * math.sin(a), 95) for a in [i * math.pi / 7 for i in range(14)]]
                              + [circle(500, 400, 300)]), 10)
    head = ellipse(500, 410, 215, 200)
    ear_l = circle(340, 240, 60); ear_r = circle(660, 240, 60)
    body = ellipse(500, 870, 200, 210)
    tail = unary_union([chaikin([(660, 980), (800, 990), (880, 900), (880, 800), (850, 790), (845, 890), (790, 950), (670, 950)]), circle(870, 780, 45)])
    arms = [capsule((360, 790), (370, 940), 100), capsule((640, 790), (630, 940), 100)]
    legs = [capsule((420, 990), (415, 1060), 120), capsule((580, 990), (585, 1060), 120)]
    feet = [ellipse(405, 1085, 85, 45), ellipse(595, 1085, 85, 45)]
    muzzle = ellipse(500, 490, 110, 80)
    parts = [Part(tail, GOLD), Part(mane, GOLD_D)] + chibi(None, body, arms, legs, feet, GOLD, None, ellipse(500, 910, 110, 130), CREAM) + \
            [Part(ear_l, GOLD), Part(ear_r, GOLD), Part(head, GOLD), Part(muzzle, CREAM, sil=False)]

    def details(c, sw):
        s = eye(420, 390, 26, sw) + eye(580, 390, 26, sw) + nose(500, 460, 40, 27)
        s += smile(470, 510, 60, sw, 20) + smile(530, 510, 60, sw, 20) + cheek(365, 470, 30, 18, c, sw) + cheek(635, 470, 30, 18, c, sw)
        s += fill_path(circle(340, 240, 28), PINKY if c else 'white', INK, sw * .6) + fill_path(circle(660, 240, 28), PINKY if c else 'white', INK, sw * .6)
        return s
    return dict(parts=parts, details=details, dots=42, start=(500, 15))


# ------------------------------------------------------------------ MOUSE
def mouse():
    head = soften(unary_union([circle(500, 430, 200), ellipse(500, 520, 130, 120)]), 30)
    ear_l = circle(310, 250, 135); ear_r = circle(690, 250, 135)
    in_l = circle(315, 255, 85); in_r = circle(685, 255, 85)
    body = ellipse(500, 840, 180, 230)
    tail = LineString([(640, 980), (760, 1010), (860, 960), (880, 860), (830, 800)]).buffer(22)
    arms = [capsule((370, 770), (390, 920), 90), capsule((630, 770), (610, 920), 90)]
    legs = [capsule((430, 990), (425, 1060), 110), capsule((570, 990), (575, 1060), 110)]
    feet = [ellipse(415, 1085, 85, 42), ellipse(585, 1085, 85, 42)]
    parts = [Part(tail, PINKY), Part(ear_l, GREY), Part(ear_r, GREY), Part(in_l, PINKY, sil=False), Part(in_r, PINKY, sil=False)] + \
            chibi(head, body, arms, legs, feet, GREY, PINKY, ellipse(500, 890, 100, 130), '#F3EDF0') + [Part(head, GREY)]

    def details(c, sw):
        s = eye(430, 430, 26, sw) + eye(570, 430, 26, sw) + nose(500, 545, 30, 22)
        s += smile(475, 585, 50, sw, 18) + smile(525, 585, 50, sw, 18) + cheek(390, 520, 28, 17, c, sw) + cheek(610, 520, 28, 17, c, sw)
        for dy in (-15, 15):
            s += f'<path d="M420,{560 + dy} L300,{545 + dy * 2.5}" stroke="{INK}" stroke-width="{sw * .55}" stroke-linecap="round"/>'
            s += f'<path d="M580,{560 + dy} L700,{545 + dy * 2.5}" stroke="{INK}" stroke-width="{sw * .55}" stroke-linecap="round"/>'
        return s
    return dict(parts=parts, details=details, dots=40, start=(310, 115))



DARK = '#5A4A40'
NAVY2 = '#5D7FB8'; SEA = '#9CC7E6'; PIGP = '#F4B3C2'; PIGD = '#E08AA0'; WHITE2 = '#F7F4EE'; YAKB = '#8A6448'; PURP = '#B79BE0'


def side_body(cx, cy, rx, ry):
    return ellipse(cx, cy, rx, ry)


# ------------------------------------------------------------------ NARWHAL
def narwhal():
    body = chaikin([(150, 600), (250, 430), (450, 360), (680, 380), (840, 470), (900, 600), (840, 720), (650, 780), (420, 770),
                    (250, 720), (130, 760), (60, 700), (90, 640)])
    tail = poly([(120, 660), (10, 560), (30, 680), (10, 800)], 25)
    tusk = poly([(820, 430), (1010, 250), (850, 470)], 6)
    fin = ellipse(500, 680, 70, 32, 25)
    belly = ellipse(640, 710, 180, 50).intersection(body.buffer(-6))
    parts = [Part(tail, NAVY2), Part(tusk, CREAM, tex=lambda g: unary_union([LineString([(840 + i * 30, 455 - i * 30), (860 + i * 30, 435 - i * 30)]) for i in range(6)])),
             Part(body, NAVY2), Part(belly, SEA, sil=False), Part(fin, '#4A6A9E', sil=False)]

    def details(c, sw):
        return eye(740, 520, 26, sw) + smile(780, 590, 60, sw, 20) + cheek(700, 590, 28, 16, c, sw) + \
            ''.join(f'<circle cx="{x}" cy="{y}" r="12" fill="none" stroke="{INK}" stroke-width="{sw * .5}"/>' for x, y in ((420, 480), (480, 450), (360, 520)))
    return dict(parts=parts, details=details, dots=34, start=(1000, 255))


# ------------------------------------------------------------------ OCTOPUS
def octopus():
    head = ellipse(500, 400, 260, 260)
    def leg(x0, ang, curl):
        pts = []
        for i in range(12):
            t = i / 11
            x = x0 + math.sin(ang) * 330 * t + curl * 90 * math.sin(t * math.pi)
            y = 560 + 380 * t
            pts.append((x, y))
        return LineString(pts).buffer(58, resolution=10).union(circle(*pts[-1], 52))
    legs = [leg(x, a, cv) for x, a, cv in ((320, -.45, .6), (410, -.18, -.6), (500, 0, .6), (590, .18, -.6), (680, .45, .6))]
    parts = [Part(l, PURP, tex=lambda g: LineString()) for l in legs] + [Part(head, PURP, tex=lambda g: unary_union([circle(x, y, 22).exterior for x, y in ((380, 230), (600, 220), (480, 180), (700, 330))]))]

    def details(c, sw):
        return eye(420, 430, 32, sw) + eye(580, 430, 32, sw) + smile(500, 500, 80, sw, 30) + cheek(350, 500, 34, 20, c, sw) + cheek(650, 500, 34, 20, c, sw)
    return dict(parts=parts, details=details, dots=40, start=(500, 140))


# ------------------------------------------------------------------ PIG
def pig():
    head = ellipse(500, 420, 260, 220)
    ear_l = poly([(290, 310), (300, 110), (450, 240)], 25); ear_r = poly([(710, 310), (700, 110), (550, 240)], 25)
    snout = ellipse(500, 500, 100, 70)
    body = ellipse(500, 860, 210, 235)
    tail = LineString([(690, 900), (760, 880), (770, 830), (730, 820), (740, 780)]).buffer(16)
    arms = [capsule((340, 780), (320, 930), 100), capsule((660, 780), (680, 930), 100)]
    legs = [capsule((420, 990), (415, 1060), 120), capsule((580, 990), (585, 1060), 120)]
    feet = [ellipse(405, 1085, 85, 45), ellipse(595, 1085, 85, 45)]
    parts = [Part(tail, PIGD, sil=False), Part(ear_l, PIGP), Part(ear_r, PIGP)] + chibi(None, body, arms, legs, feet, PIGP, PIGD, ellipse(500, 900, 120, 140), '#F9D3DC') + \
            [Part(head, PIGP), Part(snout, PIGD, sil=False)]

    def details(c, sw):
        return (eye(410, 400, 26, sw) + eye(590, 400, 26, sw) + f'<ellipse cx="470" cy="500" rx="15" ry="22" fill="{INK}"/><ellipse cx="530" cy="500" rx="15" ry="22" fill="{INK}"/>'
                + smile(500, 590, 80, sw, 22) + cheek(350, 490, 30, 18, c, sw) + cheek(650, 490, 30, 18, c, sw))
    return dict(parts=parts, details=details, dots=36, start=(300, 110))


# ------------------------------------------------------------------ QUAIL
def quail():
    body = ellipse(500, 680, 330, 280)
    head = circle(560, 360, 190)
    plume = unary_union([capsule((560, 180), (610, 60), 34), circle(625, 55, 40)])
    tail = poly([(200, 640), (60, 560), (110, 700)], 20)
    wing = ellipse(420, 700, 190, 130, -10)
    legs = [capsule((440, 940), (430, 1060), 34), capsule((580, 940), (590, 1060), 34)]
    feet = [poly([(380, 1080), (480, 1080), (430, 1050)], 8), poly([(540, 1080), (640, 1080), (590, 1050)], 8)]
    beak = poly([(730, 360), (800, 390), (730, 410)], 8)
    BRW = '#C29A6B'
    parts = [Part(plume, BROWN_D), Part(tail, BRW)] + [Part(l, ORANGE) for l in legs] + [Part(f, ORANGE) for f in feet] + \
            [Part(body, BRW, tex=lambda g: dashes(ellipse(560, 760, 200, 150), 46, 26, 70)), Part(beak, ORANGE), Part(head, BRW),
             Part(wing, BROWN, sil=False, tex=lambda g: unary_union([LineString([(300, y), (520, y + 20)]) for y in (660, 710, 760)]))]

    def details(c, sw):
        return eye(620, 340, 26, sw) + cheek(600, 420, 28, 17, c, sw)
    return dict(parts=parts, details=details, dots=36, start=(625, 15))


# ------------------------------------------------------------------ RABBIT
def rabbit():
    head = ellipse(500, 450, 230, 200)
    ear_l = ellipse(400, 170, 70, 200, -8); ear_r = ellipse(600, 170, 70, 200, 8)
    in_l = ellipse(400, 180, 35, 150, -8); in_r = ellipse(600, 180, 35, 150, 8)
    body = ellipse(500, 860, 195, 225)
    tail = circle(690, 950, 60)
    arms = [capsule((350, 780), (370, 930), 95), capsule((650, 780), (630, 930), 95)]
    legs = [capsule((420, 990), (415, 1060), 120), capsule((580, 990), (585, 1060), 120)]
    feet = [ellipse(400, 1085, 100, 45), ellipse(600, 1085, 100, 45)]
    parts = [Part(tail, 'white'), Part(ear_l, WHITE2), Part(ear_r, WHITE2), Part(in_l, PINKY, sil=False), Part(in_r, PINKY, sil=False)] + \
            chibi(None, body, arms, legs, feet, WHITE2, None, ellipse(500, 900, 110, 140), 'white') + [Part(head, WHITE2)]

    def details(c, sw):
        s = eye(420, 450, 26, sw) + eye(580, 450, 26, sw) + fill_path(poly([(475, 510), (525, 510), (500, 540)], 8), PINKY if c else 'white', INK, sw * .7)
        s += smile(475, 550, 50, sw, 18) + smile(525, 550, 50, sw, 18) + cheek(360, 520, 30, 18, c, sw) + cheek(640, 520, 30, 18, c, sw)
        s += fill_path(soften(box(470, 560, 530, 610), 6), 'white', INK, sw * .5)
        return s
    return dict(parts=parts, details=details, dots=38, start=(400, -30))


# ------------------------------------------------------------------ SNAKE
def snake():
    pts = [(120, 1000), (300, 1060), (520, 1030), (650, 930), (560, 820), (360, 780), (300, 660), (430, 560), (620, 540), (720, 430), (650, 330)]
    body = LineString(pts).buffer(70, resolution=16)
    from shapely.ops import unary_union as uu
    body = soften(body, 30)
    head = ellipse(640, 270, 140, 105, -10)
    tongue = poly([(760, 300), (850, 320), (880, 300), (860, 330), (880, 350), (850, 340), (760, 320)], 2)
    stripes = lambda g: unary_union([LineString(pts).parallel_offset(0, 'left').interpolate(d).buffer(26).exterior for d in range(80, 1900, 140)])
    parts = [Part(tongue, RED, sil=False), Part(body, '#7CC36A', tex=stripes), Part(head, '#7CC36A')]

    def details(c, sw):
        return eye(600, 245, 26, sw) + eye(700, 245, 26, sw) + smile(660, 320, 80, sw, 24) + cheek(560, 310, 26, 16, c, sw) + cheek(740, 300, 26, 16, c, sw)
    return dict(parts=parts, details=details, dots=36, start=(640, 160))


# ------------------------------------------------------------------ TURTLE
def turtle():
    shell = ellipse(480, 640, 320, 250).intersection(box(0, 0, 1000, 690))
    rim = ellipse(480, 690, 340, 45)
    head = circle(850, 580, 105)
    neck = capsule((740, 680), (830, 620), 110)
    legs = [ellipse(290, 745, 65, 55), ellipse(660, 745, 65, 55)]
    tail = poly([(170, 690), (90, 700), (170, 720)], 10)
    TG = '#86C27A'; SH = '#C99B5B'
    hexes = lambda g: unary_union([circle(x, y, 52).exterior for x, y in ((480, 500), (350, 590), (610, 590), (480, 625))])
    parts = [Part(tail, TG)] + [Part(l, TG) for l in legs] + [Part(neck, TG), Part(head, TG), Part(rim, '#A87B44'), Part(shell, SH, tex=hexes)]

    def details(c, sw):
        return eye(875, 555, 24, sw) + smile(880, 620, 50, sw, 18) + cheek(830, 615, 24, 14, c, sw)
    return dict(parts=parts, details=details, dots=34, start=(480, 370))


# ------------------------------------------------------------------ UNICORN
def unicorn():
    head = ellipse(560, 360, 180, 150)
    snout = ellipse(680, 420, 120, 95)
    horn = poly([(520, 240), (590, 40), (610, 245)], 10)
    ear = poly([(450, 250), (440, 140), (520, 220)], 12)
    neck = capsule((520, 420), (440, 650), 190)
    body = ellipse(420, 760, 270, 170)
    legs = [capsule(p, (p[0], 1050), 85) for p in ((250, 840), (360, 860), (500, 860), (610, 840))]
    hooves = [ellipse(x, 1070, 50, 28) for x in (250, 360, 500, 610)]
    mane = chaikin([(470, 210), (380, 260), (330, 400), (320, 560), (370, 640), (420, 560), (430, 420), (500, 300)])
    tail = chaikin([(160, 720), (60, 780), (40, 920), (110, 960), (150, 860), (200, 780)])
    WH = '#FBF7FF'; MANE = '#E6A3D9'
    parts = [Part(tail, MANE)] + [Part(l, WH) for l in legs] + [Part(h, LILAC) for h in hooves] + [Part(body, WH), Part(neck, WH), Part(ear, WH), Part(head, WH),
             Part(snout, WH), Part(horn, GOLD, tex=lambda g: unary_union([LineString([(545, y), (600, y - 20)]) for y in (200, 150, 100)])), Part(mane, MANE, sil=False)]

    def details(c, sw):
        return eye(600, 350, 24, sw) + cheek(650, 420, 28, 16, c, sw) + smile(720, 460, 50, sw, 16) + f'<ellipse cx="750" cy="400" rx="9" ry="6" fill="{INK}"/>'
    return dict(parts=parts, details=details, dots=40, start=(590, 30))


# ------------------------------------------------------------------ VULTURE (cute, bald)
def vulture():
    body = ellipse(500, 760, 230, 270)
    wing_l = ellipse(280, 760, 110, 230, 12); wing_r = ellipse(720, 760, 110, 230, -12)
    neck = capsule((500, 560), (500, 420), 120)
    ruff = ellipse(500, 520, 200, 80)
    head = circle(500, 320, 150)
    beak = poly([(470, 360), (530, 360), (520, 440), (500, 460)], 10)
    legs = [capsule((440, 1000), (430, 1070), 40), capsule((560, 1000), (570, 1070), 40)]
    feet = [poly([(380, 1090), (480, 1090), (430, 1055)], 8), poly([(520, 1090), (620, 1090), (570, 1055)], 8)]
    DK = '#6E5D59'
    parts = [Part(l, ORANGE) for l in legs] + [Part(f, ORANGE) for f in feet] + [Part(wing_l, DK), Part(wing_r, DK), Part(body, DK, tex=lambda g: dashes(ellipse(500, 820, 140, 160), 46, 26, 80)),
             Part(neck, PINKY), Part(ruff, WHITE2, tex=lambda g: scallops(g, 46, 12)), Part(head, PINKY), Part(beak, GOLD)]

    def details(c, sw):
        return eye(445, 300, 28, sw) + eye(555, 300, 28, sw) + cheek(400, 360, 26, 16, c, sw) + cheek(600, 360, 26, 16, c, sw)
    return dict(parts=parts, details=details, dots=38, start=(500, 170))


# ------------------------------------------------------------------ WHALE
def whale():
    body = chaikin([(140, 560), (260, 380), (500, 320), (760, 360), (900, 500), (900, 640), (780, 760), (520, 790), (300, 760), (160, 700)])
    tail = unary_union([poly([(220, 590), (20, 380), (110, 600)], 30), poly([(220, 610), (20, 800), (110, 600)], 30)])
    belly = ellipse(600, 740, 260, 90).intersection(body.buffer(-6))
    spout = unary_union([capsule((600, 300), (600, 200), 30), circle(560, 180, 40), circle(640, 180, 40), circle(600, 150, 40)])
    fin = ellipse(520, 690, 90, 40, 20)
    parts = [Part(tail, BLUE_D), Part(spout, SEA, sil=False), Part(body, BLUE_D), Part(belly, SEA, sil=False, tex=lambda g: unary_union([LineString([(420, y), (800, y)]) for y in (700, 740, 780)])), Part(fin, '#3E78AE', sil=False)]

    def details(c, sw):
        return eye(760, 520, 28, sw) + smile(800, 600, 70, sw, 22) + cheek(720, 590, 30, 17, c, sw)
    return dict(parts=parts, details=details, dots=34, start=(500, 320))


# ------------------------------------------------------------------ X-RAY FISH
def xrayfish():
    body = ellipse(540, 560, 330, 200)
    tail = poly([(260, 560), (60, 360), (120, 560), (60, 760)], 40)
    top = poly([(420, 410), (520, 260), (680, 380)], 30)
    bot = poly([(440, 710), (520, 840), (640, 730)], 30)
    parts = [Part(tail, '#BDE3EE'), Part(top, '#BDE3EE'), Part(bot, '#BDE3EE'), Part(body, '#DDF2F7')]

    def details(c, sw):
        s = f'<path d="M300,560 L780,560" stroke="{INK}" stroke-width="{sw * .9}" stroke-linecap="round"/>'
        for x in range(360, 760, 55):
            h = 120 * math.sqrt(max(0, 1 - ((x - 560) / 260) ** 2)) + 20
            s += f'<path d="M{x},{560 - h} Q{x + 22},560 {x},{560 + h}" fill="none" stroke="{INK}" stroke-width="{sw * .6}" stroke-linecap="round"/>'
        s += fill_path(ellipse(520, 600, 70, 45), '#F2B04E' if c else 'white', INK, sw * .6)
        s += fill_path(circle(770, 500, 55), 'white', INK, sw * .8) + eye(782, 500, 30, sw) + smile(830, 610, 55, sw, 20)
        return s
    return dict(parts=parts, details=details, dots=32, start=(520, 260))


# ------------------------------------------------------------------ YAK
def yak():
    body = ellipse(470, 760, 300, 210)
    hair = chaikin([(180, 740), (210, 960), (260, 900), (300, 980), (350, 910), (400, 990), (450, 920), (510, 990), (560, 920), (620, 990), (670, 910), (740, 960), (770, 740)])
    head = ellipse(740, 470, 170, 150)
    horns = unary_union([LineString([(640, 400), (560, 380), (540, 300)]).buffer(30), LineString([(840, 400), (920, 380), (940, 300)]).buffer(30)])
    fringe = chaikin([(600, 420), (650, 340), (760, 320), (870, 350), (900, 430), (850, 470), (800, 430), (750, 470), (700, 430), (650, 470)])
    legs = [capsule((p, 900), (p, 1060), 80) for p in (280, 400, 560, 660)]
    hooves = [ellipse(x, 1075, 50, 28) for x in (280, 400, 560, 660)]
    tail = capsule((180, 720), (110, 840), 50)
    parts = [Part(horns, CREAM), Part(tail, YAKB)] + [Part(l, YAKB) for l in legs] + [Part(h, DARK) for h in hooves] + \
            [Part(body, YAKB), Part(hair, '#9C7556', tex=lambda g: unary_union([LineString([(x, 800), (x - 10, 940)]) for x in range(260, 760, 60)])), Part(head, YAKB), Part(fringe, '#6E4B33', sil=False)]

    def details(c, sw):
        return eye(700, 480, 24, sw) + eye(800, 480, 24, sw) + fill_path(ellipse(750, 560, 80, 50), TAN if c else 'white', INK, sw * .6) + \
            f'<ellipse cx="725" cy="555" rx="11" ry="8" fill="{INK}"/><ellipse cx="775" cy="555" rx="11" ry="8" fill="{INK}"/>' + cheek(650, 530, 26, 15, c, sw) + cheek(850, 530, 26, 15, c, sw)
    return dict(parts=parts, details=details, dots=40, start=(540, 290))


# ------------------------------------------------------------------ ZEBRA
def zebra():
    head = ellipse(560, 330, 170, 140)
    snout = ellipse(680, 400, 115, 90)
    ears = unary_union([poly([(450, 230), (430, 110), (510, 200)], 12), poly([(560, 200), (590, 90), (620, 210)], 12)])
    neck = capsule((520, 400), (440, 640), 190)
    body = ellipse(420, 760, 270, 170)
    legs = [capsule(p, (p[0], 1050), 85) for p in ((250, 840), (360, 860), (500, 860), (610, 840))]
    hooves = [ellipse(x, 1070, 50, 28) for x in (250, 360, 500, 610)]
    mane = chaikin([(470, 220), (420, 260), (370, 400), (330, 560), (380, 560), (420, 420), (480, 290)])
    tail = capsule((160, 740), (110, 880), 30).union(ellipse(105, 900, 30, 45))
    stripes = lambda g: unary_union([LineString([(x, 560), (x + 30, 960)]).buffer(18) for x in range(200, 700, 80)]).exterior if False else \
        unary_union([LineString([(x - 40, 580), (x + 20, 940)]) for x in range(220, 720, 70)])
    parts = [Part(tail, WHITE2)] + [Part(l, WHITE2) for l in legs] + [Part(h, DARK) for h in hooves] + [Part(body, WHITE2, tex=stripes), Part(mane, '#3A3A3A', sil=False), Part(neck, WHITE2, tex=lambda g: unary_union([LineString([(380, y), (560, y + 30)]) for y in (460, 530, 600)])),
             Part(ears, WHITE2), Part(head, WHITE2, tex=lambda g: unary_union([LineString([(460, y), (620, y - 20)]) for y in (300, 350)])), Part(snout, '#9A9A9A')]

    def details(c, sw):
        return eye(600, 320, 24, sw) + cheek(640, 390, 26, 15, c, sw) + smile(720, 445, 50, sw, 16) + f'<ellipse cx="750" cy="385" rx="9" ry="6" fill="{INK}"/>'
    return dict(parts=parts, details=details, dots=40, start=(590, 80))


ANIMALS = {'alligator': alligator, 'bear': bear, 'cat': cat, 'dog': dog, 'elephant': elephant,
           'fish': fish, 'giraffe': giraffe, 'hippo': hippo, 'iguana': iguana,
           'jellyfish': jellyfish, 'koala': koala, 'lion': lion, 'mouse': mouse,
           'narwhal': narwhal, 'octopus': octopus, 'pig': pig, 'quail': quail, 'rabbit': rabbit, 'snake': snake, 'turtle': turtle,
           'unicorn': unicorn, 'vulture': vulture, 'whale': whale, 'xrayfish': xrayfish, 'yak': yak, 'zebra': zebra}
