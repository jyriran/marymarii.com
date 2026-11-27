#!/usr/bin/env python3
"""Builds the product pages under /shop/<slug>/index.html from the PRODUCTS list.
Run from the repo root:  python3 shop/make_pages.py [slug ...]"""
import sys, os, html

SITE = "https://marymarii.com"
ETSY = "https://www.etsy.com/listing/"

V = "../../img/video/"
S = "../../img/shop/"
AM = "Alligator Bear Cat Dog Elephant Fish Giraffe Hippo Iguana Jellyfish Koala Lion Mouse".split()
NZ = "Narwhal Octopus Pig Quail Rabbit Snake Turtle Unicorn Vulture Whale X-ray_Fish Yak Zebra".split()
N123 = "Dinosaur Duck Crab Ladybug Bee Snail Frog Panda Monkey Cow Sheep Chick Butterfly Dolphin Seal Flamingo Squirrel Parrot Tiger Dragon".split()
ABC_STEPS = [("Trace & connect", "Trace the big letter in the right stroke order, then connect the dots on the animal and color it."),
             ("Scan", "A grown-up scans the QR code on the page with the phone camera. The magic camera opens in the browser."),
             ("Watch it come alive", "Point the phone at the page and the animal comes alive in your child's own colors.")]
N_STEPS = [("Count & connect", "Trace the number and its word, count the pictures, then connect the dots and color the animal."),
           ("Scan", "A grown-up scans the QR code on the page with the phone camera. The magic camera opens in the browser."),
           ("Watch it come alive", "The animal hops the same number of times as the number on the page, then dances.")]
ABC_FAQ = [("What age is it for?", "Ages 3–6: preschool, kindergarten and homeschool. Little ones trace, older ones write the letter on their own."),
           ("Is the artwork made with AI?", "No. The letters and animals are drawn with our own drawing code.")]

