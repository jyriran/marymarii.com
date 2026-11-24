"""Animals for 123 Count & Connect (procedural, same house style as the ABC animals)."""
import sys, math
sys.path.insert(0, '/home/claude/xmas'); sys.path.insert(0, '/home/claude/abc')
from engine import *
from chars import eye, cheek, smile, CREAM, PINK, RED, YELLOW
from animals import chaikin, nose, chibi, BROWN, BROWN_D, TAN, GREY, GREY_D, ORANGE, PINKY, BLUE, BLUE_D, GOLD, GOLD_D, LILAC

FROG = '#86C46A'; FROG_D = '#5E9E4A'; FROG_B = '#E6F0B6'


def frog():
    head = soften(unary_union([ellipse(500, 430, 300, 190), circle(345, 270, 105), circle(655, 270, 105)]), 30)
    body = ellipse(500, 790, 240, 250)
    belly = ellipse(500, 830, 150, 180)
    thigh_l = ellipse(285, 930, 130, 110, 25); thigh_r = ellipse(715, 930, 130, 110, -25)
    foot_l = poly([(150, 1080), (230, 1010), (330, 1040), (300, 1095), (240, 1080), (200, 1110)], 22)
    foot_r = poly([(850, 1080), (770, 1010), (670, 1040), (700, 1095), (760, 1080), (800, 1110)], 22)
    arm_l = capsule((370, 700), (390, 960), 95); arm_r = capsule((630, 700), (610, 960), 95)
    hand_l = ellipse(385, 985, 70, 35); hand_r = ellipse(615, 985, 70, 35)
    parts = [Part(thigh_l, FROG_D), Part(thigh_r, FROG_D), Part(foot_l, FROG_D), Part(foot_r, FROG_D), Part(body, FROG),
             Part(belly, FROG_B, sil=False), Part(arm_l, FROG), Part(arm_r, FROG), Part(hand_l, FROG_D), Part(hand_r, FROG_D),
             Part(head, FROG)]

    def details(c, sw):
        s = fill_path(circle(345, 265, 70), 'white', INK, sw * .8) + fill_path(circle(655, 265, 70), 'white', INK, sw * .8)
        s += eye(355, 275, 34, sw) + eye(645, 275, 34, sw)
        s += f'<path d="M330,470 Q500,590 670,470" fill="none" stroke="{INK}" stroke-width="{sw}" stroke-linecap="round"/>'
        s += cheek(285, 440, 38, 22, c, sw) + cheek(715, 440, 38, 22, c, sw)
        s += f'<ellipse cx="470" cy="400" rx="9" ry="6" fill="{INK}"/><ellipse cx="530" cy="400" rx="9" ry="6" fill="{INK}"/>'
        for x in (440, 500, 560):
            s += f'<circle cx="{x}" cy="{760 + (x - 500) ** 2 * .002}" r="16" fill="none" stroke="{INK}" stroke-width="{sw * .5}"/>'
        return s
    return dict(parts=parts, details=details, dots=34, start=(345, 160))


GREEN = '#9CCB6B'; GREEN_D = '#6FA34A'; DUCKY = '#F6D35B'; BEAK = '#F29A45'; CRAB = '#E86B55'; CRAB_D = '#C24E3B'
LADY = '#E2493B'; BLACKISH = '#3A3236'; BEE = '#F4C542'; WING = '#DDEFF8'; SNAIL = '#E9C88E'; SHELL = '#C98B5A'
PANDA_W = '#FFFFFF'; PANDA_K = '#3A3236'; MONKEY = '#A8754E'; MONKEY_L = '#EBC9A2'; COWW = '#FFFFFF'; SPOTC = '#5A4A48'
WOOL = '#F4F1EA'; SHEEPF = '#6E6466'; CHICK = '#F9DC5C'; BFLY = '#B48FE0'; BFLY_2 = '#F4A9C8'; DOLPH = '#7FB3D9'; DOLPH_L = '#D8EAF5'
SEAL = '#A9B4BF'; SEAL_L = '#DDE3E8'; FLAM = '#F3A3B6'; FLAM_D = '#E17C95'; SQ = '#D98A4A'; SQ_L = '#F2D3AE'
PARROT = '#4FB477'; PARROT_R = '#E5543F'; PARROT_Y = '#F4C542'; TIGER = '#F2A04A'; TIGER_L = '#FBE6C8'; DRAGON = '#7CC4A4'; DRAGON_D = '#4E9C7C'


