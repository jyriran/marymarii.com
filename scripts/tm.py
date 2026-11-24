import asyncio, sys
from playwright.async_api import async_playwright
ARGS = ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=ARGS)
        for key in sys.argv[1:]:
            img = f'/home/claude/ar/genabc/stills/{key}_a4.jpg' if key.startswith('abc-') else f'/home/claude/ar/gen/stills/{key}_a4.jpg'
            pg = await (await b.new_context(viewport={'width':390,'height':780}, device_scale_factor=1.5)).new_page()
            errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(f'http://localhost:8766/scan/?s={key}&fov=56')
            await pg.set_input_files('#file', img)
            try: await pg.wait_for_function("window.__ar.state==='alive'", timeout=90000)
            except Exception: print(key,'NOT ALIVE',errs); await pg.close(); continue
            await pg.wait_for_timeout(3000); await pg.screenshot(path=f'/tmp/m_{key}.png'); print(key,errs,flush=True); await pg.close()
        await b.close()
asyncio.run(main())
