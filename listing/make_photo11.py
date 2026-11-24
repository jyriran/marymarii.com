import asyncio
from playwright.async_api import async_playwright
exec(open('make_photos.py').read().split("pages = {}")[0])   # reuse CSS and paths
names = dict(hedgehog='Hedgehog', gift='Gift Box', bell='Bell', stocking='Stocking', snowman='Snowman', gingerbread='Gingerbread', penguin='Penguin', tree='Tree', owl='Owl', santa='Santa', house='House', bunny='Bunny', fox='Fox', reindeer='Reindeer', bear='Polar Bear')
cells = ''.join(f'''<div style="display:flex;flex-direction:column;gap:8px;align-items:center"><div style="width:320px;height:500px;border-radius:30px;overflow:hidden;border:8px solid var(--ink);background:#000"><img src="{SRC}/dance_{k}.png" style="width:100%;height:100%;object-fit:cover;object-position:top"></div>
<div style="font-size:34px;font-weight:800">{n}</div></div>''' for k, n in names.items())
body = f'''<div style="position:absolute;left:0;right:0;top:50px;text-align:center"><h2 style="font-size:112px">Every page comes alive</h2>
<p style="color:var(--muted);margin-top:12px;font-weight:700">15 pages, 15 little dances, each in your child's own colors</p></div>
<div style="position:absolute;left:62px;top:290px;display:grid;grid-template-columns:repeat(5,320px);gap:16px 54px">{cells}</div>'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        pg = await (await b.new_context(viewport={'width': 2000, 'height': 2000})).new_page()
        path = '/home/claude/listing/src/11.html'
        open(path, 'w').write(f'<!DOCTYPE html><html><head><meta charset="utf-8"><style>{CSS}</style></head><body>{body}</body></html>')
        await pg.goto('file://' + path); await pg.wait_for_timeout(500)
        await pg.screenshot(path='/home/claude/listing/photos/11-every-page-alive.png')
        await b.close()
asyncio.run(main())
