#!/usr/bin/env python3
"""Builds the product pages under /shop/<slug>/index.html from the PRODUCTS list.
Run from the repo root:  python3 shop/make_pages.py [slug ...]"""
import sys, os, html

SITE = "https://marymarii.com"
ETSY = "https://www.etsy.com/listing/"

PRODUCTS = {
  "christmas": dict(
    payhip="EGtDe", etsy="4623775202", price="4.99",
    name="Christmas Coloring Pages That Come Alive",
    kicker="15 dot-to-dot pages · ages 4–8",
    lead="Your child connects the dots and colors the picture. Then you scan the page with your phone and their own drawing comes alive and dances. No app needed.",
    video="../../img/video/real-scan-bear.mp4", poster="../../img/video/real-scan-bear.jpg",
    video_note="Real phone, real page, no edits: a colored Polar Bear page scanned with the magic camera.",
    grid_title="All 15 pages", grid=[(f"../../img/{k}-sm.jpg", n) for k, n in [
      ("hedgehog","Hedgehog"),("gift","Gift Box"),("bell","Bell"),("stocking","Stocking"),("snowman","Snowman"),
      ("gingerbread","Gingerbread Man"),("penguin","Penguin"),("tree","Christmas Tree"),("owl","Owl"),("santa","Santa"),
      ("house","Gingerbread House"),("bunny","Bunny"),("fox","Fox"),("reindeer","Reindeer"),("bear","Polar Bear")]],
    included=["15 Christmas dot-to-dot pages, from easy (30 dots) to tricky (73 dots)",
              "Every page has a QR code for the magic camera",
              "2 PDF files: A4 and US Letter",
              "Made for black-and-white printers"],
    ai=True,
    title="Christmas Coloring Pages That Come Alive · Printable Dot to Dot for Kids",
    desc="15 printable Christmas dot-to-dot coloring pages for kids ages 4–8. Color the page, scan it with your phone and watch it come alive. No app needed. A4 + US Letter PDF.",
  ),
}

