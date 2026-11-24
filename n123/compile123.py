import asyncio, os, time, shutil
from playwright.async_api import async_playwright
T = '/home/claude/repo-marymarii/scan/targets'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
        pg = await b.new_page()
        await pg.goto('http://localhost:8765/tools/compile1.html'); await pg.wait_for_function('window.ready')
        for f in sorted(os.listdir('/home/claude/ar/gen123/ardata')):
            key, size = f[:-5].rsplit('_', 1)
            if os.path.exists(f'{T}/{key}-{size}.js'): continue
            t0 = time.time()
            b64 = await pg.evaluate(f"window.compile('../gen123/pages/{size}/{key}.png')")
            open(f'{T}/{key}-{size}.js', 'w').write('export default "' + b64 + '";\n')
            shutil.copy(f'/home/claude/ar/gen123/ardata/{f}', f'{T}/{key}_{size}.json')
            print(key, size, round(time.time() - t0, 1), 's', len(b64) // 1024, 'KB', flush=True)
        await b.close()
asyncio.run(main())