def dino():
    head = ellipse(640, 330, 210, 170)
    neck = capsule((560, 420), (480, 640), 190)
    body = ellipse(450, 790, 260, 220)
    tail = chaikin([(250, 760), (120, 800), (20, 900), (60, 930), (200, 900), (300, 900)])
    legs = [capsule((340, 920), (330, 1060), 130), capsule((560, 920), (570, 1060), 130)]
    feet = [ellipse(325, 1085, 90, 42), ellipse(580, 1085, 90, 42)]
    arm = capsule((600, 720), (690, 800), 70)
    belly = ellipse(500, 820, 150, 150)
    plates = unary_union([poly([(x - 40, y + 20), (x, y - 50), (x + 40, y + 20)], 12) for x, y in ((470, 470), (400, 590), (320, 690), (220, 760))])
    parts = [Part(tail, GREEN), Part(plates, GREEN_D), Part(legs[0], GREEN), Part(legs[1], GREEN), Part(feet[0], GREEN_D), Part(feet[1], GREEN_D),
             Part(body, GREEN), Part(belly, '#E8F2C8', sil=False), Part(neck, GREEN), Part(arm, GREEN), Part(head, GREEN)]
    def details(c, sw):
        return (eye(680, 300, 30, sw) + smile(720, 385, 90, sw, 25) + cheek(610, 370, 34, 20, c, sw)
                + f'<ellipse cx="800" cy="300" rx="10" ry="7" fill="{INK}"/>')
    return dict(parts=parts, details=details, dots=34, start=(640, 160))


def duck():
    head = circle(520, 340, 200)
    beak = ellipse(720, 400, 130, 60)
    body = ellipse(480, 790, 300, 230)
    tailf = poly([(200, 700), (110, 600), (230, 640), (250, 720)], 20)
    wing = ellipse(430, 780, 170, 110, -15)
    legs = [capsule((420, 1000), (420, 1060), 40), capsule((560, 1000), (560, 1060), 40)]
    feet = [poly([(350, 1100), (420, 1050), (490, 1100)], 15), poly([(490, 1100), (560, 1050), (630, 1100)], 15)]
    neck = capsule((520, 500), (500, 600), 200)
    parts = [Part(legs[0], BEAK), Part(legs[1], BEAK), Part(feet[0], BEAK), Part(feet[1], BEAK), Part(tailf, DUCKY), Part(body, DUCKY),
             Part(wing, '#EFC04A', sil=False), Part(neck, DUCKY), Part(head, DUCKY), Part(beak, BEAK)]
    def details(c, sw):
        return (eye(560, 300, 30, sw) + cheek(500, 400, 32, 19, c, sw) + f'<path d="M600,400 Q720,420 840,395" fill="none" stroke="{INK}" stroke-width="{sw * .7}"/>')
    return dict(parts=parts, details=details, dots=32, start=(520, 140))


def crab():
    body = ellipse(500, 640, 330, 220)
    eyes = [capsule((400, 420), (390, 300), 40), capsule((600, 420), (610, 300), 40)]
    balls = [circle(390, 280, 60), circle(610, 280, 60)]
    claws = [poly([(120, 360), (230, 300), (260, 430), (170, 470), (90, 440)], 40), poly([(880, 360), (770, 300), (740, 430), (830, 470), (910, 440)], 40)]
    arms = [capsule((220, 600), (180, 450), 70), capsule((780, 600), (820, 450), 70)]
    legs = [capsule((260 - i * 20, 760 + i * 70), (110 - i * 10, 850 + i * 80), 50) for i in range(3)] + \
           [capsule((740 + i * 20, 760 + i * 70), (890 + i * 10, 850 + i * 80), 50) for i in range(3)]
    parts = [Part(l, CRAB_D) for l in legs] + [Part(a, CRAB) for a in arms] + [Part(cl, CRAB) for cl in claws] + \
            [Part(e, CRAB) for e in eyes] + [Part(body, CRAB)] + [Part(b, 'white') for b in balls]
    def details(c, sw):
        s = eye(395, 290, 28, sw) + eye(605, 290, 28, sw) + smile(500, 680, 120, sw, 35)
        s += cheek(380, 640, 34, 20, c, sw) + cheek(620, 640, 34, 20, c, sw)
        s += f'<path d="M150,400 L230,370" stroke="{INK}" stroke-width="{sw * .7}"/><path d="M850,400 L770,370" stroke="{INK}" stroke-width="{sw * .7}"/>'
        return s
    return dict(parts=parts, details=details, dots=40, start=(390, 210))


