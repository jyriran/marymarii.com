# ABC mockup compositing (runs in the Higgsfield sandbox, ~/abc)
- scenes/s1..s7.png: blank-paper scenes generated with gpt_image_2_6 in Higgsfield (same 7 scenes for A–M and N–Z).
- quads.json: page corner quads per scene (detected with detect.py / detect2.py, then hand-checked).
- pages/: color_X.jpg / bw_X.jpg = out/mk_color_X.png / mk_bw_X.png from abc/build.py `done` / `done2` (A4 at 200 dpi).
  Current copies are on GitHub branch mockup-assets, folder abc2/.
- comp.py (A–M) / compNZ.py (N–Z): warp page into quad, keep the scene's paper shading, keep occluders (hands, clips).
