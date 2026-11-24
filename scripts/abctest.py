import asyncio, json, sys, time
from playwright.async_api import async_playwright
SIZE = sys.argv[1]; KEYS = sys.argv[2].split(','); SUF = sys.argv[3] if len(sys.argv) > 3 else ''
async def one(b, key):
    ctx = await b.new_context(viewport={'width': 390, 'height': 760}, device_scale_factor=1)
    pg = await ctx.new_page(); errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)[:160]))
    await pg.goto(f'http://localhost:8766/scan/?s={key}&fov=56' + ('&size=letter' if SIZE == 'letter' else ''))
    await pg.set_input_files('#file', f'/home/claude/ar/genabc/stills/{key}_{SIZE}{SUF}.jpg')
    t0 = time.time(); res = {'key': key}
    try:
        await pg.wait_for_function("window.__ar.state==='alive'", timeout=60000)
        res['alive_s'] = round(time.time() - t0, 1)
        await pg.wait_for_timeout(1500); await pg.screenshot(path=f'/tmp/abc_{SIZE}_{key}.png')
    except Exception as e:
        res['error'] = str(e)[:60]; await pg.screenshot(path=f'/tmp/abc_{SIZE}_{key}.png')
    res['errors'] = errs; print(json.dumps(res), flush=True); await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        for k in KEYS: await one(b, k)
        await b.close()
asyncio.run(main())
