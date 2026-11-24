import asyncio, sys
from playwright.async_api import async_playwright
exec(open('css_part.py').read().split("def stars")[0])   # F, CSS
I = 'file:///home/claude/abc/cardsNZ/img'; O = 'file:///home/claude/abc/out'
BR = '<div class="brand"><i></i>MaryMariiArt</div>'
ANIMALS = ['Narwhal','Octopus','Pig','Quail','Rabbit','Snake','Turtle','Unicorn','Vulture','Whale','X-ray Fish','Yak','Zebra']
cards = {}
cards['01-hero'] = f'''{BR}
<div style="position:absolute;left:90px;top:210px;width:960px">
  <h1 style="font-size:176px">ABC<br>Dot to Dot</h1>
  <p style="font-size:66px;margin-top:30px;font-weight:800">Letters N to Z</p>
  <p style="font-size:54px;margin-top:14px;color:var(--muted);font-weight:700">13 printable pages · Ages 3–6</p>
  <div style="margin-top:56px;display:flex;flex-direction:column;gap:22px;font-size:54px;font-weight:800">
    <div>✏️ Trace the letter</div><div>🔢 Connect the dots</div><div>🖍️ Color it in</div><div>📱 Scan &amp; watch it come alive</div></div>
</div>
<div class="sheet" style="position:absolute;left:1060px;top:300px;width:760px;height:1075px;transform:rotate(6deg)"><img src="{O}/mk_color_U.png" style="width:100%"></div>
<div class="sheet" style="position:absolute;left:990px;top:560px;width:800px;height:1131px;transform:rotate(-4deg)"><img src="{O}/mk_color_P.png" style="width:100%"></div>
<p style="position:absolute;left:90px;bottom:90px"><span class="pill" style="background:var(--red);font-size:50px">No app needed · Prints in black &amp; white</span></p>'''
steps = [('1', 'Trace the<br>big letter', 'crop_letter.png', 'var(--ink)'), ('2', 'Practice<br>on the lines', 'crop_practice.png', 'var(--red)'),
         ('3', 'Connect<br>&amp; color', 'crop_animal_done.png', 'var(--sun)'), ('4', 'Scan &amp;<br>watch', None, 'var(--teal)')]
cells = ''
for n, t, img, col in steps:
    inner = f'<img src="{I}/{img}" style="width:100%;height:100%;object-fit:contain;background:#fff">' if img else \
        f'''<div style="position:relative;height:100%;background:#fff"><div class="phone" style="left:250px;top:30px;width:300px;height:500px;border-width:10px;border-radius:52px;box-shadow:14px 14px 0 var(--teal)"><img src="{O}/col_narwhal.png" style="width:100%;height:100%;object-fit:contain;background:#fff"></div>
<div style="position:absolute;left:150px;top:90px;font:800 80px Gluten;color:var(--sun)">✦</div><div style="position:absolute;left:600px;top:200px;font:800 64px Gluten;color:var(--red)">✦</div><div style="position:absolute;left:180px;top:380px;font:800 56px Gluten;color:var(--teal)">✦</div></div>'''
    cells += f'''<div><div class="sheet" style="height:560px">{inner}</div>
    <div style="margin-top:40px;display:flex;gap:24px;align-items:center"><span class="num" style="background:{col};color:{'var(--ink)' if col in ('var(--sun)','var(--teal)') else 'var(--paper)'}">{n}</span><span class="d" style="font-size:70px">{t}</span></div></div>'''