def ladybug():
    shell = ellipse(500, 650, 330, 360)
    head = ellipse(500, 300, 200, 150)
    split = LineString([(500, 330), (500, 1010)])
    spots = unary_union([circle(x, y, r) for x, y, r in ((380, 540, 55), (620, 540, 55), (360, 760, 60), (640, 760, 60), (500, 890, 45), (420, 650, 30), (580, 650, 30))]).intersection(shell)
    ant = [capsule((440, 180), (380, 70), 18), capsule((560, 180), (620, 70), 18)]
    knobs = [circle(375, 65, 32), circle(625, 65, 32)]
    legs = [capsule((230 + i * 20 * (i == 2), 520 + i * 160), (90, 560 + i * 170), 40) for i in range(3)] + [capsule((770 - i * 20 * (i == 2), 520 + i * 160), (910, 560 + i * 170), 40) for i in range(3)]
    parts = [Part(l, BLACKISH) for l in legs] + [Part(a, BLACKISH) for a in ant] + [Part(k, BLACKISH) for k in knobs] + \
            [Part(shell, LADY, tex=lambda g: split), Part(spots, BLACKISH, sil=False), Part(head, BLACKISH)]
    def details(c, sw):
        s = fill_path(circle(430, 290, 42), 'white', INK, sw * .7) + fill_path(circle(570, 290, 42), 'white', INK, sw * .7)
        s += eye(435, 295, 24, sw) + eye(565, 295, 24, sw)
        s += f'<path d="M455,360 Q500,395 545,360" fill="none" stroke="white" stroke-width="{sw}" stroke-linecap="round"/>'
        return s
    return dict(parts=parts, details=details, dots=40, start=(500, 170))


def bee():
    body = ellipse(500, 700, 260, 300)
    head = circle(500, 330, 190)
    wings = [ellipse(250, 520, 150, 100, -30), ellipse(750, 520, 150, 100, 30)]
    stinger = poly([(470, 990), (530, 990), (500, 1080)], 10)
    ant = [capsule((440, 170), (390, 70), 18), capsule((560, 170), (610, 70), 18)]
    knobs = [circle(385, 62, 30), circle(615, 62, 30)]
    stripes = lambda g: unary_union([box(200, y, 800, y + 70) for y in (590, 740, 890)]).intersection(g.buffer(-2))
    arms = [capsule((290, 680), (200, 760), 60), capsule((710, 680), (800, 760), 60)]
    parts = [Part(w, WING) for w in wings] + [Part(stinger, BLACKISH)] + [Part(a, BLACKISH) for a in ant] + [Part(k, BLACKISH) for k in knobs] + \
            [Part(a, BEE) for a in arms] + [Part(body, BEE), Part(stripes(body), BLACKISH, sil=False), Part(head, BEE)]
    def details(c, sw):
        return eye(430, 320, 28, sw) + eye(570, 320, 28, sw) + smile(500, 390, 70, sw, 24) + cheek(390, 390, 32, 19, c, sw) + cheek(610, 390, 32, 19, c, sw)
    return dict(parts=parts, details=details, dots=38, start=(500, 140))


def snail():
    foot = soften(unary_union([ellipse(520, 930, 400, 90), capsule((820, 900), (840, 560), 150)]), 30)
    head = circle(840, 500, 140)
    shell = circle(470, 650, 270)
    spiral = lambda g: LineString([(470 + math.cos(t) * (230 - t * 25), 650 + math.sin(t) * (230 - t * 25)) for t in [i * .15 for i in range(55)]])
    ant = [capsule((800, 380), (760, 250), 22), capsule((880, 380), (920, 250), 22)]
    knobs = [circle(755, 240, 30), circle(925, 240, 30)]
    parts = [Part(a, SNAIL) for a in ant] + [Part(k, SNAIL) for k in knobs] + [Part(foot, SNAIL), Part(head, SNAIL), Part(shell, SHELL, tex=spiral)]
    def details(c, sw):
        return eye(800, 490, 26, sw) + eye(890, 490, 26, sw) + smile(845, 560, 60, sw, 20) + cheek(780, 560, 26, 16, c, sw)
    return dict(parts=parts, details=details, dots=34, start=(470, 380))


