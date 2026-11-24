import asyncio, os
from playwright.async_api import async_playwright
F = 'file:///home/claude/listing/node_modules/@fontsource'
IMG = 'file:///home/claude/xmas/img_bw'
SRC = 'file:///home/claude/listing/src'
SHEETS = [('hedgehog','Hedgehog',30),('gift','Gift Box',32),('bell','Bell',34),('stocking','Stocking',36),('snowman','Snowman',40),
          ('gingerbread','Gingerbread Man',42),('penguin','Penguin',42),('tree','Christmas Tree',44),('owl','Owl',44),('santa','Santa',48),
          ('house','Gingerbread House',48),('bunny','Bunny',52),('fox','Fox',56),('reindeer','Reindeer',59),('bear','Polar Bear',73)]
lv = lambda d: 1 if d <= 36 else 2 if d <= 44 else 3 if d <= 56 else 4
CSS = f'''
@font-face {{ font-family: Gluten; font-weight: 700; src: url({F}/gluten/files/gluten-latin-700-normal.woff2); }}
@font-face {{ font-family: Gluten; font-weight: 800; src: url({F}/gluten/files/gluten-latin-800-normal.woff2); }}
@font-face {{ font-family: Figtree; font-weight: 600; src: url({F}/figtree/files/figtree-latin-600-normal.woff2); }}
@font-face {{ font-family: Figtree; font-weight: 700; src: url({F}/figtree/files/figtree-latin-700-normal.woff2); }}
@font-face {{ font-family: Figtree; font-weight: 800; src: url({F}/figtree/files/figtree-latin-800-normal.woff2); }}
:root {{ --paper:#fffcf6; --ink:#2a1c15; --muted:#6d5d53; --red:#e0574c; --teal:#7fbfb8; --sun:#f2c14e; --grid:#e8ddd0; }}
* {{ box-sizing: border-box; margin: 0; }}
html, body {{ width: 2000px; height: 2000px; overflow: hidden; }}
body {{ background: var(--paper); color: var(--ink); font: 600 44px/1.35 Figtree, sans-serif;
  background-image: radial-gradient(var(--grid) 4px, transparent 4.6px); background-size: 62px 62px; position: relative; }}
h1, h2, .d {{ font-family: Gluten, cursive; font-weight: 800; line-height: 1; letter-spacing: -0.01em; }}
.brand {{ position: absolute; left: 90px; top: 74px; font: 800 52px Gluten; display: flex; gap: 16px; align-items: center; }}
.brand i {{ width: 30px; height: 30px; border-radius: 50%; background: var(--red); display: inline-block; }}
.sheet {{ background: #fff; border-radius: 26px; box-shadow: 0 18px 0 rgba(42,28,21,.9), 0 0 0 5px var(--ink); overflow: hidden; }}
.sheet img {{ display: block; width: 100%; height: 100%; object-fit: cover; }}
.pill {{ display: inline-block; background: var(--ink); color: var(--paper); border-radius: 999px; padding: 18px 40px; font-weight: 800; }}
.phone {{ position: absolute; border: 14px solid var(--ink); border-radius: 86px; background: var(--ink); overflow: hidden; box-shadow: 26px 26px 0 var(--teal); }}
.phone img {{ display: block; width: 100%; height: 100%; object-fit: cover; object-position: top; border-radius: 70px; }}
.num {{ display: inline-grid; place-items: center; width: 120px; height: 120px; border-radius: 50%; background: var(--ink); color: var(--paper); font: 800 66px Gluten; }}
.stars {{ color: var(--red); letter-spacing: 4px; }} .stars s {{ color: #e3d6c8; text-decoration: none; }}
'''
def stars(n): return '★' * n + '<s>' + '★' * (4 - n) + '</s>'
pages = {}

