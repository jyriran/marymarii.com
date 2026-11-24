import asyncio
from playwright.async_api import async_playwright
ARGS = ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']
KEYS = ['hedgehog','gift','bell','stocking','snowman','gingerbread','penguin','tree','owl','santa','house','bunny','fox','reindeer','bear']
async def shot(b, key, img, vp, dpr, out, n, wait=2500, step=700):
    pg = await (await b.new_context(viewport=vp, device_scale_factor=dpr)).new_page()
    await pg.goto(f'http://localhost:8766/scan/?s={key}&fov=56')
    await pg.set_input_files('#file', img)
    await pg.wait_for_function("window.__ar.state==='alive'", timeout=90000)
    await pg.wait_for_timeout(wait)
    for i in range(n):
        await pg.screenshot(path=out.format(i=i)); await pg.wait_for_timeout(step)
    await pg.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=ARGS)
        for key in ['bunny','reindeer']:
            await shot(b, key, f'/home/claude/ar/gen/stills/{key}_a4.jpg', {'width':390,'height':780}, 2.5, f'/tmp/new_ph_{key}_{{i}}.png', 3)
        await shot(b, 'penguin', '/home/claude/ar/gen/stills/penguin_a4.jpg', {'width':390,'height':780}, 2.5, '/tmp/new_penguin_{i}.png', 3)
        for key in KEYS:
            await shot(b, key, f'/home/claude/ar/gen/stills/{key}_a4.jpg', {'width':390,'height':640}, 1, f'/tmp/new_dance_{key}_{{i}}.png', 2)
            print(key, flush=True)
        await b.close()
asyncio.run(main())