def panda():
    head = ellipse(500, 400, 260, 230)
    ears = [circle(300, 210, 85), circle(700, 210, 85)]
    patches = [ellipse(410, 400, 70, 85, 25), ellipse(590, 400, 70, 85, -25)]
    body = ellipse(500, 860, 220, 230)
    arms = [capsule((320, 760), (260, 910), 115), capsule((680, 760), (740, 910), 115)]
    legs = [capsule((410, 990), (400, 1060), 140), capsule((590, 990), (600, 1060), 140)]
    feet = [ellipse(395, 1085, 95, 50), ellipse(605, 1085, 95, 50)]
    belly = ellipse(500, 900, 120, 140)
    neck = capsule((500, 560), (500, 690), 230)
    parts = [Part(neck, PANDA_W)] + [Part(e, PANDA_K) for e in ears] + [Part(l, PANDA_K) for l in legs] + [Part(f, PANDA_K) for f in feet] + [Part(body, PANDA_W), Part(belly, '#F3F0EA', sil=False)] + \
            [Part(a, PANDA_K) for a in arms] + [Part(head, PANDA_W)] + [Part(p, PANDA_K, sil=False) for p in patches]
    def details(c, sw):
        s = fill_path(circle(415, 395, 26), 'white', INK, sw * .5) + fill_path(circle(585, 395, 26), 'white', INK, sw * .5)
        s += f'<circle cx="420" cy="398" r="13" fill="{INK}"/><circle cx="580" cy="398" r="13" fill="{INK}"/>'
        return s + nose(500, 480, 36, 24) + smile(475, 520, 50, sw, 18) + smile(525, 520, 50, sw, 18) + cheek(350, 480, 30, 18, c, sw) + cheek(650, 480, 30, 18, c, sw)
    return dict(parts=parts, details=details, dots=36, start=(500, 170))


def monkey():
    head = circle(500, 380, 220)
    ears = [circle(270, 390, 90), circle(730, 390, 90)]
    inner = [circle(275, 395, 50), circle(725, 395, 50)]
    face = soften(unary_union([circle(430, 360, 100), circle(570, 360, 100), ellipse(500, 480, 150, 100)]), 20)
    body = ellipse(500, 840, 190, 220)
    tail = chaikin([(640, 960), (780, 980), (870, 900), (860, 780), (790, 760), (800, 840), (760, 900), (650, 900)])
    arms = [capsule((340, 750), (320, 930), 95), capsule((660, 750), (680, 930), 95)]
    legs = [capsule((420, 990), (415, 1060), 120), capsule((580, 990), (585, 1060), 120)]
    feet = [ellipse(405, 1085, 85, 45), ellipse(595, 1085, 85, 45)]
    belly = ellipse(500, 880, 110, 140)
    neck = capsule((500, 560), (500, 690), 230)
    parts = [Part(neck, MONKEY)] + [Part(tail, MONKEY)] + [Part(e, MONKEY) for e in ears] + [Part(i, MONKEY_L, sil=False) for i in inner] + \
        chibi(head, body, arms, legs, feet, MONKEY, None, belly, MONKEY_L) + [Part(head, MONKEY), Part(face, MONKEY_L, sil=False)]
    def details(c, sw):
        return (eye(440, 360, 26, sw) + eye(560, 360, 26, sw) + f'<ellipse cx="480" cy="440" rx="9" ry="6" fill="{INK}"/><ellipse cx="520" cy="440" rx="9" ry="6" fill="{INK}"/>'
                + smile(500, 500, 110, sw, 30) + cheek(390, 450, 28, 17, c, sw) + cheek(610, 450, 28, 17, c, sw))
    return dict(parts=parts, details=details, dots=38, start=(500, 160))