# 1 hero
pages['01-hero'] = f'''
<div class="brand"><i></i>MaryMariiArt</div>
<div style="position:absolute;left:90px;top:210px;width:1100px">
  <h1 style="font-size:168px">Christmas<br>Dot to Dot</h1>
  <p style="font-size:62px;margin-top:40px;color:var(--muted);font-weight:700">15 printable pages · Ages 4–8</p>
  <p style="margin-top:44px"><span class="pill" style="background:var(--red);font-size:54px">Their coloring comes alive!</span></p>
</div>
<div class="sheet" style="position:absolute;left:110px;top:1010px;width:560px;height:560px;transform:rotate(-6deg)"><img src="{IMG}/santa.png"></div>
<div class="sheet" style="position:absolute;left:560px;top:1150px;width:560px;height:560px;transform:rotate(4deg)"><img src="{IMG}/fox.png"></div>
<div class="sheet" style="position:absolute;left:250px;top:1440px;width:470px;height:470px;transform:rotate(-2deg)"><img src="{IMG}/reindeer.png"></div>
<div class="phone" style="left:1240px;top:360px;width:640px;height:985px"><img src="{SRC}/phone_crop.png"></div>
<div style="position:absolute;left:1220px;top:1440px;width:700px;text-align:center;font-weight:800;font-size:46px">Scan the page with a phone.<br>No app needed.</div>
'''
# 2 all 15
cells = ''.join(f'''<div style="display:flex;flex-direction:column;gap:12px"><div class="sheet" style="width:340px;height:340px;box-shadow:0 10px 0 rgba(42,28,21,.9),0 0 0 4px var(--ink)"><img src="{IMG}/{k}.png"></div>
<div style="font-size:34px;font-weight:800;text-align:center">{n}</div></div>''' for k, n, d in SHEETS)
pages['02-all-15'] = f'''
<div style="position:absolute;left:0;right:0;top:80px;text-align:center"><h2 style="font-size:120px">15 pages inside</h2>
<p style="color:var(--muted);margin-top:18px;font-weight:700">From 30 to 73 dots · prints great in black &amp; white</p></div>
<div style="position:absolute;left:95px;top:390px;display:grid;grid-template-columns:repeat(5,340px);gap:34px 32px">{cells}</div>
'''
# 3 how it works
pages['03-how-it-works'] = f'''
<div style="position:absolute;left:0;right:0;top:80px;text-align:center"><h2 style="font-size:120px">How it works</h2></div>
<div style="position:absolute;left:90px;top:300px;display:grid;grid-template-columns:repeat(3,580px);gap:40px">
  <div><div class="sheet" style="width:580px;height:760px"><img src="{SRC}/page_penguin-09.png" style="object-fit:cover;object-position:center 30%"></div>
    <div style="margin-top:56px;display:flex;gap:24px;align-items:center"><span class="num">1</span><span class="d" style="font-size:74px">Connect<br>the dots</span></div></div>
  <div><div class="sheet" style="width:580px;height:760px"><img src="{SRC}/penguin_kid.jpg" style="object-position:62% 40%"></div>
    <div style="margin-top:56px;display:flex;gap:24px;align-items:center"><span class="num" style="background:var(--red)">2</span><span class="d" style="font-size:74px">Color<br>it in</span></div></div>
  <div><div class="phone" style="position:relative;width:580px;height:760px;box-shadow:none;border-radius:60px"><img src="{SRC}/phone_crop.png" style="border-radius:46px"></div>
    <div style="margin-top:56px;display:flex;gap:24px;align-items:center"><span class="num" style="background:var(--teal);color:var(--ink)">3</span><span class="d" style="font-size:74px">Scan &amp;<br>watch</span></div></div>
</div>
<p style="position:absolute;left:0;right:0;bottom:110px;text-align:center;font-size:54px;font-weight:700;color:var(--muted)">Each page has its own QR code. Works in the phone's browser.</p>
'''
# 4 colors come alive
pages['04-colors-come-alive'] = f'''
<div style="position:absolute;left:90px;top:110px;width:1820px"><h2 style="font-size:132px">Their own colors<br>come alive</h2>
<p style="margin-top:34px;font-size:52px;color:var(--muted);font-weight:700;max-width:1500px">The magic camera uses the colors your child chose, then the drawing jumps off the page and dances.</p></div>
<div class="sheet" style="position:absolute;left:110px;top:760px;width:820px;height:1080px;transform:rotate(-3deg)"><img src="{SRC}/penguin_kid.jpg" style="object-position:center"></div>
<div style="position:absolute;left:960px;top:1220px;font:800 160px Gluten;color:var(--red)">→</div>
<div class="phone" style="left:1220px;top:780px;width:680px;height:1046px"><img src="{SRC}/phone_crop.png"></div>
'''
# 5 difficulty
rows = ''.join(f'''<div style="display:grid;grid-template-columns:120px 1fr 200px;align-items:center;gap:24px;padding:14px 0;border-bottom:4px dashed var(--grid)">
<img src="file:///home/claude/site/img/{k}-sm.jpg" style="width:120px;height:120px;border-radius:18px;border:4px solid var(--ink);object-fit:cover"><span style="font-size:46px;font-weight:800">{n}<span style="color:var(--muted);font-weight:600"> · 1–{d}</span></span>
<span class="stars" style="font-size:46px;text-align:right">{stars(lv(d))}</span></div>''' for k, n, d in [SHEETS[i] for i in (0, 3, 4, 7, 9, 11, 12, 13, 14)])
pages['05-easy-to-tricky'] = f'''
<div style="position:absolute;left:90px;top:100px"><h2 style="font-size:124px">Easy to tricky</h2>
<p style="margin-top:22px;color:var(--muted);font-weight:700">Difficulty stars on every page, so every child finds the right one.</p></div>
<div style="position:absolute;left:90px;right:90px;top:430px">{rows}</div>
<p style="position:absolute;left:90px;bottom:80px;color:var(--muted);font-size:40px">Showing 9 of the 15 pages.</p>
'''
# 6 what you get
items = [('15 dot-to-dot pages', 'Christmas characters, 30 to 73 dots'),
         ('A4 and US Letter', 'Two PDF files, 18 pages each'),
         ('Black &amp; white friendly', 'Designed for any home printer'),
         ('A QR code on every page', 'Opens the magic camera in the browser'),
         ('Name boxes', 'Your child writes their own name'),
         ('Instant download', 'Print at home as often as you like')]
