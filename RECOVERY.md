# MaryMariiArt – recovery guide (state 24 Nov 2026)

If a chat or workspace is lost, start a new session and say:
"Read RECOVERY.md on branch build-tools of github.com/jyriran/marymarii.com and the MaryMarii project docs, then continue."

## 1. What exists
- **Etsy shop** MaryMariiArt (shop id 51183012). Live: Christmas Dot to Dot (listing 4623775202, €6.50).
  Drafts: ABC A–M (4624015371), ABC N–Z (4624410579). Planned: A–Z combo, 123 Count & Connect.
- **Website** marymarii.com = GitHub repo jyriran/marymarii.com, branch `main`, GitHub Pages (CNAME). Plain HTML/CSS/JS, no build step.
  Sections: hero (animated penguin SVG), how it works, Christmas bundle, ABC sets, who it's for, magic camera (real scan video img/video/real-scan-bear.mp4), FAQ.
- **Magic camera** (web AR, no app) at marymarii.com/scan/?s=<key>[&size=letter]. Every page's QR code points there.
- **Other branches**: `mockup-assets` (page JPGs used for mockups; abc2/ = current ABC pages), `social-week1` (week-1 social pack), `build-tools` (this branch: all generator scripts, no art).
- **JR's Mac**: Desktop/MaryMarii/{1 Christmas Dot to Dot, 2 ABC A-M, 3 ABC N-Z, Social media, Website, Notes, Original zip downloads}. Each bundle folder has PDFs to sell, Etsy listing cards/photos, Mockups, Videos.
- **claude.ai project "MaryMarii"** docs: claude/abc-bundle-plan.md, etsy-listing-*.md, magic-scanner.md, landing-page.md, christmas-bundle-trial.md, claude/RECOVERY-build-guide.md (copy of this file).

## 2. Rules (from JR)
- Never publish, edit live listings, change prices, send messages or start ads without JR's explicit yes in chat. Never enter passwords; JR signs in himself (built-in browser).
- No invented reviews/quotes/testimonials, no fake scarcity. Disclose AI-made imagery (mockup backgrounds are AI; pages and animals are our own code-drawn art).
- Kids: no data collection, no personal info in AR pages. Never show real children's faces or real names (blur names like the one on JR's test page; use made-up names MIA, LIAM, EVA, OTTO, MAX, ROSE, LILY, ZOE). Hands only in videos.
- The name-greeting feature was removed (24 Nov): no listing/site/social text may promise it. Code keeps it behind ?name=1 for tests only.

## 3. Brand / style
- Colours: paper #fbf7f1, ink #2a1c15, muted #6d5d53, red #d65f50, blush #f4e5dd, teal #8cbdb5, sun #ecc06a, grid #e9dfd3.
- Fonts: site = Fraunces (display) + Figtree (body). Listing cards / social / video titles = Gluten (display, rounded) + Figtree. Dotted-paper background on cards.
- Logo files: site brand/ (lockup-ink/white, mark, icon). Name "MaryMariiArt" on Etsy/social, "MaryMarii" lockup on the site.
- Pages: A4 + US Letter PDFs, black & white, dense black symbol border (stars, trees, hearts, circles), title + "My name:" letter boxes, QR strip "Finished? Make it come alive!", footer "© MaryMariiArt · for personal and family use · marymariiart.etsy.com".
- Copy tone: warm, simple, parent-facing; US spelling on Etsy ("color"); ages 4–8 (Christmas), 3–6 (ABC).

## 4. Magic camera architecture (repo scan/)
- scan/index.html + scan/app.js (ES module, three.js + MindAR image tracking, lib/). app.js is cache-busted in index.html (?v=YYYYMMDDx) – bump when changing.
- Per page and size: `targets/<key>-<size>.js` (compiled MindAR target, base64) and `targets/<key>_<size>.json` (region, body/parts polygons in target px at 150 dpi, pivots, motions, eyes/lids, paper sample points, base) and, for drawn characters, `targets/<key>_<size>_ink.png` (2× region, RGBA line art).
- Flow: track page → extract the coloured region from the camera into a render target (normalised by paper colour) → build the character from polygons with that texture → animate (TOON springs: hop, wiggle, spin, yawn…; parts rot/flap/tap/pop) → record video button.
- **Drawn-character mode (data.clean)**: polygons = clean outline through the printed dots (inset to the inner dot edge), ink PNG drawn on top, printed lines in the camera image painted over with the child's colours, thin white gaps filled, thickness layers behind (6 stacked copies), bevel light. All 41 pages use it.
- Tuning constants in app.js: SLOW=0.72 (tempo), HOLD_MS=2200 (keep character when tracking drops), MindAR missTolerance 15 / warmupTolerance 2, limb clamp amp+0.12 for clean characters, lean ×0.6. Flashlight button (torch) where supported.
- Keys: Christmas = hedgehog gift bell stocking snowman gingerbread penguin tree owl santa house bunny fox reindeer bear. ABC = abc-a … abc-z.