def cow():
    head = ellipse(500, 400, 230, 220)
    horns = [poly([(350, 260), (290, 130), (410, 220)], 20), poly([(650, 260), (710, 130), (590, 220)], 20)]
    ears = [ellipse(250, 330, 90, 45, 20), ellipse(750, 330, 90, 45, -20)]
    muzzle = ellipse(500, 520, 170, 110)
    spot = ellipse(600, 330, 70, 60)
    body = ellipse(500, 850, 220, 230)
    arms = [capsule((330, 760), (300, 920), 100), capsule((670, 760), (700, 920), 100)]
    legs = [capsule((420, 990), (415, 1060), 120), capsule((580, 990), (585, 1060), 120)]
    feet = [ellipse(405, 1085, 85, 45), ellipse(595, 1085, 85, 45)]
    bspots = unary_union([ellipse(420, 800, 70, 55), ellipse(600, 900, 60, 50)])
    bell = circle(500, 680, 45)
    neck = capsule((500, 560), (500, 690), 230)
    parts = [Part(neck, COWW)] + [Part(h, '#EFE3C2') for h in horns] + [Part(e, COWW) for e in ears] + chibi(head, body, arms, legs, feet, COWW, SPOTC) + \
        [Part(bspots, SPOTC, sil=False), Part(head, COWW), Part(spot, SPOTC, sil=False), Part(muzzle, '#F6C5C0', sil=False), Part(bell, GOLD)]
    def details(c, sw):
        return (eye(420, 380, 26, sw) + eye(580, 380, 26, sw) + f'<ellipse cx="460" cy="520" rx="14" ry="18" fill="{INK}"/><ellipse cx="540" cy="520" rx="14" ry="18" fill="{INK}"/>'
                + smile(500, 580, 70, sw, 18))
    return dict(parts=parts, details=details, dots=36, start=(500, 175))


def sheep():
    wool = soften(unary_union([circle(500 + 260 * math.cos(math.radians(a)), 700 + 220 * math.sin(math.radians(a)), 110) for a in range(0, 360, 40)] + [ellipse(500, 700, 270, 230)]), 10)
    head = ellipse(500, 380, 170, 190)
    tuft = soften(unary_union([circle(430, 220, 70), circle(500, 200, 75), circle(570, 220, 70)]), 10)
    ears = [ellipse(310, 380, 80, 40, 20), ellipse(690, 380, 80, 40, -20)]
    legs = [capsule((400, 900), (400, 1060), 70), capsule((600, 900), (600, 1060), 70)]
    feet = [ellipse(400, 1080, 60, 35), ellipse(600, 1080, 60, 35)]
    parts = [Part(l, SHEEPF) for l in legs] + [Part(f, BLACKISH) for f in feet] + [Part(wool, WOOL)] + [Part(e, SHEEPF) for e in ears] + [Part(head, SHEEPF), Part(tuft, WOOL)]
    def details(c, sw):
        s = fill_path(circle(440, 380, 34), 'white', INK, sw * .6) + fill_path(circle(560, 380, 34), 'white', INK, sw * .6)
        s += eye(445, 385, 20, sw) + eye(555, 385, 20, sw) + f'<path d="M470,480 Q500,505 530,480" fill="none" stroke="white" stroke-width="{sw}" stroke-linecap="round"/>'
        return s
    return dict(parts=parts, details=details, dots=40, start=(500, 120))


def chick():
    body = soften(unary_union([circle(500, 520, 260), ellipse(500, 780, 300, 260)]), 40)
    tuft = poly([(470, 280), (440, 180), (500, 240), (540, 170), (540, 280)], 12)
    wings = [ellipse(220, 760, 80, 130, 20), ellipse(780, 760, 80, 130, -20)]
    beak = poly([(450, 540), (550, 540), (500, 610)], 15)
    legs = [capsule((420, 1020), (420, 1080), 30), capsule((580, 1020), (580, 1080), 30)]
    feet = [poly([(360, 1110), (420, 1070), (480, 1110)], 12), poly([(520, 1110), (580, 1070), (640, 1110)], 12)]
    parts = [Part(l, BEAK) for l in legs] + [Part(f, BEAK) for f in feet] + [Part(tuft, CHICK)] + [Part(w, '#EFC94A') for w in wings] + [Part(body, CHICK), Part(beak, BEAK, sil=False)]
    def details(c, sw):
        return eye(420, 470, 30, sw) + eye(580, 470, 30, sw) + cheek(360, 560, 34, 20, c, sw) + cheek(640, 560, 34, 20, c, sw)
    return dict(parts=parts, details=details, dots=36, start=(500, 200))


def butterfly():
    wings = [ellipse(300, 420, 230, 260, -20), ellipse(700, 420, 230, 260, 20), ellipse(320, 820, 170, 200, 25), ellipse(680, 820, 170, 200, -25)]
    dots_ = unary_union([circle(280, 400, 70), circle(720, 400, 70), circle(320, 840, 50), circle(680, 840, 50)])
    body = capsule((500, 380), (500, 1000), 110)
    head = circle(500, 300, 110)
    ant = [capsule((470, 210), (400, 90), 16), capsule((530, 210), (600, 90), 16)]
    knobs = [circle(395, 82, 28), circle(605, 82, 28)]
    parts = [Part(a, BLACKISH) for a in ant] + [Part(k, BLACKISH) for k in knobs] + [Part(w, BFLY) for w in wings[:2]] + [Part(w, BFLY_2) for w in wings[2:]] + \
            [Part(dots_, '#FFFFFF', sil=False), Part(body, '#6B5A7A'), Part(head, '#6B5A7A')]
    def details(c, sw):
        return eye(465, 295, 20, sw) + eye(535, 295, 20, sw) + f'<path d="M475,340 Q500,360 525,340" fill="none" stroke="white" stroke-width="{sw * .8}" stroke-linecap="round"/>'
    return dict(parts=parts, details=details, dots=40, start=(500, 150))


