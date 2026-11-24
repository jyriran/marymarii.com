import asyncio, sys
from playwright.async_api import async_playwright
ARGS = ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=ARGS)
        key,img,o=sys.argv[1],sys.argv[2],sys.argv[3]
        pg = await (await b.new_context(viewport={'width':390,'height':780}, device_scale_factor=2)).new_page()
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(f'http://localhost:8766/scan/?s={key}&fov=56')
        await pg.set_input_files('#file', img)
        await pg.wait_for_function("window.__ar.state==='alive'", timeout=90000)
        for i,w in enumerate([1200,900,900,900]):
            await pg.wait_for_timeout(w); await pg.screenshot(path=f'/tmp/{o}_{i}.png')
        print(o,errs); await b.close()
asyncio.run(main())