PRODUCTS = {
  "christmas": dict(
    payhip="EGtDe", etsy="4623775202", price="4.99",
    name="Christmas Coloring Pages That Come Alive",
    kicker="15 dot-to-dot pages · ages 4–8",
    lead="Your child connects the dots and colors the picture. Then you scan the page with your phone and their own drawing comes alive and dances. No app needed.",
    video=V+"real-scan-bear.mp4", poster=V+"real-scan-bear.jpg",
    video_note="Real phone, real page, no edits: a colored Polar Bear page scanned with the magic camera.",
    grid_title="All 15 pages", grid=[(f"../../img/{k}-sm.jpg", n) for k, n in [
      ("hedgehog","Hedgehog"),("gift","Gift Box"),("bell","Bell"),("stocking","Stocking"),("snowman","Snowman"),
      ("gingerbread","Gingerbread Man"),("penguin","Penguin"),("tree","Christmas Tree"),("owl","Owl"),("santa","Santa"),
      ("house","Gingerbread House"),("bunny","Bunny"),("fox","Fox"),("reindeer","Reindeer"),("bear","Polar Bear")]],
    included=["15 Christmas dot-to-dot pages, from easy (30 dots) to tricky (73 dots)",
              "Every page has a QR code for the magic camera",
              "2 PDF files: A4 and US Letter",
              "Made for black-and-white printers"],
    ai=True, final="Make Christmas a little more magic",
    title="Christmas Coloring Pages That Come Alive · Printable Dot to Dot for Kids",
    desc="15 printable Christmas dot-to-dot coloring pages for kids ages 4–8. Color the page, scan it with your phone and watch it come alive. No app needed. A4 + US Letter PDF.",
  ),
  "abc-a-m": dict(
    payhip="ThytP", etsy="4624015371", price="4.99",
    name="Alphabet Tracing A–M That Comes Alive",
    kicker="13 letter pages · ages 3–6",
    lead="Trace the letter, practice it on the lines, connect the dots on a friendly animal and color it. Then scan the page and the animal comes alive. No app needed.",
    video=V+"real-scan-narwhal.mp4", poster=V+"real-scan-narwhal.jpg",
    video_note="Real phone scan of a page from the series (N is for Narwhal). Every A–M page works the same way.",
    grid_title="All 13 letters", grid=[(S+f"abc-{c}.jpg", f"{c.upper()} · {a}") for c, a in zip("abcdefghijklm", AM)],
    included=["13 letter pages, A to M: " + ", ".join(AM),
              "On every page: a big capital and lowercase letter with numbered stroke order, a dot-to-dot animal, two practice rows and boxes for your child's name",
              "Every page has a QR code for the magic camera",
              "2 PDF files: A4 and US Letter (cover, how-it-works page, 13 letter pages and a color-ideas page)",
              "Made for black-and-white printers"],
    steps=ABC_STEPS, faq=ABC_FAQ, final="Learn the letters with a little magic",
    title="Alphabet Tracing Worksheets A–M That Come Alive · Printable for Preschool",
    desc="13 printable letter tracing pages A–M for ages 3–6: stroke order, handwriting practice and a dot-to-dot animal that comes alive when you scan the page. No app. A4 + US Letter PDF.",
  ),
  "abc-n-z": dict(
    payhip="8MTQZ", etsy="4624410579", price="4.99",
    name="Alphabet Tracing N–Z That Comes Alive",
    kicker="13 letter pages · ages 3–6",
    lead="Trace the letter, practice it on the lines, connect the dots on a friendly animal and color it. Then scan the page and the animal comes alive. No app needed.",
    video=V+"real-scan-narwhal.mp4", poster=V+"real-scan-narwhal.jpg",
    video_note="Real phone, real page, no edits: N is for Narwhal, scanned with the magic camera.",
    grid_title="All 13 letters", grid=[(S+f"abc-{c}.jpg", f"{c.upper()} · {a.replace('_',' ')}") for c, a in zip("nopqrstuvwxyz", NZ)],
    included=["13 letter pages, N to Z: " + ", ".join(a.replace('_',' ') for a in NZ),
              "On every page: a big capital and lowercase letter with numbered stroke order, a dot-to-dot animal, two practice rows and boxes for your child's name",
              "Every page has a QR code for the magic camera",
              "2 PDF files: A4 and US Letter",
              "Made for black-and-white printers"],
    steps=ABC_STEPS, faq=ABC_FAQ, final="Finish the alphabet with a little magic",
    title="Alphabet Tracing Worksheets N–Z That Come Alive · Printable for Preschool",
    desc="13 printable letter tracing pages N–Z for ages 3–6: stroke order, handwriting practice and a dot-to-dot animal that comes alive when you scan the page. No app. A4 + US Letter PDF.",
  ),
  "123": dict(
    payhip="ubg1k", etsy="4624717605", price="4.99",
    name="Number Tracing 1–20 That Comes Alive",
    kicker="20 number pages · ages 3–6",
    lead="Trace the number and its word, count the pictures, connect the dots and color the animal. Then scan the page: the animal hops as many times as the number, then dances.",
    video=V+"real-scan-duck.mp4", poster=V+"real-scan-duck.jpg",
    video_note="Real phone, real page, no edits: 2 is for Duck, scanned with the magic camera.",
    grid_title="All 20 numbers", grid=[(S+f"n{i}.jpg", f"{i} · {a}") for i, a in enumerate(N123, 1)],
    included=["20 number pages, 1 to 20, each with its own animal",
              "On every page: a big number with a stroke start and arrow, the number word to trace, a counting box with ten-frames, a dot-to-dot animal and a practice row",
              "Every page has a QR code for the magic camera",
              "2 PDF files: A4 and US Letter",
              "Made for black-and-white printers"],
    steps=N_STEPS, faq=[("What age is it for?", "Ages 3–6: preschool, kindergarten and homeschool counting practice."),
                        ("Is the artwork made with AI?", "No. The numbers and animals are drawn with our own drawing code.")],
    final="Make counting a little more magic",
    title="Number Tracing Worksheets 1–20 That Come Alive · Printable Counting for Preschool",
    desc="20 printable number tracing pages 1–20 for ages 3–6: trace, count and connect the dots. Scan the page and the animal hops and dances. No app. A4 + US Letter PDF.",
  ),
  "learning-bundle": dict(
    payhip="fFsvI", etsy="4624719417", price="9.99",
    name="Preschool Learning Bundle: ABC A–Z + Numbers 1–20",
    kicker="46 pages · ages 3–6 · save 33%",
    lead="The whole alphabet and numbers 1 to 20 in one download. Every page is a tracing page and a dot-to-dot animal that comes alive when you scan it.",
    video=V+"real-scan-narwhal.mp4", poster=V+"real-scan-narwhal.jpg",
    video_note="Real phone, real page, no edits: N is for Narwhal, scanned with the magic camera.",
    grid_title="All 46 pages", grid=[(S+f"abc-{c}.jpg", f"{c.upper()} · {a.replace('_',' ')}") for c, a in zip("abcdefghijklmnopqrstuvwxyz", AM + NZ)]
                                   + [(S+f"n{i}.jpg", f"{i} · {a}") for i, a in enumerate(N123, 1)],
    included=["Letter Tracing A–M (13 pages), Letter Tracing N–Z (13 pages) and Number Tracing 1–20 (20 pages)",
              "€14.97 if bought separately, €9.99 together",
              "Every page has a QR code for the magic camera",
              "2 PDF files: A4 and US Letter (55 pages each, with covers and how-it-works pages)",
              "Made for black-and-white printers"],
    steps=ABC_STEPS, faq=ABC_FAQ, final="A whole year of letters and numbers",
    title="Preschool Learning Bundle · Alphabet A–Z + Numbers 1–20 That Come Alive",
    desc="46 printable tracing pages for ages 3–6: the whole alphabet and numbers 1–20, each with a dot-to-dot animal that comes alive when you scan the page. No app. A4 + US Letter PDF.",
  ),
  "christmas-eve-box": dict(
    payhip="kLe15", etsy=None, price="5.99",
    name="Christmas Eve Box Activity Pack",
    kicker="42 pages · ages 3–8",
    lead="Fill the whole evening: a treasure hunt that leads to the Christmas Eve box, a reindeer hunt, picture bingo with a magic caller and dot-to-dot pages that come alive. Print at home, no app needed.",
    video=V+"found-it.mp4", poster=V+"found-it.jpg",
    video_note="The last treasure clue has a QR code. Scan it and the phone celebrates: \"You found it!\"",
    grid_title="What's inside", grid=[(S+f"eb-p{n}.jpg", c) for n, c in [
      (1,"Overview"),(2,"Treasure hunt guide"),(3,"Clue cards"),(4,"More clue cards"),(6,"Reindeer hunt"),(7,"Hunt checklist"),
      (8,"Bingo: how to play"),(9,"Bingo card"),(33,"Calling cards"),(35,"Star markers"),(37,"Hedgehog"),(38,"Gingerbread Man"),
      (39,"Santa"),(40,"Reindeer"),(41,"Box tags"),(42,"Certificate")]],
    included=["Treasure hunt to the box: 11 rhyming clue cards and a blank card; the last clue has a QR code for a \"You found it!\" surprise",
              "Reindeer hunt: 15 Christmas friends to cut out and hide, with a picture checklist (no reading needed)",
              "Christmas Bingo: 12 cards in color and in black and white, calling cards, star markers and the Magic Bingo Caller",
              "4 dot-to-dot pages that come alive: Hedgehog, Gingerbread Man, Santa and Reindeer",
              "\"Do not open until Christmas Eve!\" box tags and an \"I found my Christmas Eve box!\" certificate",
              "2 PDF files: A4 and US Letter"],
    ai=True,
    steps=[("Print & hide", "Print the pages, hide the clue cards and the reindeer around the house."),
           ("Play", "Follow the clues to the box, find all the reindeer friends and play bingo with the magic caller."),
           ("Scan", "Scan a QR code with the phone camera: the caller, the surprise and the dot-to-dot pages open in the browser.")],
    faq=[("What age is it for?", "Ages 3–8. Grown-ups read the clues to little ones; the checklists and bingo use pictures."),
         ("Color or black and white?", "Both work. The bingo cards come in both versions.")],
    final="Make Christmas Eve a little more magic",
    title="Christmas Eve Box Activity Pack · Printable Treasure Hunt, Bingo & Dot to Dot",
    desc="A printable Christmas Eve box activity pack for kids 3–8: treasure hunt clues, a reindeer hunt, picture bingo with a magic caller and dot-to-dot pages that come alive. A4 + US Letter PDF.",
  ),
  "christmas-bingo": dict(
    payhip="ReEpa", etsy=None, price="2.99",
    name="Christmas Bingo with a Magic Caller",
    kicker="12 picture cards · ages 3–8",
    lead="Picture bingo for the whole family or the class party. Tap the magic caller on your phone to call the next picture and watch it dance. Tap BINGO! for a confetti party.",
    video=V+"bingo-caller.mp4", poster=V+"bingo-caller.jpg",
    video_note="The Magic Bingo Caller runs in any phone browser. No app, nothing is saved or sent.",
    grid_title="What's inside", grid=[(S+f"eb-p{n}.jpg", c) for n, c in [
      (8,"How to play"),(9,"Card 1"),(10,"Card 2"),(11,"Card 3"),(21,"Black-and-white card"),(33,"Calling cards"),(34,"B&W calling cards"),(35,"Star markers")]],
    included=["12 different bingo cards (3×3 with a FREE star), no two alike",
              "The same 12 cards in black and white, to save ink or color in",
              "15 calling cards in color and in black and white",
              "Star markers to cut out",
              "How-to-play page with a QR code for the Magic Bingo Caller",
              "2 PDF files: A4 and US Letter"],
    ai=True,
    steps=[("Print", "Print the cards and cut out the star markers."),
           ("Call", "Scan the QR code to open the magic caller, or use the calling cards."),
           ("BINGO!", "First full row shouts BINGO! Tap the button for a confetti party.")],
    faq=[("How many can play?", "2 or more. With 12 different cards it works for a whole class; print extra for more players."),
         ("Can non-readers play?", "Yes. Every square is a picture with its word.")],
    final="Bring bingo to the Christmas table",
    title="Christmas Bingo for Kids with a Magic Caller · Printable Picture Bingo",
    desc="Printable Christmas picture bingo for kids 3–8: 12 cards in color and black and white, calling cards and a magic caller on your phone. A4 + US Letter PDF.",
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
    etsy = (f'<p class="alt">Instant download · 2 PDFs (A4 + US Letter) · Prefer Etsy? <a href="{ETSY}{p["etsy"]}">Buy it on Etsy ↗</a></p>'
            if p.get("etsy") else '<p class="alt">Instant download · 2 PDFs (A4 + US Letter)</p>')
    steps = p.get("steps") or [("Connect &amp; color", "Print a page, connect the dots and color the picture any way you like."),
        ("Scan", "Scan the QR code on the page with your phone camera. The magic camera opens in your browser."),
        ("Watch it come alive", "Point the phone at the page and the drawing comes alive in your child's own colors.")]
    steps_html = "".join(f'<div class="step"><b>{i}</b><h3>{t if "&amp;" in t else e(t)}</h3><p>{e(d)}</p></div>' for i, (t, d) in enumerate(steps, 1))
    faq_html = "".join(f'<details><summary>{e(q)}</summary><p>{e(a)}</p></details>' for q, a in p.get("faq", []))
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
    <h2>How it works</h2>
    <div class="steps">{steps_html}</div>
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
    {faq_html}
    <details><summary>Can I use it in my classroom?</summary><p>Yes, you can print for your own class. For a whole school, send us a message at info@marymarii.com.</p></details>
  </section>

  <section class="final">
    <h2>{e(p["final"])}</h2>
    <p class="lead">Instant download · €{p['price']}</p>
    {buy_btn}
  </section>
</main>
<footer><div class="wrap"><span>© 2026 MaryMariiArt · Blissena OÜ, Estonia</span><span>Checkout and file delivery are provided by Payhip (payments by Stripe).</span></div></footer>
<script src="https://payhip.com/payhip.js" async></script>
<script>
document.addEventListener('click',function(e){{var a=e.target.closest&&e.target.closest('a[href]');if(!a||!window.goatcounter||!window.goatcounter.count)return;var h=a.getAttribute('href');
if(/payhip\\.com\\/b\\//.test(h)){{window.goatcounter.count({{path:'buy/{slug}',title:'Buy now click',event:true}});}}
else if(/etsy\\.com/i.test(h)){{window.goatcounter.count({{path:'etsy/{p.get("etsy")}',title:'Etsy link (product page)',event:true}});}}}});
</script>
<script data-goatcounter="https://marymarii.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
</body>
</html>
"""

def overview():
    e = html.escape
    order = ["christmas-eve-box", "christmas", "christmas-bingo", "learning-bundle", "abc-a-m", "abc-n-z", "123"]
    cards = ""
    for s in order:
        p = PRODUCTS[s]
        img = {"abc-a-m": "../img/shop/abc-a.jpg", "abc-n-z": "../img/shop/abc-z.jpg"}.get(s, p["poster"].replace("../../", "../"))
        cards += f'''<article class="pc"><a href="{s}/" class="pimg"><img src="{img}" alt="" loading="lazy" width="540" height="974"></a>
<div class="pbody"><span class="pk">{e(p["kicker"])}</span><h3><a href="{s}/">{e(p["name"])}</a></h3>
<div class="prow"><span class="price">€{p["price"]}</span><a class="btn sm" href="{s}/">See the pages</a></div></div></article>'''
    css = CSS.replace("../../", "../")
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Shop · MaryMarii printable pages that come alive</title>
<meta name="description" content="Printable dot-to-dot, tracing and Christmas activity pages for kids 3–8 that come alive when you scan them with your phone. Instant download, no app.">
<link rel="canonical" href="{SITE}/shop/"><link rel="icon" href="../brand/icon-32.png" type="image/png" sizes="32x32">
<style>{css}
.pgrid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:22px;margin:30px 0 60px}}
.pc{{background:#fff;border-radius:20px;box-shadow:0 0 0 2px var(--grid);overflow:hidden;display:flex;flex-direction:column}}
.pimg img{{width:100%;height:260px;object-fit:cover;display:block}}
.pbody{{padding:14px 16px 18px;display:flex;flex-direction:column;gap:8px;flex:1}}
.pk{{font-size:.8rem;font-weight:700;color:var(--muted)}}
.pc h3{{font-size:22px}} .pc h3 a{{text-decoration:none}}
.prow{{display:flex;flex-direction:column;align-items:stretch;gap:10px;margin-top:auto}}
.prow .btn{{text-align:center}}
.btn.sm{{padding:10px 16px 7px;font-size:17px;white-space:nowrap;box-shadow:0 4px 0 var(--ink)}}
.pc .price{{font-size:30px}}
.pimg img{{object-position:top}}
</style></head><body>
<header><div class="wrap nav"><a href="../"><img src="../brand/lockup-ink.png" alt="MaryMarii" width="186" height="56"></a>
<nav><a href="../#how">How it works</a><a href="../#free">Free page</a></nav></div></header>
<main class="wrap"><div style="text-align:center;padding:40px 0 0"><h1>Pages that come alive</h1>
<p class="lead" style="margin:12px auto 0;max-width:620px">Print, color, scan with your phone and watch the drawing move. Instant download, no app, no sign-up.</p></div>
<div class="pgrid">{cards}</div></main>
<footer><div class="wrap"><span>© 2026 MaryMariiArt · Blissena OÜ, Estonia</span><span>Checkout and file delivery are provided by Payhip (payments by Stripe).</span></div></footer>
<script data-goatcounter="https://marymarii.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>
</body></html>
"""

if __name__ == "__main__":
    slugs = sys.argv[1:] or list(PRODUCTS)
    for s in slugs:
        os.makedirs(f"shop/{s}", exist_ok=True)
        open(f"shop/{s}/index.html", "w").write(page(s, PRODUCTS[s]))
        print("built shop/%s/index.html" % s)
    open("shop/index.html", "w").write(overview()); print("built shop/index.html")
