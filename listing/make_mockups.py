import asyncio, math, random
from playwright.async_api import async_playwright
SRC = 'file:///home/claude/listing/src'
F = 'file:///home/claude/listing/node_modules/@fontsource'
def crayon(color, x, y, rot, L=520, w=58):
    return f'''<svg style="position:absolute;left:{x}px;top:{y}px;transform:rotate({rot}deg);filter:drop-shadow(8px 14px 10px rgba(40,25,10,.35))" width="{L+40}" height="{w}" viewBox="0 0 {L+40} {w}">
      <path d="M{L},{w*0.18} L{L+38},{w/2} L{L},{w*0.82} Z" fill="{color}"/><path d="M{L},{w*0.18} L{L+14},{w*0.3} L{L+14},{w*0.7} L{L},{w*0.82} Z" fill="#e9dcc6"/>
      <rect x="0" y="0" width="{L}" height="{w}" rx="{w*0.22}" fill="{color}"/>
      <rect x="{L*0.12}" y="0" width="{L*0.72}" height="{w}" fill="rgba(255,255,255,.18)"/>
      <rect x="{L*0.14}" y="{w*0.12}" width="{L*0.68}" height="{w*0.76}" rx="4" fill="none" stroke="rgba(0,0,0,.18)" stroke-width="3"/>
      <rect x="0" y="{w*0.12}" width="{L}" height="{w*0.1}" fill="rgba(255,255,255,.35)"/></svg>'''
def page(img, x, y, w, rot, shadow=True):
    h = w * 1.4142
    return f'<img src="{SRC}/{img}" style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;transform:rotate({rot}deg);box-shadow:{"0 30px 60px rgba(40,25,10,.35), 0 4px 10px rgba(40,25,10,.25)" if shadow else "none"};background:#fff">'
def phone(img, x, y, w, rot):
    h = w * 2.06
    return f'''<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;height:{h}px;transform:rotate({rot}deg);border-radius:{w*0.16}px;background:#1d1b1f;padding:{w*0.035}px;box-shadow:0 50px 90px rgba(30,18,8,.45),0 8px 20px rgba(30,18,8,.35), inset 0 0 0 3px #3a373d">
      <div style="width:100%;height:100%;border-radius:{w*0.13}px;overflow:hidden;position:relative;background:#000">
        <img src="{SRC}/{img}" style="width:100%;height:100%;object-fit:cover;object-position:top">
        <div style="position:absolute;top:{w*0.025}px;left:50%;transform:translateX(-50%);width:{w*0.3}px;height:{w*0.085}px;border-radius:99px;background:#000"></div>
      </div></div>'''
BASE = f'''<style>@font-face{{font-family:Gluten;font-weight:800;src:url({F}/gluten/files/gluten-latin-800-normal.woff2)}}
@font-face{{font-family:Figtree;font-weight:700;src:url({F}/figtree/files/figtree-latin-700-normal.woff2)}}
*{{margin:0;box-sizing:border-box}} html,body{{width:2000px;height:2000px;overflow:hidden}}
body{{background:url({SRC}/wood.jpg) center/cover;position:relative;font-family:Figtree}}
.tag{{position:absolute;background:#fffcf6;color:#2a1c15;border-radius:999px;padding:22px 44px;font:800 52px Gluten;box-shadow:0 14px 30px rgba(40,25,10,.3)}}</style>'''
mock = {}
mock['08-mockup-desk'] = BASE + page('flat_bunny.jpg', 170, 260, 980, -5) + crayon('#e0574c', 1060, 1640, -18) + crayon('#2f7fd0', 980, 1760, -9) + crayon('#f2c14e', 120, 1720, 6, 460) + \
    phone('ph_bunny_2.png', 1200, 330, 640, 7) + '<div class="tag" style="left:1180px;top:1760px;transform:rotate(-2deg)">Their colors come alive!</div>'
mock['09-mockup-pages'] = BASE + page('page_santa.jpg', 120, 140, 760, -9) + page('page_house.jpg', 640, 90, 760, 6) + page('page_hedgehog.jpg', 1180, 210, 760, 11) + \
    page('flat_owl.jpg', 540, 640, 820, -2) + crayon('#26a65b', 1250, 1630, -24) + crayon('#e0574c', 1320, 1745, -14) + crayon('#935cc4', 80, 1690, 12, 470) + \
    '<div class="tag" style="left:110px;top:1840px">Prints great in black &amp; white</div>'
mock['10-mockup-reindeer'] = BASE + page('flat_reindeer.jpg', 230, 300, 1000, 4) + crayon('#2f7fd0', 140, 1720, -6) + crayon('#f08a24', 260, 1830, -2, 480) + \
    phone('ph_reindeer_2.png', 1130, 230, 660, -6) + '<div class="tag" style="left:1150px;top:1680px;transform:rotate(2deg)">Scan the QR, watch it move</div>'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        pg = await (await b.new_context(viewport={'width': 2000, 'height': 2000})).new_page()
        for name, body in mock.items():
            path = f'/home/claude/listing/src/{name}.html'; open(path, 'w').write(f'<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>{body}</body></html>')
            await pg.goto('file://' + path); await pg.wait_for_timeout(600)
            await pg.screenshot(path=f'/home/claude/listing/photos/{name}.png')
        await b.close()
asyncio.run(main())