lis = ''.join(f'<div style="display:grid;grid-template-columns:70px 1fr;gap:26px;align-items:start;margin-bottom:46px"><span style="width:62px;height:62px;border-radius:50%;background:var(--teal);border:5px solid var(--ink);margin-top:6px"></span><div><div style="font-size:60px;font-weight:800">{a}</div><div style="color:var(--muted);font-size:44px">{b}</div></div></div>' for a, b in items)
pages['06-what-you-get'] = f'''
<div style="position:absolute;left:90px;top:100px"><h2 style="font-size:124px">What you get</h2></div>
<div style="position:absolute;left:90px;top:360px;width:1060px">{lis}</div>
<div class="sheet" style="position:absolute;left:1220px;top:420px;width:640px;height:906px;transform:rotate(3deg)"><img src="{SRC}/intro-01.png" style="object-fit:contain;background:#fff"></div>
<div class="sheet" style="position:absolute;left:1180px;top:1080px;width:600px;height:850px;transform:rotate(-4deg)"><img src="{SRC}/page_penguin-09.png" style="object-fit:contain;background:#fff"></div>
<p style="position:absolute;left:90px;bottom:90px;font-size:40px;color:var(--muted)">Digital download. Nothing is shipped.</p>
'''
# 7 close-up of a real page
pages['07-page-close-up'] = f'''
<div style="position:absolute;inset:0;background:#efe7dc"></div>
<div class="sheet" style="position:absolute;left:330px;top:70px;width:1340px;height:1860px;border-radius:10px;box-shadow:0 30px 60px rgba(42,28,21,.25)"><img src="{SRC}/page_penguin-09.png" style="object-fit:contain;background:#fff"></div>
'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        pg = await (await b.new_context(viewport={'width': 2000, 'height': 2000})).new_page()
        for name, body in pages.items():
            html = f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}</body></html>'
            path = f'/home/claude/listing/src/{name}.html'; open(path, 'w').write(html)
            await pg.goto('file://' + path); await pg.wait_for_timeout(400)
            await pg.screenshot(path=f'/home/claude/listing/photos/{name}.png')
        await b.close()
asyncio.run(main())