CSS = """
@font-face{font-family:Gluten;font-weight:600;font-display:swap;src:url(../../fonts/gluten-latin-600-normal.woff2) format("woff2")}
@font-face{font-family:Gluten;font-weight:800;font-display:swap;src:url(../../fonts/gluten-latin-800-normal.woff2) format("woff2")}
@font-face{font-family:Figtree;font-weight:400;font-display:swap;src:url(../../fonts/figtree-latin-400-normal.woff2) format("woff2")}
@font-face{font-family:Figtree;font-weight:700;font-display:swap;src:url(../../fonts/figtree-latin-700-normal.woff2) format("woff2")}
:root{--paper:#fbf7f1;--ink:#2a1c15;--muted:#6d5d53;--red:#d65f50;--blush:#f4e5dd;--teal:#8cbdb5;--sun:#ecc06a;--grid:#e9dfd3}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--paper) radial-gradient(var(--grid) 2.2px,transparent 2.6px) 0 0/28px 28px;color:var(--ink);font:400 17px/1.6 Figtree,system-ui,sans-serif}
.wrap{max-width:1080px;margin:0 auto;padding:0 22px}
a{color:inherit}
header{position:sticky;top:0;z-index:5;background:rgba(251,247,241,.92);backdrop-filter:blur(6px);border-bottom:2px solid var(--grid)}
.nav{display:flex;align-items:center;justify-content:space-between;height:68px}
.nav img{height:42px;width:auto;display:block}
.nav nav a{font-weight:700;text-decoration:none;margin-left:22px;font-size:.95rem}
h1,h2,h3{font-family:Gluten,cursive;font-weight:800;line-height:1.1;margin:0}
h1{font-size:clamp(34px,5.4vw,56px)}
h2{font-size:clamp(28px,4vw,40px);text-align:center}
.hero{display:grid;grid-template-columns:1.05fr .95fr;gap:46px;align-items:center;padding:46px 0 30px}
.kicker{display:inline-block;background:var(--sun);font:800 17px Gluten;padding:8px 16px 4px;border-radius:30px;box-shadow:0 0 0 3px var(--ink);transform:rotate(-2deg);margin-bottom:18px}
.lead{font-size:1.12rem;color:var(--muted);margin:18px 0 24px}
.buy{display:flex;align-items:center;gap:18px;flex-wrap:wrap}
.price{font:800 40px Gluten}
.btn{display:inline-block;background:var(--red);color:#fff!important;font:800 22px Gluten;text-decoration:none;padding:16px 30px 11px;border-radius:40px;box-shadow:0 6px 0 var(--ink);border:3px solid var(--ink);transition:transform .12s}
.btn:hover{transform:translateY(-2px)}
.btn:active{transform:translateY(3px);box-shadow:0 2px 0 var(--ink)}
.alt{font-size:.92rem;color:var(--muted);margin-top:14px}
.ticks{list-style:none;padding:0;margin:22px 0 0;display:grid;gap:6px;font-weight:700}
.ticks li:before{content:"✓ ";color:#2f7d4f}
.phone{justify-self:center;width:min(330px,80vw);aspect-ratio:9/18.5;border:14px solid var(--ink);border-radius:46px;background:var(--ink);overflow:hidden;box-shadow:18px 18px 0 var(--teal);transform:rotate(3deg)}
.phone video{width:100%;height:100%;object-fit:cover;display:block;border-radius:32px}
.note{font-size:.85rem;color:var(--muted);text-align:center;margin-top:22px}
section{padding:56px 0}
.card{background:#fff;border:3px solid var(--ink);border-radius:26px;box-shadow:0 8px 0 var(--ink);padding:34px}
.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:24px;margin-top:30px}
.step{text-align:center}
.step b{display:inline-flex;width:54px;height:54px;border-radius:50%;background:var(--sun);border:3px solid var(--ink);align-items:center;justify-content:center;font:800 26px Gluten;margin-bottom:10px}
.step h3{font-size:24px;margin-bottom:6px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:18px;margin-top:30px}
.grid figure{margin:0;background:#fff;border-radius:14px;padding:8px;box-shadow:0 0 0 2px var(--grid);text-align:center}
.grid img{width:100%;height:auto;display:block;border-radius:8px}
.grid figcaption{font-size:.85rem;color:var(--muted);margin-top:4px}
.two{display:grid;grid-template-columns:1fr 1fr;gap:28px}
.included li{margin:6px 0}
.free{background:var(--blush);text-align:center}
details{background:#fff;border:2px solid var(--grid);border-radius:16px;padding:14px 18px;margin:10px 0}
summary{font-weight:700;cursor:pointer}
.ai{font-size:.85rem;color:var(--muted);font-style:italic}
.final{text-align:center}
footer{background:var(--ink);color:#fbf7f1;padding:34px 0;font-size:.88rem;margin-top:40px}
footer .wrap{display:flex;justify-content:space-between;gap:18px;flex-wrap:wrap}
@media (max-width:820px){.hero,.two{grid-template-columns:1fr}.steps{grid-template-columns:1fr}.nav nav a:not(.shop){display:none}.phone{order:-1;width:min(260px,70vw)}}
"""

def page(slug, p):
    e = html.escape
    grid = "".join(f'<figure><img src="{src}" alt="{e(n)} page" loading="lazy" width="300" height="424"><figcaption>{e(n)}</figcaption></figure>' for src, n in p["grid"])
    inc = "".join(f"<li>{e(x)}</li>" for x in p["included"])
    buy_btn = f'<a class="btn payhip-buy-button" data-theme="none" data-product="{p["payhip"]}" href="https://payhip.com/b/{p["payhip"]}">Buy now · €{p["price"]}</a>'
    etsy = f'<p class="alt">Instant download · 2 PDFs (A4 + US Letter) · Prefer Etsy? <a href="{ETSY}{p["etsy"]}">Buy it on Etsy ↗</a></p>'
    ai = '<p class="ai">Some illustrations were created with the help of AI tools, then turned into dot-to-dot pages and checked by us.</p>' if p.get("ai") else ""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(p['title'])}</title>
<meta name="description" content="{e(p['desc'])}">
<link rel="canonical" href="{SITE}/shop/{slug}/">
<meta property="og:title" content="{e(p['title'])}">
<meta property="og:description" content="{e(p['desc'])}">
<meta property="og:image" content="{SITE}/og.jpg">
<link rel="icon" href="../../brand/icon-32.png" type="image/png" sizes="32x32">
<link rel="apple-touch-icon" href="../../brand/icon-180.png">
<style>{CSS}</style>
</head>
<body>
<header><div class="wrap nav">
  <a href="../../"><img src="../../brand/lockup-ink.png" alt="MaryMarii" width="186" height="56"></a>
  <nav><a href="../../#how">How it works</a><a href="../../#free">Free page</a><a class="shop" href="../">All products</a></nav>