def dolphin():
    body = chaikin([(180, 760), (260, 520), (420, 360), (640, 300), (820, 360), (900, 470), (880, 560), (760, 540), (650, 560), (560, 640), (480, 780), (420, 920), (330, 980)])
    fin = poly([(560, 330), (620, 170), (700, 320)], 25)
    flipper = poly([(520, 600), (470, 740), (600, 640)], 20)
    tailf = poly([(390, 920), (300, 1010), (170, 1070), (235, 965), (150, 900), (300, 935)], 20)
    belly = chaikin([(300, 840), (380, 640), (560, 540), (760, 540), (650, 600), (520, 700), (420, 880)])
    parts = [Part(fin, DOLPH), Part(tailf, DOLPH), Part(body, DOLPH), Part(belly, DOLPH_L, sil=False), Part(flipper, DOLPH)]
    def details(c, sw):
        return eye(740, 420, 26, sw) + f'<path d="M800,500 Q850,520 890,505" fill="none" stroke="{INK}" stroke-width="{sw * .8}" stroke-linecap="round"/>' + cheek(760, 480, 28, 16, c, sw)
    return dict(parts=parts, details=details, dots=36, start=(640, 160))


def seal():
    body = chaikin([(250, 1000), (220, 800), (300, 600), (380, 420), (520, 330), (680, 360), (740, 480), (700, 620), (640, 800), (660, 960), (560, 1040)])
    flippers = [poly([(330, 780), (180, 900), (340, 880)], 25), poly([(620, 780), (790, 880), (640, 900)], 25)]
    tailf = poly([(300, 960), (170, 1070), (440, 1030)], 25)
    ball = circle(545, 270, 105)
    belly = ellipse(470, 820, 120, 180)
    stripes = lambda g: unary_union([LineString([(460, 180), (470, 360)]), LineString([(545, 170), (545, 370)]), LineString([(630, 180), (620, 360)])])
    parts = [Part(tailf, SEAL), Part(flippers[0], SEAL), Part(body, SEAL), Part(belly, SEAL_L, sil=False), Part(flippers[1], SEAL), Part(ball, '#F2A04A', tex=stripes)]
    def details(c, sw):
        return (eye(540, 440, 26, sw) + eye(650, 450, 24, sw) + nose(615, 510, 30, 20) + smile(590, 545, 50, sw, 18) + smile(640, 545, 50, sw, 18)
                + f'<path d="M560,520 L470,500 M560,535 L470,540 M680,525 L760,505 M680,540 L760,545" stroke="{INK}" stroke-width="{sw * .5}" stroke-linecap="round"/>')
    return dict(parts=parts, details=details, dots=38, start=(560, 130))


def flamingo():
    body = ellipse(520, 560, 230, 150, -10)
    wing = ellipse(560, 560, 150, 90, -10)
    neck = chaikin([(420, 520), (330, 430), (300, 300), (330, 180), (400, 130), (470, 150), (480, 210), (420, 200), (380, 250), (390, 360), (460, 460), (480, 500)], 3)
    head = circle(440, 150, 80)
    beak = poly([(500, 140), (600, 180), (560, 230), (490, 190)], 15)
    leg = capsule((560, 690), (560, 1060), 26)
    leg2 = chaikin([(600, 690), (640, 800), (560, 860), (580, 840), (620, 800), (585, 700)], 2)
    foot = poly([(500, 1080), (560, 1040), (630, 1080)], 12)
    tailf = poly([(290, 520), (220, 470), (280, 590)], 20)
    parts = [Part(leg, FLAM_D), Part(leg2, FLAM_D), Part(foot, FLAM_D), Part(tailf, FLAM_D), Part(body, FLAM), Part(wing, FLAM_D, sil=False), Part(neck, FLAM), Part(head, FLAM), Part(beak, BLACKISH)]
    def details(c, sw):
        return eye(450, 135, 22, sw) + cheek(420, 180, 22, 14, c, sw)
    return dict(parts=parts, details=details, dots=40, start=(440, 60))