cards['02-how-it-works'] = f'''<div style="position:absolute;left:0;right:0;top:80px;text-align:center"><h2 style="font-size:120px">How each page works</h2></div>
<div style="position:absolute;left:110px;right:110px;top:300px;display:grid;grid-template-columns:1fr 1fr;gap:70px 90px">{cells}</div>
<p style="position:absolute;left:0;right:0;bottom:70px;text-align:center;font-size:48px;font-weight:700;color:var(--muted)">Every page has its own QR code. Works in the phone's browser.</p>'''
cards['03-stroke-order'] = f'''{BR}
<div style="position:absolute;left:90px;top:220px;width:900px"><h2 style="font-size:132px">Learn the right stroke order</h2>
<p style="margin-top:40px;font-size:54px;color:var(--muted);font-weight:700">Start at number 1, follow the arrow, join the dots. Then 2, then 3.</p>
<div style="margin-top:60px;display:flex;flex-direction:column;gap:30px;font-size:54px;font-weight:800">
<div>✓ Capital and lowercase letters</div><div>✓ Numbered strokes with arrows</div><div>✓ Two practice rows on handwriting lines</div></div></div>
<div class="sheet" style="position:absolute;left:1060px;top:180px;width:820px;height:1240px"><img src="{I}/crop_letter.png" style="width:100%;height:100%;object-fit:contain;background:#fff"></div>
<div class="sheet" style="position:absolute;left:90px;top:1520px;width:1790px;height:380px"><img src="{I}/crop_practice.png" style="width:100%;height:100%;object-fit:contain;background:#fff"></div>'''
grid = ''.join(f'''<div><div class="sheet" style="height:360px"><img src="{I}/p-{i+3:02d}.png" style="width:100%;height:100%;object-fit:cover;object-position:top"></div>
<div style="font-size:34px;font-weight:800;text-align:center;margin-top:18px">{chr(78+i)} · {a}</div></div>''' for i, a in enumerate(ANIMALS))
cards['04-all-13-pages'] = f'''<div style="position:absolute;left:0;right:0;top:70px;text-align:center"><h2 style="font-size:116px">13 pages inside: N to Z</h2>
<p style="color:var(--muted);margin-top:16px;font-weight:700">A friendly animal for every letter · 32 to 40 dots</p></div>
<div style="position:absolute;left:100px;right:100px;top:330px;display:grid;grid-template-columns:repeat(5,1fr);gap:40px 44px">{grid}</div>'''
items = [('13 letter pages, N to Z', 'Capital + lowercase, stroke order, practice rows, dot-to-dot animal'),
         ('A4 and US Letter PDFs', '16 pages each: cover, how-it-works, 13 letters, color ideas'),
         ('Made for B&amp;W printers', 'Print at home as often as you like for your family'),
         ('Magic camera on every page', 'Scan the QR code. No app, no account, nothing uploaded'),
         ('Name boxes on every page', 'Your child writes their own name')]
lis = ''.join(f'<div style="display:grid;grid-template-columns:70px 1fr;gap:26px;align-items:start;margin-bottom:46px"><span style="width:62px;height:62px;border-radius:50%;background:var(--teal);border:5px solid var(--ink);margin-top:6px"></span><div><div style="font-size:60px;font-weight:800">{a}</div><div style="color:var(--muted);font-size:44px">{b}</div></div></div>' for a, b in items)
cards['05-what-you-get'] = f'''<div style="position:absolute;left:90px;top:100px"><h2 style="font-size:124px">What you get</h2></div>
<div style="position:absolute;left:90px;top:330px;width:1080px">{lis}</div>
<div class="sheet" style="position:absolute;left:1250px;top:360px;width:660px;height:933px;transform:rotate(4deg)"><img src="{O}/mk_bw_O.png" style="width:100%"></div>
<p style="position:absolute;left:90px;bottom:90px;font-size:40px;color:var(--muted)">Digital download. Nothing is shipped.</p>'''
cards['06-page-close-up'] = f'''<div style="position:absolute;inset:0;background:#efe7dc"></div>
<div class="sheet" style="position:absolute;left:330px;top:70px;width:1340px;height:1860px;border-radius:10px;box-shadow:0 30px 60px rgba(42,28,21,.25)"><img src="{I}/big-03.png" style="width:100%;height:100%;object-fit:contain;background:#fff"></div>'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await (await b.new_context(viewport={'width': 2000, 'height': 2000})).new_page()
        for name, body in cards.items():
            html = f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}</body></html>'
            path = f'/home/claude/abc/cardsNZ/{name}.html'; open(path, 'w').write(html)
            await pg.goto('file://' + path); await pg.wait_for_timeout(500)
            await pg.screenshot(path=f'/home/claude/abc/cardsNZ/{name}.jpg', type='jpeg', quality=92)
        await b.close()
asyncio.run(main())
