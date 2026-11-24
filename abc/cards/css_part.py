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