def squirrel():
    tail = chaikin([(560, 950), (760, 960), (900, 800), (900, 560), (820, 380), (700, 340), (640, 420), (720, 520), (760, 680), (700, 840), (600, 880)])
    head = circle(400, 380, 190)
    ears = [poly([(270, 260), (280, 120), (360, 220)], 20), poly([(470, 220), (540, 110), (530, 260)], 20)]
    body = ellipse(430, 800, 190, 230)
    belly = ellipse(410, 830, 110, 150)
    arms = [capsule((330, 700), (380, 800), 75), capsule((500, 700), (450, 810), 75)]
    acorn = ellipse(415, 840, 55, 65)
    legs = [capsule((350, 980), (340, 1060), 110), capsule((510, 980), (520, 1060), 110)]
    feet = [ellipse(330, 1085, 80, 42), ellipse(530, 1085, 80, 42)]
    neck = capsule((400, 520), (420, 640), 200)
    parts = [Part(neck, SQ)] + [Part(tail, SQ, tex=lambda g: LineString([(640, 900), (820, 760), (830, 560), (760, 430)]))] + [Part(e, SQ) for e in ears] + \
        [Part(l, SQ) for l in legs] + [Part(f, SQ) for f in feet] + [Part(body, SQ), Part(belly, SQ_L, sil=False), Part(head, SQ), Part(acorn, '#B07A52', sil=False)] + [Part(a, SQ) for a in arms]
    def details(c, sw):
        return (eye(340, 370, 24, sw) + eye(460, 370, 24, sw) + nose(400, 430, 24, 16) + smile(385, 465, 40, sw, 14) + smile(415, 465, 40, sw, 14)
                + cheek(300, 440, 26, 16, c, sw) + cheek(500, 440, 26, 16, c, sw))
    return dict(parts=parts, details=details, dots=40, start=(280, 110))


def parrot():
    body = ellipse(500, 640, 210, 300)
    head = circle(500, 330, 180)
    beak = soften(unary_union([ellipse(500, 400, 70, 80)]), 5)
    crest = poly([(450, 180), (430, 70), (500, 150), (540, 60), (550, 170)], 15)
    wings = [ellipse(320, 680, 90, 220, 10), ellipse(680, 680, 90, 220, -10)]
    tailf = poly([(430, 900), (570, 900), (540, 1100), (460, 1100)], 20)
    feet = [ellipse(440, 940, 50, 30), ellipse(560, 940, 50, 30)]
    belly = ellipse(500, 700, 120, 190)
    parts = [Part(tailf, '#4A8FD6'), Part(crest, PARROT_R)] + [Part(w, '#4A8FD6') for w in wings] + [Part(body, PARROT), Part(belly, PARROT_Y, sil=False), Part(head, PARROT_R), Part(beak, '#F6E7C9')] + [Part(f, '#9B9B9B') for f in feet]
    def details(c, sw):
        s = fill_path(circle(420, 320, 46), 'white', INK, sw * .6) + fill_path(circle(580, 320, 46), 'white', INK, sw * .6)
        return s + eye(425, 325, 26, sw) + eye(575, 325, 26, sw) + f'<path d="M440,405 Q500,440 560,405" fill="none" stroke="{INK}" stroke-width="{sw * .7}"/>'
    return dict(parts=parts, details=details, dots=38, start=(480, 60))