## 5. Build pipelines (scripts on this branch)
- Christmas pages: xmas/ (engine.py shapes, chars.py/chars2.py characters, build.py PDFs, gen_ar.py → pages 150 dpi + ardata + test stills). Licensed raster art (santa, snowman, reindeer, bear) lives only in the workspace/Mac, NOT in git.
- ABC pages: abc/ (letters.py stroke skeletons, animals.py 26 procedural animals, build.py `bundle ABCDEFGHIJKLM|NOPQRSTUVWXYZ`, `done`/`done2` finished mockup pages, gen_abc.py AR data). Border seeds: BORDER_SEED in build.py (C,U,V,Z re-seeded) – changing the border changes recognition, recompile targets.
- Compile targets: ar/tools/compile1.html (MindAR compiler) served locally + scripts/compile_abc.py (Playwright). Test recognition: scripts/abctest.py, scripts/tm.py (simulated tilted photos, swiftshader).
- Drawn characters: clean/build_clean.py <keys…> (generic: outline = dot path, parts clipped, ink layer, number removal); clean/build_bear.py (bear with hand-numbered dots + rig parts: head, armR wave, armL); clean/spec.py (hand-read dot paths + flood seeds for santa/snowman/reindeer). Originals of the JSONs before conversion: git history of scan/targets.
- Listing cards: abc/cards*/make_cards.py (Playwright HTML → 2000×2000 JPG, images in cards*/img rendered from the PDFs). Christmas photos: listing/make_photos.py, make_mockups.py, make_photo11.py.
- Mockups: higgsfield-mockups/ (scenes from Higgsfield gpt_image_2_6, compositing comp.py).
- Videos: ffmpeg. Brag reel structure = hook 2.57 s / connect 4 s / color 4 s / scan 7.2 s / end card 3.5 s with the original music (keep durations to keep the beat); Etsy video 1080², 15 s, silent. Name blur: scripts/blur_name_track*.py (OpenCV CSRT tracker).

## 6. Marketing state
- Meta Business Suite: Instagram @marymariiart + Facebook page. Drafts for week 1 (Days 2–6 + "Wait… it moved?!" reel). Boost €2/day, US + Canada. Post ~20:00 Estonian time (1 pm ET).
- Pinterest: 4 boards, 8 pins (link to marymarii.com; Pinterest refused API edits – JR edits by hand; AI-label the mockup pins).
- Etsy: Cyber sale 23 Nov–1 Dec joined; abandoned-cart / thank-you / favourite offers set by JR.

## 7. Next
- ABC: JR swaps photos to the new-border versions + adds a real photo, then publish on his yes; A–Z combo (same 4 PDFs, ~€10.90).
- 123 Count & Connect (numbers 1–20): PDFs built 24 Nov (A4 + Letter, 23 pages: cover, how-to, 20 number pages, colour ideas). Magic camera live for n1…n20 (drawn characters; the animal hops N times while counters 1…N pop up). Etsy listing, cards and mockups still to do. See project doc claude/123-bundle-plan.md.
- 123 build: n123/digits.py (digit stroke skeletons + number words), n123/animals123.py (20 new procedural animals), n123/build123.py (`python3 build123.py bundle`; `python3 build123.py 7` = sample page), n123/gen123.py (AR data → /home/claude/ar/gen123), n123/compile123.py (MindAR targets), then clean/build_clean.py n1 … n20 (needs the JSONs copied to clean/orig first).
- Page n layout: title "7 · seven", name boxes, big dotted number with stroke badges, number word to trace, animal dot-to-dot (right), practice row, counting box (N icons + "Write it" box + ten-frame(s)), QR strip. Border uses digits instead of letters (seed '123-<n>').