</div></header>
<main class="wrap">
  <div class="hero">
    <div>
      <span class="kicker">{e(p['kicker'])}</span>
      <h1>{e(p['name'])}</h1>
      <p class="lead">{e(p['lead'])}</p>
      <div class="buy"><span class="price">€{p['price']}</span>{buy_btn}</div>
      {etsy}
      <ul class="ticks"><li>No app, no sign-up</li><li>Print at home, as often as you like</li><li>Works on any phone camera</li></ul>
    </div>
    <div>
      <div class="phone"><video src="{p['video']}" poster="{p['poster']}" autoplay muted loop playsinline></video></div>
      <p class="note">{e(p['video_note'])}</p>
    </div>
  </div>

  <section id="how">
    <h2>How the magic works</h2>
    <div class="steps">
      <div class="step"><b>1</b><h3>Connect &amp; color</h3><p>Print a page, connect the dots and color the picture any way you like.</p></div>
      <div class="step"><b>2</b><h3>Scan</h3><p>Scan the QR code on the page with your phone camera. The magic camera opens in your browser.</p></div>
      <div class="step"><b>3</b><h3>Watch it come alive</h3><p>Point the phone at the page and the drawing comes alive in your child's own colors.</p></div>
    </div>
  </section>

  <section>
    <h2>{e(p['grid_title'])}</h2>
    <div class="grid">{grid}</div>
  </section>

  <section>
    <div class="card two">
      <div><h3 style="font-size:28px">What you get</h3><ul class="included">{inc}</ul>{ai}</div>
      <div><h3 style="font-size:28px">Good to know</h3><ul class="included"><li>Digital download, nothing is shipped. Your download link appears right after paying and is also emailed to you.</li><li>For personal and classroom use. Please don't share or resell the files.</li><li>The magic camera runs in the phone's browser. Nothing is saved or sent.</li></ul></div>
    </div>
  </section>

  <section class="card free">
    <h2>Try it free first</h2>
    <p>Download a free page, color it and see the magic for yourself.</p>
    <a class="btn" style="background:#2f7d4f" href="../../#free">Get a free page</a>
  </section>

  <section>
    <h2>Questions</h2>
    <details><summary>How do I get the files?</summary><p>Right after paying you get a download link on screen and by email. Download on a computer for easiest printing.</p></details>
    <details><summary>Do I need an app?</summary><p>No. Scan the QR code with the normal phone camera and the magic camera opens in the browser.</p></details>
    <details><summary>Which printer and paper?</summary><p>Any home printer, black and white is fine. Plain A4 or US Letter paper works; thicker paper is nicer for crayons and markers.</p></details>
    <details><summary>Can I use it in my classroom?</summary><p>Yes, you can print for your own class. For a whole school, send us a message at info@marymarii.com.</p></details>
  </section>

  <section class="final">
    <h2>Make Christmas a little more magic</h2>
    <p class="lead">Instant download · €{p['price']}</p>
    {buy_btn}
  </section>
</main>
<footer><div class="wrap"><span>© 2026 MaryMariiArt · Blissena OÜ, Estonia</span><span>Checkout and file delivery are provided by Payhip (payments by Stripe).</span></div></footer>
<script src="https://payhip.com/payhip.js" async></script>
<script>
document.addEventListener('click',function(e){{var a=e.target.closest&&e.target.closest('a[href]');if(!a||!window.goatcounter||!window.goatcounter.count)return;var h=a.getAttribute('href');
if(/payhip\\.com\\/b\\//.test(h)){{window.goatcounter.count({{path:'buy/{slug}',title:'Buy now click',event:true}});}}
else if(/etsy\\.com/i.test(h)){{window.goatcounter.count({{path:'etsy/{p["etsy"]}',title:'Etsy link (product page)',event:true}});}}}});
</script>
<script data-goatcounter="https://marymarii.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
</body>
</html>
"""

if __name__ == "__main__":
    slugs = sys.argv[1:] or list(PRODUCTS)
    for s in slugs:
        os.makedirs(f"shop/{s}", exist_ok=True)
        open(f"shop/{s}/index.html", "w").write(page(s, PRODUCTS[s]))
        print("built shop/%s/index.html" % s)