def tiger():
    head = ellipse(500, 400, 250, 220)
    ears = [circle(300, 210, 75), circle(700, 210, 75)]
    inner = [circle(305, 220, 40), circle(695, 220, 40)]
    muzzle = ellipse(500, 490, 140, 90)
    body = ellipse(500, 850, 200, 230)
    tail = chaikin([(660, 940), (800, 930), (880, 820), (880, 700), (830, 700), (830, 800), (780, 870), (650, 880)])
    arms = [capsule((340, 760), (330, 930), 100), capsule((660, 760), (670, 930), 100)]
    legs = [capsule((420, 990), (415, 1060), 120), capsule((580, 990), (585, 1060), 120)]
    feet = [ellipse(405, 1085, 85, 45), ellipse(595, 1085, 85, 45)]
    belly = ellipse(500, 890, 110, 140)
    hstripes = lambda g: unary_union([LineString([(500, 190), (500, 270)]), LineString([(440, 200), (455, 260)]), LineString([(560, 200), (545, 260)]),
                                       LineString([(260, 380), (320, 400)]), LineString([(260, 440), (320, 440)]), LineString([(740, 380), (680, 400)]), LineString([(740, 440), (680, 440)])])
    bstripes = lambda g: unary_union([LineString([(310, 800 + i * 70), (380, 790 + i * 70)]) for i in range(3)] + [LineString([(690, 800 + i * 70), (620, 790 + i * 70)]) for i in range(3)])
    neck = capsule((500, 560), (500, 690), 230)
    parts = [Part(neck, TIGER)] + [Part(tail, TIGER)] + [Part(e, TIGER) for e in ears] + [Part(i, TIGER_L, sil=False) for i in inner] + \
        [Part(l, TIGER) for l in legs] + [Part(f, TIGER) for f in feet] + [Part(body, TIGER, tex=bstripes), Part(belly, TIGER_L, sil=False)] + [Part(a, TIGER) for a in arms] + \
        [Part(head, TIGER, tex=hstripes), Part(muzzle, TIGER_L, sil=False)]
    def details(c, sw):
        return (eye(410, 380, 26, sw) + eye(590, 380, 26, sw) + nose(500, 465, 36, 24) + smile(475, 505, 50, sw, 18) + smile(525, 505, 50, sw, 18)
                + cheek(355, 470, 30, 18, c, sw) + cheek(645, 470, 30, 18, c, sw))
    return dict(parts=parts, details=details, dots=40, start=(500, 175))


def dragon():
    head = ellipse(500, 380, 230, 200)
    horns = [poly([(360, 220), (320, 90), (420, 190)], 18), poly([(640, 220), (680, 90), (580, 190)], 18)]
    snout = ellipse(500, 480, 150, 90)
    body = ellipse(500, 840, 210, 230)
    wings = [poly([(330, 700), (120, 520), (170, 700), (100, 760), (300, 820)], 30), poly([(670, 700), (880, 520), (830, 700), (900, 760), (700, 820)], 30)]
    tail = chaikin([(640, 960), (800, 1000), (900, 940), (940, 860), (890, 900), (790, 920), (660, 900)])
    tip = poly([(920, 870), (980, 800), (960, 900)], 10)
    arms = [capsule((350, 760), (370, 920), 95), capsule((650, 760), (630, 920), 95)]
    legs = [capsule((420, 990), (415, 1060), 120), capsule((580, 990), (585, 1060), 120)]
    feet = [ellipse(405, 1085, 85, 45), ellipse(595, 1085, 85, 45)]
    belly = ellipse(500, 880, 120, 150)
    scales = lambda g: unary_union([LineString([(400, 800 + i * 55), (600, 800 + i * 55)]) for i in range(4)]).intersection(belly)
    neck = capsule((500, 560), (500, 690), 230)
    parts = [Part(neck, DRAGON)] + [Part(tail, DRAGON), Part(tip, DRAGON_D)] + [Part(w, '#A8D9C3') for w in wings] + [Part(h, '#F2D58A') for h in horns] + \
        [Part(l, DRAGON) for l in legs] + [Part(f, DRAGON_D) for f in feet] + [Part(body, DRAGON), Part(belly, '#F2E6B8', sil=False, tex=scales)] + \
        [Part(a, DRAGON) for a in arms] + [Part(head, DRAGON), Part(snout, '#9DD4BA', sil=False)]
    def details(c, sw):
        return (eye(420, 360, 28, sw) + eye(580, 360, 28, sw) + f'<ellipse cx="470" cy="470" rx="10" ry="7" fill="{INK}"/><ellipse cx="530" cy="470" rx="10" ry="7" fill="{INK}"/>'
                + smile(500, 520, 100, sw, 25) + cheek(360, 450, 30, 18, c, sw) + cheek(640, 450, 30, 18, c, sw))
    return dict(parts=parts, details=details, dots=40, start=(500, 180))


ANIMALS123 = {'frog': frog, 'dino': dino, 'duck': duck, 'crab': crab, 'ladybug': ladybug, 'bee': bee, 'snail': snail, 'panda': panda,
              'monkey': monkey, 'cow': cow, 'sheep': sheep, 'chick': chick, 'butterfly': butterfly, 'dolphin': dolphin, 'seal': seal,
              'flamingo': flamingo, 'squirrel': squirrel, 'parrot': parrot, 'tiger': tiger, 'dragon': dragon}
