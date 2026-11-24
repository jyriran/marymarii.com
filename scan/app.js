import * as THREE from 'three';
import './lib/mindar-image.prod.js';
/* Camera field of view (vertical, degrees). MindAR assumes 45, but phone main cameras see about 64 degrees along
   the long side of the picture and about 50 along the short side. ?fov= overrides it for testing. */
const FOV_OVERRIDE = Number(new URLSearchParams(location.search).get('fov')) || 0;

/* ---------- sheet config: each QR code opens ?s=<sheet> (and &size=letter on US Letter pages) ---------- */
const NAMES = { hedgehog: 'Hedgehog', gift: 'Gift Box', bell: 'Bell', stocking: 'Stocking', snowman: 'Snowman', gingerbread: 'Gingerbread Man',
  penguin: 'Penguin', tree: 'Christmas Tree', owl: 'Owl', santa: 'Santa', house: 'Gingerbread House', bunny: 'Bunny', fox: 'Fox', reindeer: 'Reindeer', bear: 'Polar Bear' };
/* ABC Dot to Dot pages: ?s=abc-a … abc-z */
Object.assign(NAMES, {'abc-a': 'Alligator', 'abc-b': 'Bear', 'abc-c': 'Cat', 'abc-d': 'Dog', 'abc-e': 'Elephant', 'abc-f': 'Fish', 'abc-g': 'Giraffe', 'abc-h': 'Hippo', 'abc-i': 'Iguana', 'abc-j': 'Jellyfish', 'abc-k': 'Koala', 'abc-l': 'Lion', 'abc-m': 'Mouse', 'abc-n': 'Narwhal', 'abc-o': 'Octopus', 'abc-p': 'Pig', 'abc-q': 'Quail', 'abc-r': 'Rabbit', 'abc-s': 'Snake', 'abc-t': 'Turtle', 'abc-u': 'Unicorn', 'abc-v': 'Vulture', 'abc-w': 'Whale', 'abc-x': 'X-ray Fish', 'abc-y': 'Yak', 'abc-z': 'Zebra'});
const params = new URLSearchParams(location.search);
const sheetKey = NAMES[params.get('s')] ? params.get('s') : 'penguin';
const paperSize = params.get('size') === 'letter' ? 'letter' : 'a4';
const IS_ABC = sheetKey.startsWith('abc-');
/* Name greeting from the letter boxes: off for now (handwriting on phone cameras isn't reliable enough). ?name=1 turns it on for testing. */
const NAME_READING = new URLSearchParams(location.search).get('name') === '1';
const SHEET = { name: NAMES[sheetKey], mind: `./targets/${sheetKey}-${paperSize}.js`, parts: `targets/${sheetKey}_${paperSize}.json` };

const $ = id => document.getElementById(id);
$('sheet-name').textContent = SHEET.name;
$('start-title').textContent = `Make your ${SHEET.name.toLowerCase()} come alive!`;
$('hint').textContent = `Point the camera at your ${SHEET.name} page`;

/* ---------- renderer & scenes ---------- */
const canvas = $('gl');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: false, preserveDrawingBuffer: false });
renderer.outputColorSpace = THREE.LinearSRGBColorSpace;
renderer.autoClear = false;
renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

const video = $('cam');
let videoTex = null;
const bgScene = new THREE.Scene(), orthoCam = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
const arScene = new THREE.Scene(), arCam = new THREE.Camera();
const overlayScene = new THREE.Scene();
const crop = new THREE.Vector2(1, 1);

const bgMat = new THREE.ShaderMaterial({
  uniforms: { uVideo: { value: null }, uScale: { value: crop } },
  vertexShader: `varying vec2 vUv; uniform vec2 uScale;
    void main(){ vUv = (position.xy / uScale) * 0.5 + 0.5; gl_Position = vec4(position.xy, 0.999, 1.0); }`,
  fragmentShader: `varying vec2 vUv; uniform sampler2D uVideo; void main(){ gl_FragColor = texture2D(uVideo, vUv); }`,
  depthTest: false, depthWrite: false,
});
const bgQuad = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), bgMat);
bgQuad.frustumCulled = false;
bgScene.add(bgQuad);

/* ---------- tracking state ---------- */
let controller = null, P = new THREE.Matrix4(), postMatrix = new THREE.Matrix4();
let mw = 1241, mh = 1754, data = null, targetURL = null;
const anchorM = new THREE.Matrix4();
let tracked = false, lastSeen = 0, updates = 0;
const anchor = new THREE.Group();
anchor.matrixAutoUpdate = false;
anchor.visible = false;
arScene.add(anchor);

/* target px -> anchor-local (MindAR: width = 1 unit, origin at page centre, y up) */
const scaleT = () => mw / data.target.width;
function toLocal(x, y) { const k = scaleT(); return new THREE.Vector2((x * k) / mw - 0.5, (mh / 2 - y * k) / mw); }

/* ---------- extraction: unwarp the child's drawing from the camera image ---------- */
const RT_W = 640;
let rt = null, extractScene = null, extractMat = null, regionUV = null;
const mvp = new THREE.Matrix4();
function buildExtraction() {
  const [x0, y0, x1, y1] = data.region;
  const rtH = Math.round(RT_W * (y1 - y0) / (x1 - x0));
  rt = new THREE.WebGLRenderTarget(RT_W, rtH, { minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, generateMipmaps: false });
  const a = toLocal(x0, y0), b = toLocal(x1, y1);
  extractMat = new THREE.ShaderMaterial({
    uniforms: {
      uVideo: { value: videoTex }, uMVP: { value: mvp },
      uA: { value: a }, uB: { value: b },
      uPaper: { value: data.paper.map(([x, y]) => toLocal(x, y)) },
    },
    vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`,
    fragmentShader: `
      varying vec2 vUv; uniform sampler2D uVideo; uniform mat4 uMVP; uniform vec2 uA; uniform vec2 uB; uniform vec2 uPaper[4];
      vec3 cam(vec2 p){ vec4 c = uMVP * vec4(p, 0.0, 1.0); vec2 uv = c.xy / c.w * 0.5 + 0.5; return texture2D(uVideo, uv).rgb; }
      void main(){
        vec2 p = vec2(mix(uA.x, uB.x, vUv.x), mix(uB.y, uA.y, vUv.y));
        vec3 paper = (cam(uPaper[0]) + cam(uPaper[1]) + cam(uPaper[2]) + cam(uPaper[3])) * 0.25;
        vec3 col = cam(p) / max(paper, vec3(0.25)) * 0.97;
        col = clamp((col - 0.04) * 1.08, 0.0, 1.0);           // a little contrast so crayon pops
        gl_FragColor = vec4(col, 1.0);
      }`,
  });
  extractScene = new THREE.Scene();
  const q = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), extractMat);
  q.frustumCulled = false;
  extractScene.add(q);
  regionUV = (x, y) => new THREE.Vector2((x - x0) / (x1 - x0), 1 - (y - y0) / (y1 - y0));
}
function extract() {
  mvp.copy(P).multiply(anchorM);
  renderer.setRenderTarget(rt);
  renderer.clear();
  renderer.render(extractScene, orthoCam);
  renderer.setRenderTarget(null);
}

/* ---------- the character, built from the extracted texture ---------- */
const root = new THREE.Group(), bodyG = new THREE.Group();
const toon = new THREE.Group(); toon.matrixAutoUpdate = false; // squash, stretch, lean and hop live here
const pivots = {};
let shadow = null, patch = null, patchMat = null, lids = [], snow = null, smoke = null, B = null, BP = null;
const rigParts = [];

function partGeometry(polys, origin) {
  const shapes = polys.map(poly => new THREE.Shape(poly.map(([x, y]) => toLocal(x, y))));
  const g = new THREE.ShapeGeometry(shapes);
  const pos = g.attributes.position, uv = g.attributes.uv;
  const k = scaleT();
  for (let i = 0; i < pos.count; i++) {
    const lx = pos.getX(i), ly = pos.getY(i);
    const tx = ((lx + 0.5) * mw) / k, ty = (mh / 2 - ly * mw) / k;
    const u = regionUV(tx, ty);
    uv.setXY(i, u.x, u.y);
  }
  g.translate(-origin.x, -origin.y, 0);
  return g;
}
/* cut-out: keep the child's coloring, drop the printed dots, numbers and white paper around the edge.
   Worked out once on the CPU right after the capture, stored as R = alpha, G = soft alpha (bevel), B = drawn outline. */
const BAND = 20;           // target px (150 dpi): soft edge zone where dots, numbers and paper get keyed out
let inkTex = null, CLEAN = false, maskTex = null, sideTex = null, polyFill = null, polySoft = null, MW = 0, MH = 0;
function boxBlur(a, W, H, r, passes) {
  let b = new Float32Array(W * H);
  const pass = (inp, out, horiz) => {
    const n = horiz ? W : H, m = horiz ? H : W, k = 1 / (2 * r + 1);
    for (let j = 0; j < m; j++) {
      const at = i => horiz ? j * W + Math.min(n - 1, Math.max(0, i)) : Math.min(n - 1, Math.max(0, i)) * W + j;
      let acc = 0; for (let i = -r; i <= r; i++) acc += inp[at(i)];
      for (let i = 0; i < n; i++) { out[horiz ? j * W + i : i * W + j] = acc * k; acc += inp[at(i + r + 1)] - inp[at(i - r)]; }
    }
  };
  a = Float32Array.from(a);
  for (let it = 0; it < passes; it++) { pass(a, b, true); pass(b, a, false); }
  return a;
}
function writeMask(R, G, Bc) {
  const px = maskTex.image.data;
  for (let i = 0; i < MW * MH; i++) { const o = i * 4; px[o] = R[i] * 255; px[o + 1] = G[i] * 255; px[o + 2] = Bc[i] * 255; px[o + 3] = 255; }
  maskTex.needsUpdate = true;
}
function buildMask() {
  const [x0, y0, x1, y1] = data.region; MW = RT_W; MH = rt.height; const s = MW / (x1 - x0);
  const c = document.createElement('canvas'); c.width = MW; c.height = MH;
  const g = c.getContext('2d'); g.fillStyle = '#fff';
  const polys = [...data.body, ...data.parts.flatMap(p => p.polys)];
  for (const poly of polys) { g.beginPath(); poly.forEach(([x, y], i) => g[i ? 'lineTo' : 'moveTo']((x - x0) * s, (y - y0) * s)); g.closePath(); g.fill(); }
  const src = g.getImageData(0, 0, MW, MH).data;
  polyFill = new Float32Array(MW * MH);
  for (let j = 0; j < MH; j++) for (let i = 0; i < MW; i++) polyFill[j * MW + i] = src[((MH - 1 - j) * MW + i) * 4] / 255;  // texture row 0 = bottom
  const sigma = BAND * s, r = Math.max(1, Math.round((Math.sqrt(4 * sigma * sigma + 1) - 1) / 2));
  polySoft = boxBlur(polyFill, MW, MH, r, 3);
  maskTex = new THREE.DataTexture(new Uint8Array(MW * MH * 4), MW, MH, THREE.RGBAFormat);
  maskTex.minFilter = maskTex.magFilter = THREE.LinearFilter;
  sideTex = new THREE.DataTexture(new Uint8Array(MW * MH * 4).fill(150), MW, MH, THREE.RGBAFormat);
  sideTex.minFilter = sideTex.magFilter = THREE.LinearFilter; sideTex.needsUpdate = true;
  const inner = CLEAN ? polyFill : polySoft.map(v => v > 0.98 ? 1 : 0);   // clean characters: the drawn shape is the edge
  writeMask(inner, boxBlur(inner, MW, MH, CLEAN ? 6 : 4, 2), new Float32Array(MW * MH));
}
function finalizeCutout() {
  const N = MW * MH, px = new Uint8Array(N * 4);
  renderer.readRenderTargetPixels(rt, 0, 0, MW, MH, px);
  const keep = new Float32Array(N), open = new Uint8Array(N);
  for (let i = 0; i < N; i++) {
    const r = px[i * 4], g = px[i * 4 + 1], b = px[i * 4 + 2], hi = Math.max(r, g, b), chroma = hi - Math.min(r, g, b);
    keep[i] = Math.min(1, Math.max(0, (chroma - 12) / 24)) * Math.min(1, Math.max(0, (hi - 95) / 50));  // crayon (even pale pink), not ink
    open[i] = hi > 165 && chroma < 22 ? 1 : 0;                                                       // bare paper
  }
  if (CLEAN) { sideColors(px, keep); return; }   // fixed outline: nothing to cut, just the colors
  // crayon strokes leave little white gaps: only paper with no coloring nearby counts as open
  const keepAvg = boxBlur(keep, MW, MH, 4, 2);
  // and only near the outline: deep inside the drawing nothing is ever cut away
  for (let i = 0; i < N; i++) if (keepAvg[i] > 0.12 || polySoft[i] > 0.97) open[i] = 0;
  // flood the bare paper in from outside the outline: white the child left open inside the drawing stays,
  // white that leaks out between the dots goes
  const out = new Uint8Array(N), q = new Int32Array(N); let qh = 0, qt = 0;
  for (let i = 0; i < N; i++) if (polyFill[i] < 0.5) { out[i] = 1; q[qt++] = i; }
  while (qh < qt) {
    const i = q[qh++], x = i % MW, y = (i / MW) | 0;
    const nb = [x > 0 ? i - 1 : -1, x < MW - 1 ? i + 1 : -1, y > 0 ? i - MW : -1, y < MH - 1 ? i + MW : -1];
    for (const j of nb) if (j >= 0 && !out[j] && open[j]) { out[j] = 1; q[qt++] = j; }
  }
  // the printed dots and numbers sit right against that paper: drop anything uncolored next to it
  const near = boxBlur(Float32Array.from(out), MW, MH, Math.max(2, Math.round(RT_W / (data.region[2] - data.region[0]) * 11)), 1);
  const alpha0 = new Float32Array(N);
  for (let i = 0; i < N; i++) {
    if (out[i]) continue;
    alpha0[i] = near[i] > 0.01 && polySoft[i] < 0.97 ? Math.min(1, Math.max(0, (keepAvg[i] - 0.3) / 0.25)) : 1;
  }
  const sm = boxBlur(alpha0, MW, MH, 6, 3);                       // round off the bites the dots leave: smooth, flowing edge
  const alpha = sm.map(v => Math.min(1, Math.max(0, (v - 0.5) / 0.08 + 0.5)));
  const nearEdge = boxBlur(alpha, MW, MH, 3, 2);
  const ink = alpha.map((v, i) => v * Math.min(1, Math.max(0, (0.97 - nearEdge[i]) / 0.2)));
  writeMask(alpha, boxBlur(alpha, MW, MH, 4, 2), ink);
  sideColors(px, keep);
}
/* the child's colors smoothed, without the printed lines: for the thickness, and to paint over the printed ink */
function sideColors(px, keep) {
  const N = MW * MH, sp = sideTex.image.data;
  for (let ch = 0; ch < 3; ch++) {
    const w = new Float32Array(N), v = new Float32Array(N);
    for (let i = 0; i < N; i++) { const hi = Math.max(px[i * 4], px[i * 4 + 1], px[i * 4 + 2]); const k = keep[i] + (hi > 150 ? 0.03 : 0); w[i] = k + 1e-4; v[i] = px[i * 4 + ch] * w[i]; }
    const bw = boxBlur(w, MW, MH, 6, 2), bv = boxBlur(v, MW, MH, 6, 2);
    for (let i = 0; i < N; i++) sp[i * 4 + ch] = bv[i] / bw[i];
  }
  for (let i = 0; i < N; i++) sp[i * 4 + 3] = 255;
  sideTex.needsUpdate = true;
}
const CUT_VS = `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`;
const CUT_FS = `varying vec2 vUv; uniform sampler2D uMap; uniform sampler2D uMask; uniform sampler2D uSideMap; uniform sampler2D uInk; uniform float uClean; uniform vec2 uPx; uniform float uSide;
  void main(){
    vec3 k = texture2D(uMask, vUv).rgb;
    if (k.r < 0.02) discard;
    vec3 c = texture2D(uMap, vUv).rgb;
    if (uSide > 0.5) { gl_FragColor = vec4(texture2D(uSideMap, vUv).rgb * 0.62, uClean > 0.5 ? k.r : smoothstep(0.6, 0.75, k.g)); return; }
    if (uClean > 0.5) {   // printed lines in the camera image give way to the child's color; crisp lines go on top
      vec3 sc = texture2D(uSideMap, vUv).rgb;
      c = mix(c, sc, 1.0 - smoothstep(0.38, 0.62, max(c.r, max(c.g, c.b))));
      // a thin white gap between the coloring and the line gets the color next to it
      float edge = 1.0 - smoothstep(0.7, 0.93, k.g), white = smoothstep(0.72, 0.88, min(c.r, min(c.g, c.b)));
      c = mix(c, sc, edge * white);
    }
    // bevel: light from the top left falls on a rounded edge
    vec2 e = uPx * 3.0;
    vec2 n = vec2(texture2D(uMask, vUv + vec2(e.x, 0.0)).g - texture2D(uMask, vUv - vec2(e.x, 0.0)).g,
                  texture2D(uMask, vUv + vec2(0.0, e.y)).g - texture2D(uMask, vUv - vec2(0.0, e.y)).g);
    float lit = dot(n, normalize(vec2(1.0, -1.0))) * 2.0;
    float rim = 1.0 - smoothstep(0.55, 1.0, k.g);
    c = c * (1.0 - 0.2 * rim) + vec3(max(0.0, lit)) * 0.3 - vec3(max(0.0, -lit)) * 0.22;
    c = mix(c, vec3(0.13, 0.1, 0.1), k.b * 0.9);                 // a clean drawn outline where the dots used to be
    if (uClean > 0.5) { vec4 ik = texture2D(uInk, vUv); c = mix(c, ik.rgb, ik.a); }
    gl_FragColor = vec4(clamp(c, 0.0, 1.0), k.r);
  }`;
const LAYERS = 6, DEPTH = 0.014;   // thickness behind the cut-out, in page widths
function cutMat(side) {
  return new THREE.ShaderMaterial({
    uniforms: { uMap: { value: rt.texture }, uMask: { value: maskTex }, uSideMap: { value: sideTex }, uInk: { value: inkTex }, uClean: { value: CLEAN ? 1 : 0 }, uPx: { value: new THREE.Vector2(1 / RT_W, 1 / rt.height) }, uSide: { value: side ? 1 : 0 } },
    vertexShader: CUT_VS, fragmentShader: CUT_FS, transparent: true, depthTest: false, depthWrite: false, side: THREE.DoubleSide,
  });
}
function partMesh(polys, origin, order) {
  const geo = partGeometry(polys, origin), grp = new THREE.Group();
  const side = cutMat(true);
  for (let i = LAYERS; i >= 1; i--) {             // stacked copies behind = a thick, chunky cut-out
    const l = new THREE.Mesh(geo, side); l.position.z = -DEPTH * i / LAYERS; l.renderOrder = 3; grp.add(l);
  }
  const m = new THREE.Mesh(geo, cutMat(false)); m.renderOrder = order; grp.add(m);
  return grp;
}
function dot(r, color, opacity) {
  const c = document.createElement('canvas'); c.width = c.height = 64;
  const g = c.getContext('2d'), gr = g.createRadialGradient(32, 32, 0, 32, 32, 32);
  gr.addColorStop(0, color); gr.addColorStop(1, 'rgba(0,0,0,0)');
  g.fillStyle = gr; g.fillRect(0, 0, 64, 64);
  const t = new THREE.CanvasTexture(c);
  return new THREE.MeshBasicMaterial({ map: t, transparent: true, opacity, depthTest: false, depthWrite: false });
}

function buildCharacter() {
  B = toLocal(...data.base);                                   // feet: where the character stands on the page
  BP = data.bodyPivot ? toLocal(...data.bodyPivot) : B.clone(); // body pivot (the top for swinging bells and stockings)
  root.position.set(B.x, B.y, 0.002);
  anchor.add(root);
  root.add(toon); toon.add(bodyG);
  bodyG.position.set(BP.x - B.x, BP.y - B.y, 0); bodyG.userData.base = bodyG.position.clone();

  // paper patch: covers the drawing on the page once it has jumped off
  const sil = data.silhouette;
  patchMat = new THREE.ShaderMaterial({
    uniforms: { uVideo: { value: videoTex }, uMVP: { value: mvp }, uPaper: { value: data.paper.map(([x, y]) => toLocal(x, y)) }, uOpacity: { value: 0 } },
    vertexShader: `varying vec2 vP; void main(){ vP = position.xy; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
    fragmentShader: `varying vec2 vP; uniform sampler2D uVideo; uniform mat4 uMVP; uniform vec2 uPaper[4]; uniform float uOpacity;
      vec3 cam(vec2 p){ vec4 c = uMVP * vec4(p, 0.0, 1.0); return texture2D(uVideo, c.xy / c.w * 0.5 + 0.5).rgb; }
      void main(){
        // paper colour follows the light across the page: blend the four blank corners by position
        float u = clamp((vP.x - uPaper[0].x) / (uPaper[1].x - uPaper[0].x), 0.0, 1.0);
        float v = clamp((vP.y - uPaper[0].y) / (uPaper[2].y - uPaper[0].y), 0.0, 1.0);
        vec3 top = mix(cam(uPaper[0]), cam(uPaper[1]), u), bot = mix(cam(uPaper[2]), cam(uPaper[3]), u);
        gl_FragColor = vec4(mix(top, bot, v), uOpacity);
      }`,
    transparent: true, depthTest: false, depthWrite: false,
  });
  // grow the patch a little around each outline so hand shake never lets the printed drawing peek out
  const grow = poly => { const cx = poly.reduce((a, p) => a + p[0], 0) / poly.length, cy = poly.reduce((a, p) => a + p[1], 0) / poly.length;
    return poly.map(([x, y]) => { const dx = x - cx, dy = y - cy, d = Math.hypot(dx, dy) || 1, k = (d + 14) / d; return [cx + dx * k, cy + dy * k]; }); };
  const pg = new THREE.ShapeGeometry(sil.map(poly => new THREE.Shape(grow(poly).map(([x, y]) => toLocal(x, y)))));
  patch = new THREE.Mesh(pg, patchMat);
  patch.position.z = 0.0005; patch.renderOrder = 1;
  patch.visible = false;   // the printed drawing stays on the paper; a thick copy pops out of it
  anchor.add(patch);

  const sw = (data.region[2] - data.region[0]) * scaleT() / mw;
  shadow = new THREE.Mesh(new THREE.PlaneGeometry(sw * 0.8, sw * 0.16), dot(1, 'rgba(0,0,0,1)', 0.32));
  shadow.position.set(B.x, B.y + 0.01, 0.001); shadow.renderOrder = 2;
  anchor.add(shadow);


  buildMask();
  bodyG.add(partMesh(data.body, BP, 6));
  for (const p of data.parts) {
    const o = toLocal(...p.pivot), parentOrigin = p.parent === 'root' ? B : BP;
    const piv = new THREE.Group(); piv.position.set(o.x - parentOrigin.x, o.y - parentOrigin.y, 0); piv.userData = { base: piv.position.clone(), motion: p.motion };
    piv.add(partMesh(p.polys, o, p.order));
    (p.parent === 'root' ? toon : bodyG).add(piv); piv.userData.a = 0; piv.userData.va = 0; rigParts.push(piv);
  }
  // eyelids take their color from the child's coloring next to each eye
  data.eyes.forEach(([x, y, r], i) => {
    const o = toLocal(x, y), rr = (r * scaleT() / mw) * 1.25;
    const s = regionUV(...data.lid[i]);
    const m = new THREE.Mesh(new THREE.CircleGeometry(rr, 24), new THREE.ShaderMaterial({
      uniforms: { uMap: { value: rt.texture }, uS: { value: s } },
      vertexShader: `void main(){ gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }`,
      fragmentShader: `uniform sampler2D uMap; uniform vec2 uS; void main(){ gl_FragColor = vec4(texture2D(uMap, uS).rgb, 1.0); }`,
      depthTest: false, depthWrite: false,
    }));
    m.position.set(o.x - BP.x, o.y - BP.y + rr * 0.15, 0); m.renderOrder = 9; m.visible = false;
    bodyG.add(m); lids.push(m);
  });
  // chimney smoke
  if (data.smoke) {
    const o = toLocal(...data.smoke), N = 7, pos = new Float32Array(N * 3);
    const g = new THREE.BufferGeometry(); g.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    smoke = new THREE.Points(g, new THREE.PointsMaterial({ size: 0.07, color: 0xdcdcdc, map: dot(1, 'rgba(255,255,255,1)', 1).map, transparent: true, depthTest: false, depthWrite: false, opacity: 0 }));
    smoke.position.set(o.x - BP.x, o.y - BP.y, 0); smoke.renderOrder = 7; smoke.frustumCulled = false;
    bodyG.add(smoke);
  }
  // snow
  const N = 46, pos = new Float32Array(N * 3), seed = [];
  for (let i = 0; i < N; i++) { seed.push([Math.random() * 0.9 - 0.45, Math.random() * 1.0, (Math.random() - 0.5) * 0.25, 0.08 + Math.random() * 0.1]); }
  const sg = new THREE.BufferGeometry(); sg.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  const sc = document.createElement('canvas'); sc.width = sc.height = 32;
  const sx = sc.getContext('2d'); const grd = sx.createRadialGradient(16, 16, 0, 16, 16, 16);
  grd.addColorStop(0, 'rgba(255,255,255,1)'); grd.addColorStop(.5, 'rgba(255,255,255,.8)'); grd.addColorStop(1, 'rgba(255,255,255,0)');
  sx.fillStyle = grd; sx.fillRect(0, 0, 32, 32);
  snow = new THREE.Points(sg, new THREE.PointsMaterial({ size: IS_ABC ? 0.028 : 0.034, color: IS_ABC ? 0xffd34d : 0x9fd3ff, map: new THREE.CanvasTexture(sc), transparent: true, depthTest: false, depthWrite: false, opacity: 0 }));
  snow.userData.seed = seed; snow.renderOrder = 10; snow.frustumCulled = false;
  root.add(snow);
  root.visible = false; shadow.visible = false;
}

/* ---------- watermark burned into the recording ---------- */
let wm = null;
function buildWatermark() {
  const c = document.createElement('canvas'); c.width = 512; c.height = 112;
  const g = c.getContext('2d');
  g.fillStyle = 'rgba(42,28,21,.62)'; g.beginPath(); g.roundRect(4, 8, 504, 96, 48); g.fill();
  g.fillStyle = '#e0574c'; g.beginPath(); g.arc(58, 56, 14, 0, Math.PI * 2); g.fill();
  g.fillStyle = '#fffcf6'; g.font = '800 46px Gluten, "Chalkboard SE", "Comic Sans MS", cursive'; g.textBaseline = 'middle';
  g.fillText('MaryMariiArt', 86, 60);
  const t = new THREE.CanvasTexture(c);
  wm = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ map: t, transparent: true, depthTest: false }));
  overlayScene.add(wm);
}
function layoutWatermark() {
  if (!wm) return;
  const w = canvas.clientWidth, h = canvas.clientHeight;
  const pxW = Math.min(200, w * 0.42), pxH = pxW * 112 / 512;
  wm.scale.set(pxW / w * 2, pxH / h * 2, 1);
  wm.position.set(1 - (pxW / 2 + 14) / w * 2, -1 + (pxH / 2 + 14) / h * 2, 0);
}

/* ---------- layout ---------- */
function resize() {
  const w = window.innerWidth, h = window.innerHeight;
  renderer.setSize(w, h, false);
  if (video.videoWidth) {
    const va = video.videoWidth / video.videoHeight, sa = w / h;
    if (va > sa) crop.set(va / sa, 1); else crop.set(1, sa / va);
  }
  const C = new THREE.Matrix4().makeScale(crop.x, crop.y, 1);
  arCam.projectionMatrix.copy(C).multiply(P);
  arCam.projectionMatrixInverse.copy(arCam.projectionMatrix).invert();
  layoutWatermark();
}
window.addEventListener('resize', resize);

/* ---------- name reading (on this phone only) + speech bubble ---------- */
let nameRT = null, nameScene = null, nameInfo = null, childName = null, ocrWorker = null, ocrLoading = null;
const NAME_SCALE = 1.5;
const PADX = 80, PADY = 70;               // extra margin (target px) so we can snap to the printed boxes
function buildNameReader() {
  if (!data.nameBoxes) return;
  const bx = data.nameBoxes;
  const X0 = bx[0][0] - PADX, Y0 = Math.min(...bx.map(b => b[1])) - PADY, X1 = bx[bx.length - 1][2] + PADX, Y1 = Math.max(...bx.map(b => b[3])) + PADY;
  data.nameRegion = [X0, Y0, X1, Y1];
  nameRT = new THREE.WebGLRenderTarget(Math.round((X1 - X0) * NAME_SCALE), Math.round((Y1 - Y0) * NAME_SCALE), { minFilter: THREE.LinearFilter, magFilter: THREE.LinearFilter, generateMipmaps: false });
  const m = new THREE.ShaderMaterial({ uniforms: { ...extractMat.uniforms, uA: { value: toLocal(X0, Y0) }, uB: { value: toLocal(X1, Y1) } },
    vertexShader: extractMat.vertexShader, fragmentShader: extractMat.fragmentShader });
  nameScene = new THREE.Scene();
  const q = new THREE.Mesh(new THREE.PlaneGeometry(2, 2), m); q.frustumCulled = false; nameScene.add(q);
}
/* find the printed boxes in the grabbed strip: the empty inside of each square is a white blob of known size */
/* Find the row of printed boxes near where tracking says it is: its two long horizontal edges give the tilt
   and the height, then the twenty vertical edges give the exact position. Returns box interiors as rotated rects. */
function findBoxes(g, w, h) {
  const S = NAME_SCALE, nb = data.nameBoxes;
  const bh = (nb[0][3] - nb[0][1]) * S, edges = nb.flatMap(b => [(b[0] - nb[0][0]) * S, (b[2] - nb[0][0]) * S]);
  // dark = darker than the neighbourhood (box lines are faint at camera resolution)
  const R = 12, I = new Float64Array((w + 1) * (h + 1));
  for (let y = 0; y < h; y++) { let row = 0; for (let x = 0; x < w; x++) { row += g[y * w + x]; I[(y + 1) * (w + 1) + x + 1] = I[y * (w + 1) + x + 1] + row; } }
  const xs = [], ys = [];
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const x0 = Math.max(0, x - R), x1 = Math.min(w, x + R + 1), y0 = Math.max(0, y - R), y1 = Math.min(h, y + R + 1);
    const mean = (I[y1 * (w + 1) + x1] - I[y0 * (w + 1) + x1] - I[y1 * (w + 1) + x0] + I[y0 * (w + 1) + x0]) / ((x1 - x0) * (y1 - y0));
    if (g[y * w + x] < mean * 0.93) { xs.push(x); ys.push(y); }
  }
  const expR = PADY * S, expC = PADX * S;
  let best = null;
  for (let th = -4; th <= 4.01; th += 0.5) {
    const t = th * Math.PI / 180, sn = Math.sin(t), cs = Math.cos(t);
    const H = new Float32Array(h + w + 2), off = w;
    for (let i = 0; i < xs.length; i++) { const r = Math.round(-xs[i] * sn + ys[i] * cs) + off; if (r >= 0 && r < H.length) H[r]++; }
    const Hs = (r) => (H[r - 1] || 0) + (H[r] || 0) + (H[r + 1] || 0);
    for (let r1 = Math.round(expR - 50); r1 <= expR + 50; r1++) for (let s = Math.round(bh * 0.88); s <= bh * 1.12; s++) {
      const sc = Hs(r1 + off) + Hs(r1 + s + off);
      if (!best || sc > best.sc) best = { sc, th, r1, s };
    }
  }
  if (!best) return null;
  const t = best.th * Math.PI / 180, sn = Math.sin(t), cs = Math.cos(t), k = best.s / bh;
  const Hc = new Float32Array(2 * w + h);
  for (let i = 0; i < xs.length; i++) {
    const r = -xs[i] * sn + ys[i] * cs;
    if (r > best.r1 + 0.15 * best.s && r < best.r1 + 0.85 * best.s) { const c = Math.round(xs[i] * cs + ys[i] * sn) + h; if (c >= 0 && c < Hc.length) Hc[c]++; }
  }
  const Hcs = (c) => (Hc[c - 1] || 0) + (Hc[c] || 0) + (Hc[c + 1] || 0);
  let bc = null;
  for (let c0 = Math.round(expC - 70); c0 <= expC + 70; c0++) {
    let sc = 0; for (const e of edges) sc += Hcs(Math.round(c0 + e * k) + h);
    if (!bc || sc > bc.sc) bc = { sc, c0 };
  }
  // quality check: the vertical edges must really be there
  const lineStrength = bc.sc / edges.length;
  const boxes = nb.map(b => ({ c0: bc.c0 + (b[0] - nb[0][0]) * S * k, c1: bc.c0 + (b[2] - nb[0][0]) * S * k, r0: best.r1, r1: best.r1 + best.s }));
  return { boxes, rot: { sn, cs }, angle: best.th, scale: +k.toFixed(3), lineStrength: +lineStrength.toFixed(1) };
}
/* sample the strip in the row's rotated frame */
function sampleRot(g, w, h, rot, c, r) {
  const x = c * rot.cs - r * rot.sn, y = c * rot.sn + r * rot.cs;
  const xi = Math.round(x), yi = Math.round(y);
  return (xi < 0 || yi < 0 || xi >= w || yi >= h) ? 1 : g[yi * w + xi];
}
let stripDim = false; const DIM_PAPER = Number(new URLSearchParams(location.search).get('dim')) || 0.9;
function grabName() {
  mvp.copy(P).multiply(anchorM);
  renderer.setRenderTarget(nameRT); renderer.clear(); renderer.render(nameScene, orthoCam); renderer.setRenderTarget(null);
  const w = nameRT.width, h = nameRT.height, px = new Uint8Array(w * h * 4);
  renderer.readRenderTargetPixels(nameRT, 0, 0, w, h, px);
  const g = new Float32Array(w * h);           // grey, top row first
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const i = ((h - 1 - y) * w + x) * 4; g[y * w + x] = (px[i] * 0.299 + px[i + 1] * 0.587 + px[i + 2] * 0.114) / 255;
  }
  // stretch to the paper's own white and the ink's black, so dim or warm lamp light reads like daylight
  const smp = []; for (let i = 0; i < g.length; i += 7) smp.push(g[i]); smp.sort((a, b) => a - b);
  const lo = smp[Math.floor(smp.length * 0.02)], hi = smp[Math.floor(smp.length * 0.9)], span = Math.max(0.08, hi - lo);
  stripDim = hi < DIM_PAPER; window.__paperHi = hi;                          // only correct pages that are actually dim; daylight pages stay as they are
  if (stripDim) for (let i = 0; i < g.length; i++) g[i] = Math.min(1, Math.max(0, (g[i] - lo) / span * 0.92 + 0.04));
  return { g, w, h };
}
function loadOCR() {
  if (ocrLoading) return ocrLoading;
  const base = new URL('./ocr/', location.href).href;
  ocrLoading = import('./ocr/tesseract.esm.min.js').then(async T => {
    const createWorker = T.createWorker || T.default.createWorker;
    ocrWorker = await createWorker('eng', 1, { workerPath: base + 'worker.min.js', corePath: base, langPath: base, gzip: true });
    await ocrWorker.setParameters({ tessedit_pageseg_mode: '8', tessedit_char_whitelist: 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz' });
    return ocrWorker;
  }).catch(e => { console.warn('OCR unavailable', e); return null; });
  return ocrLoading;
}
async function readNameOnce() {
  nameInfo = { status: 'reading' };
  if (!nameRT) { nameInfo = { status: 'no-boxes' }; return; }
  const { g, w, h } = grabName();
  const found = findBoxes(g, w, h);
  if (window.__debugStrip) { const c = document.createElement('canvas'); c.width = w; c.height = h; const x = c.getContext('2d'), im = x.createImageData(w, h); for (let i = 0; i < w * h; i++) { const v = g[i] * 255; im.data[i * 4] = im.data[i * 4 + 1] = im.data[i * 4 + 2] = v; im.data[i * 4 + 3] = 255; } x.putImageData(im, 0, 0); window.__debugStrip = c.toDataURL(); }
  if (!found || found.lineStrength < 4) { nameInfo = { status: 'boxes-not-found', ...(found ? { lineStrength: found.lineStrength } : {}) }; return; }
  const ink = [], cells = [];
  for (const b of found.boxes) {                       // box interior, inset to stay clear of the printed lines
    const ic = (b.c1 - b.c0) * 0.15, ir = (b.r1 - b.r0) * 0.13;
    const cw = Math.max(4, Math.round(b.c1 - b.c0 - 2 * ic)), ch = Math.max(4, Math.round(b.r1 - b.r0 - 2 * ir));
    const cell = new Float32Array(cw * ch);
    for (let y = 0; y < ch; y++) for (let x = 0; x < cw; x++) cell[y * cw + x] = sampleRot(g, w, h, found.rot, b.c0 + ic + x, b.r0 + ir + y);
    cells.push({ cell, cw, ch });
  }
  // adaptive ink level: halfway between this page's paper and the darkest pen strokes inside the boxes
  const all = []; cells.forEach(c => { for (let i = 0; i < c.cell.length; i += 3) all.push(c.cell[i]); }); all.sort((a, b) => a - b);
  const paperV = all[Math.floor(all.length * 0.7)], inkV = all[Math.floor(all.length * 0.01)], contrast = paperV - inkV;
  const T = contrast > 0.18 ? (paperV + inkV) / 2 : 0.5, TV = contrast > 0.18 ? 0.17 * contrast : 0.1;
  cells.forEach(c => { let dark = 0; for (let i = 0; i < c.cell.length; i++) if (c.cell[i] < T) dark++; ink.push(dark / c.cell.length); });
  const inkThr = Math.max(0.05, 0.22 * Math.max(...ink));    // relative to how bold this child's letters are
  const filled = ink.map(v => v > inkThr);
  let n = 0; while (n < filled.length && filled[n]) n++;
  nameInfo = { status: 'checked', T: +T.toFixed(2), contrast: +contrast.toFixed(2), angle: found.angle, scale: found.scale, lineStrength: found.lineStrength, ink: ink.map(v => +v.toFixed(3)), letters: n };
  if (n < 2 || filled.slice(n).some(Boolean)) { nameInfo.status = 'no-name'; return; }
  if (ink.slice(0, n).some(v => v > 0.6)) { nameInfo.status = 'messy'; return; }   // scribbles fill boxes far more than letters do
  // tidy word image: each letter in black on white, side by side
  const H = 72, gap = 16, pad = 24;
  const cv = document.createElement('canvas'), cx = cv.getContext('2d');
  const widths = cells.slice(0, n).map(c => Math.round(c.cw * H / c.ch));
  cv.width = widths.reduce((s, v) => s + v + gap, pad * 2); cv.height = H + pad * 2;
  cx.fillStyle = '#fff'; cx.fillRect(0, 0, cv.width, cv.height);
  let ox = pad;
  cells.slice(0, n).forEach(({ cell, cw, ch }, i) => {
    const tmp = document.createElement('canvas'); tmp.width = cw; tmp.height = ch;
    const t = tmp.getContext('2d'), img = t.createImageData(cw, ch);
    for (let k = 0; k < cw * ch; k++) { const v = cell[k] < T + 0.05 * contrast ? 0 : 255; img.data[k * 4] = img.data[k * 4 + 1] = img.data[k * 4 + 2] = v; img.data[k * 4 + 3] = 255; }
    t.putImageData(img, 0, 0);
    cx.drawImage(tmp, ox, pad, widths[i], H); ox += widths[i] + gap;
  });
  nameInfo.image = cv;
  const worker = await loadOCR();
  if (!worker) { nameInfo.status = 'ocr-unavailable'; return; }
  const { data: r } = await worker.recognize(cv, {}, { text: true, blocks: true });
  const syms = [];
  (r.blocks || []).forEach(b => b.paragraphs.forEach(p => p.lines.forEach(l => l.words.forEach(wd => wd.symbols.forEach(s => syms.push(s))))));
  const text = syms.map(s => s.text).join('');
  const minConf = syms.length ? Math.min(...syms.map(s => s.confidence)) : 0;
  Object.assign(nameInfo, { text, minConf: Math.round(minConf), symbols: syms.map(s => [s.text, Math.round(s.confidence)]) });
  const looksLikeName = /^([A-Z]+|[A-Z]?[a-z]+)$/.test(text) && !/(.)\1\1/i.test(text) && (text.length < 3 || /[aeiouy]/i.test(text));
  nameInfo.looksLikeName = looksLikeName;
  // second opinion: read the word again from a darker and a lighter version of the cut-out; all readings must match
  let agree = false;
  if (text.length === n && looksLikeName && minConf >= NAME_MAYBE_CONF) {
    const variants = [];
    for (const thr of [T - TV, T + TV]) {
      const v = document.createElement('canvas'); v.width = cv.width; v.height = cv.height; const vx = v.getContext('2d');
      vx.fillStyle = '#fff'; vx.fillRect(0, 0, v.width, v.height);
      let o = pad;
      cells.slice(0, n).forEach(({ cell, cw, ch }, i) => {
        const tmp = document.createElement('canvas'); tmp.width = cw; tmp.height = ch; const tx = tmp.getContext('2d'), im = tx.createImageData(cw, ch);
        for (let q = 0; q < cw * ch; q++) { const val = cell[q] < thr ? 0 : 255; im.data[q * 4] = im.data[q * 4 + 1] = im.data[q * 4 + 2] = val; im.data[q * 4 + 3] = 255; }
        tx.putImageData(im, 0, 0); vx.drawImage(tmp, o, pad, widths[i], H); o += widths[i] + gap;
      });
      const { data: rv } = await worker.recognize(v);
      variants.push((rv.text || '').replace(/[^A-Za-z]/g, ''));
    }
    agree = variants.every(t => t.toLowerCase() === text.toLowerCase());
    nameInfo.variants = variants.join('/');
  }
  nameInfo.agree = agree; nameInfo.status = agree ? 'candidate' : 'unsure';
  // fingerprint of the cut-out letters, so the same camera frame is never counted twice
  const sig = []; cells.slice(0, n).forEach(({ cell, cw, ch }) => { for (let y = 0; y < 8; y++) for (let x = 0; x < 6; x++) sig.push(cell[Math.floor((y + 0.5) * ch / 8) * cw + Math.floor((x + 0.5) * cw / 6)]); });
  return { text, minConf, agree, sig };
}
const NAME_MAYBE_CONF = 90;
/* keep looking for ~12 s: accept one very sure reading, or the same reading from two separate camera frames */
let readToken = 0;
/* ?debug=1 shows what the name reader saw, for testing on a real phone */
const DEBUG = new URLSearchParams(location.search).get('debug') === '1';
let dbg = null;
function showDebug() {
  if (!DEBUG) return;
  if (!dbg) { dbg = document.createElement('div'); dbg.style.cssText = 'position:fixed;left:8px;right:8px;top:70px;z-index:99;background:rgba(0,0,0,.75);color:#fff;font:12px/1.35 monospace;padding:8px;border-radius:10px;pointer-events:none;white-space:pre-wrap'; document.body.appendChild(dbg); }
  const i = nameInfo || {};
  dbg.textContent = `name: ${childName || '-'}  status: ${i.status}  text: ${i.text || ''}  conf: ${i.minConf ?? ''}\nvariants: ${i.variants || ''}  seen: ${JSON.stringify(i.seen || {})}\nlines: ${i.lineStrength}  contrast: ${i.contrast}  paper: ${(window.__paperHi || 0).toFixed(2)}  ink: ${(i.ink || []).map(v => v.toFixed(2)).join(' ')}\n`;
  if (typeof window.__debugStrip === 'string') { const im = new Image(); im.src = window.__debugStrip; im.style.cssText = 'width:100%;margin-top:6px;background:#fff'; dbg.appendChild(im); }
  if (i.image) { i.image.style.cssText = 'width:100%;margin-top:6px;background:#fff'; dbg.appendChild(i.image); }
}
if (DEBUG) window.__debugStrip = true;
async function readName() {
  const my = ++readToken; childName = null; const seen = {};
  const t0 = performance.now();
  while (performance.now() - t0 < 20000) {
    if (my !== readToken || childName) return;
    if (state === 'alive' && tracked) {
      const r = await readNameOnce();
      if (my !== readToken) return;
      if (r && r.agree) {
        const key = r.text.toLowerCase();
        const prev = (seen[key] = seen[key] || []);
        const fresh = prev.every(p => p.length !== r.sig.length || r.sig.reduce((d, v, i) => d + Math.abs(v - p[i]), 0) / r.sig.length > 0.02);
        if (fresh && r.minConf >= NAME_MAYBE_CONF) prev.push(r.sig);
        if (prev.length >= 2) {   // two different camera frames agree
          childName = r.text[0].toUpperCase() + r.text.slice(1).toLowerCase();
          nameInfo.status = 'read'; showBubble(); showDebug(); return;
        }
      }
      nameInfo.seen = Object.fromEntries(Object.entries(seen).map(([k, v]) => [k, v.length])); showDebug();
      if (DEBUG) window.__debugStrip = true;
    }
    await new Promise(res => setTimeout(res, 900));
  }
}

let bubble = null, bubbleCanvas = null, bubbleIdx = -1, bubbleT = 0;
function bubbleLines() { return [`Hi ${childName}!`, `Good job, ${childName}!`, `I love my colors!`]; }
function drawBubble(text) {
  const c = bubbleCanvas, g = c.getContext('2d');
  g.clearRect(0, 0, c.width, c.height);
  g.font = '800 92px Gluten, "Chalkboard SE", "Comic Sans MS", cursive';
  const tw = Math.min(c.width - 120, g.measureText(text).width), bw = tw + 110, bh = 190, x = (c.width - bw) / 2, y = 20;
  g.fillStyle = '#fffcf6'; g.strokeStyle = '#2a1c15'; g.lineWidth = 12; g.lineJoin = 'round';
  g.beginPath(); g.roundRect(x, y, bw, bh, 70);
  g.moveTo(x + bw * 0.28, y + bh - 2); g.lineTo(x + bw * 0.18, y + bh + 70); g.lineTo(x + bw * 0.42, y + bh - 2);
  g.fill(); g.stroke();
  g.fillStyle = '#fffcf6'; g.fillRect(x + bw * 0.28 + 8, y + bh - 14, bw * 0.14 - 14, 20);
  g.fillStyle = '#2a1c15'; g.textAlign = 'center'; g.textBaseline = 'middle';
  g.fillText(text, c.width / 2, y + bh / 2 + 6, c.width - 120);
  bubble.material.map.needsUpdate = true;
}
async function showBubble() {
  if (!bubble) {
    bubbleCanvas = document.createElement('canvas'); bubbleCanvas.width = 1024; bubbleCanvas.height = 300;
    const t = new THREE.CanvasTexture(bubbleCanvas);
    bubble = new THREE.Mesh(new THREE.PlaneGeometry(0.5, 0.5 * 300 / 1024), new THREE.MeshBasicMaterial({ map: t, transparent: true, depthTest: false, depthWrite: false }));
    bubble.renderOrder = 12;
    const top = toLocal(...data.top).y - B.y;
    bubble.position.set(-0.04, top + 0.09, 0.01);
    root.add(bubble);
  }
  try { await document.fonts.load('800 92px Gluten'); } catch (e) {}
  bubbleIdx = -1; bubbleT = 0; bubble.visible = true;
  TOON.joy = true; // celebrate the name with a big spin jump
}
function hideBubble() { readToken++; childName = null; if (bubble) bubble.visible = false; }
function animateBubble(dt) {
  if (!bubble || !bubble.visible || !childName) return;
  bubbleT += dt;
  const lines = bubbleLines(), idx = Math.floor(bubbleT / 2.8) % lines.length;
  if (idx !== bubbleIdx) { bubbleIdx = idx; drawBubble(lines[idx]); }
  const local = (bubbleT % 2.8) / 0.35, s = local < 1 ? 0.6 + 0.4 * (1 - Math.pow(1 - local, 3)) * 1.08 : 1;
  bubble.scale.setScalar(Math.min(s, 1.06));
}

/* ---------- state machine ---------- */
let state = 'idle', stateT = 0, hasTexture = false, popT = 0, standAngle = 0.9;
function setState(s) {
  state = s; stateT = performance.now();
  $('hint').hidden = s !== 'scanning';
  $('frame').hidden = s !== 'scanning';
  const mg = $('magic');
  mg.hidden = s !== 'capturing';
  mg.classList.remove('run'); if (s === 'capturing') { void mg.offsetWidth; mg.classList.add('run'); }
  $('rec').disabled = !(s === 'alive');
  if (s === 'alive') { popT = 0; resetToon(); }
}

const easeOutBack = t => { const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); };
const camLocal = new THREE.Vector3(), inv = new THREE.Matrix4();
/* smooth the tracked pose: steady when the phone is still, quick to follow when it moves */
const anchorS = new THREE.Matrix4(), sP = new THREE.Vector3(), sQ = new THREE.Quaternion(), sS = new THREE.Vector3();
const rP = new THREE.Vector3(), rQ = new THREE.Quaternion(), rS = new THREE.Vector3();
let sInit = false;
function smoothAnchor(dt) {
  anchorM.decompose(rP, rQ, rS);
  if (!sInit || !tracked && performance.now() - lastSeen > 700) { sP.copy(rP); sQ.copy(rQ); sS.copy(rS); sInit = true; }
  const move = rP.distanceTo(sP) / Math.max(1e-6, rS.x);           // in page widths
  const a = 1 - Math.exp(-dt * (move > 0.04 ? 30 : 9 + move * 500));
  sP.lerp(rP, a); sQ.slerp(rQ, a); sS.lerp(rS, a);
  anchorS.compose(sP, sQ, sS);
}


/* ---------- cartoon performance: springs, squash & stretch, anticipation, follow-through ---------- */
const TOON = {};
function resetToon() {
  Object.assign(TOON, {
    h: 0, vh: 0, air: false, s: -0.45, vs: 0, k: 0, vk: 0, r: 0, vr: 0, spin: 0, spinV: 0,
    stand: 0, vstand: 0, act: null, actT: 0, rest: 0.9, joy: false, land: 0, sT: 0, kT: 0, rT: 0, lastAct: '',
  });
}
resetToon();
const spring = (x, v, target, w, z, dt) => v + (w * w * (target - x) - 2 * z * w * v) * dt;
const GRAV = 2.4;
function launch(height, spinTurns) {
  TOON.vh = Math.sqrt(2 * GRAV * height); TOON.air = true; TOON.vs += 3.2;
  if (spinTurns) TOON.spinV = (spinTurns * 2 * Math.PI) / (2 * TOON.vh / GRAV);
}
/* acts: each returns targets for squash (sT), lean (kT) and tilt (rT) at time tau, and can launch hops */
const ACTS = {
  hop:    { dur: 0.75, f(t, a) { if (t < 0.16) TOON.sT = -0.24; else if (!a.done) { a.done = 1; TOON.sT = 0; launch(0.045); } } },
  hop2:   { dur: 1.35, f(t, a) { if (t < 0.14 || (t > 0.62 && t < 0.74 && !TOON.air)) TOON.sT = -0.22;
                                  else { TOON.sT = 0; if (t < 0.6 && !a.d1) { a.d1 = 1; launch(0.035); } if (t >= 0.74 && !a.d2) { a.d2 = 1; launch(0.055); } } } },
  bigspin:{ dur: 1.3, f(t, a) { if (t < 0.24) { TOON.sT = -0.34; TOON.kT = 0.08 * Math.sin(t * 90); } else if (!a.done) { a.done = 1; TOON.sT = 0; TOON.kT = 0; launch(0.1, 1); } } },
  wiggle: { dur: 1.6, f(t) { const w = Math.sin(t * Math.PI / 1.6); TOON.kT = 0.3 * Math.sin(t * 2 * Math.PI * 2.4) * w;
                             TOON.rT = 0.07 * Math.sin(t * 2 * Math.PI * 1.2) * w; TOON.sT = 0.06 * Math.abs(Math.sin(t * 2 * Math.PI * 2.4)) * w; } },
  tilt:   { dur: 1.4, f(t, a) { a.dir = a.dir || (Math.random() < 0.5 ? -1 : 1); TOON.rT = t < 0.9 ? 0.2 * a.dir : 0; TOON.sT = t < 0.9 ? 0.04 : 0; } },
  yawn:   { dur: 1.6, f(t) { TOON.sT = t < 0.7 ? 0.28 * Math.min(1, t / 0.45) : (t < 0.95 ? -0.14 : 0); TOON.kT = t < 0.7 ? -0.06 : 0; } },
  joy:    { dur: 1.9, f(t, a) { if (t < 0.4) { TOON.sT = -0.18; TOON.kT = 0.07 * Math.sin(t * 110); TOON.rT = 0.03 * Math.sin(t * 77); }
                                  else if (!a.done) { a.done = 1; TOON.sT = 0; TOON.kT = 0; TOON.rT = 0; launch(0.13, 1); } } },
  // hanging things (bell, stocking): pivot at the top
  swing:  { dur: 2.2, f(t, a) { if (!a.done) { a.done = 1; TOON.vr += (Math.random() < 0.5 ? -1 : 1) * 2.6; } } },
  boing:  { dur: 1.2, f(t, a) { if (t < 0.12) TOON.sT = -0.15; else if (!a.done) { a.done = 1; TOON.sT = 0; TOON.vs += 5.5; } } },
  jingle: { dur: 1.1, f(t) { TOON.rT = 0.12 * Math.sin(t * 2 * Math.PI * 5) * Math.sin(t * Math.PI / 1.1); } },
};
const HOPPER = ['hop', 'wiggle', 'hop2', 'tilt', 'hop', 'bigspin', 'yawn', 'wiggle'];
const HANGER = ['swing', 'jingle', 'boing', 'swing'];
function stepToon(dt, t) {
  const hanging = data.motion === 'swing';
  // pick the next act after a short "moving hold"
  if (!TOON.act) {
    TOON.rest -= dt;
    TOON.sT = 0.018 * Math.sin(t * 2 * Math.PI * 0.9); TOON.kT = 0.03 * Math.sin(t * 2 * Math.PI * 0.45); TOON.rT = 0;
    if (TOON.joy && !hanging) { TOON.joy = false; TOON.act = { name: 'joy', t: 0 }; }
    else if (TOON.rest <= 0) {
      const list = hanging ? HANGER : HOPPER; let name;
      do { name = list[Math.floor(Math.random() * list.length)]; } while (name === TOON.lastAct && list.length > 1);
      TOON.act = { name, t: 0 }; TOON.lastAct = name;
    }
  }
  if (TOON.act) {
    const A = ACTS[TOON.act.name]; TOON.act.t += dt; A.f(TOON.act.t, TOON.act);
    if (TOON.act.t >= A.dur && !TOON.air) { TOON.act = null; TOON.rest = 0.35 + Math.random() * 0.8; TOON.sT = 0; TOON.kT = 0; TOON.rT = 0; }
  }
  // physics in small fixed steps so it's smooth at any frame rate
  const n = Math.max(1, Math.ceil(dt / (1 / 120))), h = dt / n;
  for (let i = 0; i < n; i++) {
    if (TOON.air) {
      TOON.vh -= GRAV * h; TOON.h += TOON.vh * h;
      const st = 0.26 * Math.min(1, Math.abs(TOON.vh) / 0.8);       // stretch along the motion
      TOON.vs = spring(TOON.s, TOON.vs, st, 22, 0.5, h);
      TOON.spin += TOON.spinV * h;
      if (TOON.h <= 0 && TOON.vh < 0) {                                 // landing: splat, then wobble
        const impact = Math.abs(TOON.vh); TOON.h = 0; TOON.vh = 0; TOON.air = false;
        TOON.vs -= 7.5 * impact; TOON.spin = 0; TOON.spinV = 0; TOON.land = impact;
        for (const piv of rigParts) piv.userData.va += (piv.userData.motion.sign || 1) * 9 * impact;
      }
    } else {
      TOON.vs = spring(TOON.s, TOON.vs, TOON.sT, 17, hanging ? 0.16 : 0.22, h);
    }
    TOON.s += TOON.vs * h;
    TOON.vk = spring(TOON.k, TOON.vk, TOON.kT, 11, 0.28, h); TOON.k += TOON.vk * h;
    TOON.vr = spring(TOON.r, TOON.vr, TOON.rT + (hanging ? 0.05 * Math.sin(t * 2.1) : 0), hanging ? 4.2 : 9, hanging ? 0.06 : 0.32, h); TOON.r += TOON.vr * h;
    TOON.vstand = spring(TOON.stand, TOON.vstand, 1, 9.5, 0.3, h); TOON.stand += TOON.vstand * h;
  }
  // compose: pivot at the feet (or the hook for hanging things)
  const P0 = hanging ? new THREE.Vector3(BP.x - B.x, BP.y - B.y, 0) : new THREE.Vector3(0, 0, 0);
  const sy = Math.max(0.45, 1 + TOON.s), sx = 1 / Math.sqrt(sy);
  const M = new THREE.Matrix4().makeTranslation(P0.x, P0.y + TOON.h, 0)
    .multiply(new THREE.Matrix4().makeRotationZ(TOON.r))
    .multiply(new THREE.Matrix4().set(1, TOON.k, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1))
    .multiply(new THREE.Matrix4().makeScale(sx * Math.cos(TOON.spin), sy, 1))
    .multiply(new THREE.Matrix4().makeTranslation(-P0.x, -P0.y, 0));
  toon.matrix.copy(M); toon.matrixWorldNeedsUpdate = true;
}

function animate(now) {
  requestAnimationFrame(animate);
  if (!controller) return;
  const t = now / 1000;
  const visible = tracked || (now - lastSeen < 700);
  const dt = Math.min(0.1, (now - (animate.last || now)) / 1000); animate.last = now;
  if (state === 'alive') animateBubble(dt);

  if (state === 'scanning' && tracked) setState(hasTexture ? 'alive' : 'capturing');
  if (state === 'capturing') {
    if (!tracked) { setState('scanning'); }
    else { extract(); if (now - stateT > 1300) { hasTexture = true; finalizeCutout(); setState('alive'); if (NAME_READING) readName(); } }
  }
  if (state === 'alive' && !visible) setState('scanning');

  smoothAnchor(dt);
  anchor.matrix.copy(anchorS);
  anchor.visible = visible && state === 'alive';

  if (state === 'alive') {
    popT = Math.min(1, popT + dt / 0.9);
    stepToon(dt, t);
    // stand up facing the phone, on a spring so it overshoots and settles like a cartoon
    inv.copy(anchorS).invert(); camLocal.set(0, 0, 0).applyMatrix4(inv);
    const target = THREE.MathUtils.clamp(Math.atan2(-(camLocal.y - B.y), camLocal.z), 0.3, 1.35);
    standAngle += (target - standAngle) * Math.min(1, dt * 4);
    root.rotation.x = standAngle * TOON.stand;
    root.position.z = 0.002 + 0.05 * Math.min(1, TOON.stand);
    root.scale.setScalar(1.07);
    root.rotation.y = 0.28 * Math.sin(t * 0.9) * Math.min(1, TOON.stand);   // a slow turn shows off the thickness
    root.visible = true; shadow.visible = true;
    patchMat.uniforms.uOpacity.value = Math.min(0.96, popT * 2);
    const d = Math.min(1, Math.max(0, popT - 0.4) / 0.6), beat = t * 2 * Math.PI * 1.15;
    const busy = TOON.act ? 0.45 : 1;   // parts calm down while the body performs, then flop on landings
    for (const piv of rigParts) {
      const m = piv.userData.motion, sg = m.sign || 1, ph = m.phase || 0, sp = m.speed || 1, u = piv.userData;
      piv.position.copy(u.base); piv.scale.set(1, 1, 1);
      let tgt = 0;
      if (m.type === 'rot') tgt = m.amp * Math.sin(beat * sp + ph) * d * busy;
      else if (m.type === 'flap') tgt = sg * (m.base + m.amp * (0.5 + 0.5 * Math.sin(beat * 2 + ph))) * d * busy;
      else if (m.type === 'tap') tgt = sg * m.amp * Math.max(0, Math.sin(beat + ph)) * d * busy;
      else if (m.type === 'pop') { const k = Math.pow(Math.max(0, Math.sin(beat)), 2) * d + 0.8 * Math.min(1, TOON.s < -0.1 ? -TOON.s * 3 : 0); piv.position.y += m.amp * k; tgt = -0.22 * k; }
      else if (m.type === 'twinkle') { piv.scale.setScalar(1 + 0.22 * Math.sin(t * 5) * d); u.a = t * 1.6 * d; piv.rotation.z = u.a; continue; }
      tgt += -0.6 * TOON.vk * 0.08 * sg;   // drag behind the body's lean
      u.va = spring(u.a, u.va, tgt, 13, 0.16, dt); u.a += u.va * dt;
      u.a = THREE.MathUtils.clamp(u.a, -1.2, 1.2);
      piv.rotation.z = u.a;
    }
    const blink = (t % 3.2) < 0.13 || (TOON.land > 0.3 && TOON.s < -0.12);
    lids.forEach(l => { l.visible = blink && d > 0.5; });
    const lift = TOON.h * 6;
    shadow.scale.set((1 - Math.min(0.55, lift)) * (1 + 0.25 * Math.max(0, -TOON.s)), 1, 1);
    shadow.material.opacity = (0.18 + 0.2 * Math.min(1, popT * 2)) * (1 - Math.min(0.6, lift));
    if (smoke) {
      const p = smoke.geometry.attributes.position, n = p.count;
      smoke.material.opacity = 0.85 * d;
      for (let i = 0; i < n; i++) { const k = ((t * 0.35 + i / n) % 1); p.setXYZ(i, 0.03 * Math.sin(k * 6 + i), k * 0.35, 0); }
      p.needsUpdate = true; smoke.material.size = 0.05 + 0.04 * Math.sin(t);
    }
    // snow
    const snowPos = snow.geometry.attributes.position, seed = snow.userData.seed;
    snow.material.opacity = d * 0.95;
    for (let i = 0; i < seed.length; i++) {
      const [x, y0, z, v] = seed[i];
      const y = 1.05 - ((y0 + t * v) % 1.05);
      snowPos.setXYZ(i, x + 0.02 * Math.sin(t * 1.5 + i), y, z);
    }
    snowPos.needsUpdate = true;
  } else {
    root.visible = false; shadow && (shadow.visible = false);
  }

  renderer.setRenderTarget(null);
  renderer.clear();
  renderer.render(bgScene, orthoCam);
  renderer.render(arScene, arCam);
  renderer.render(overlayScene, orthoCam);
}

/* ---------- start: camera or photo ---------- */
async function startWith(stream) {
  $('start').hidden = true;
  video.srcObject = stream;
  await new Promise(r => { if (video.readyState >= 1) r(); else video.onloadedmetadata = r; });
  await video.play().catch(() => {});
  video.setAttribute('width', video.videoWidth); video.setAttribute('height', video.videoHeight);
  videoTex = new THREE.VideoTexture(video);
  videoTex.minFilter = THREE.LinearFilter; videoTex.magFilter = THREE.LinearFilter; videoTex.generateMipmaps = false;
  bgMat.uniforms.uVideo.value = videoTex;

  if (!data) data = await (await fetch(SHEET.parts)).json();
  if (data.clean && !inkTex) {   // a drawn character: fixed outline and lines, the camera only brings the colors
    CLEAN = true;
    inkTex = await new THREE.TextureLoader().loadAsync(`targets/${data.clean.ink}?v=1`);
    inkTex.minFilter = THREE.LinearFilter; inkTex.generateMipmaps = false;
  }
  if (controller) controller.stopProcessVideo();
  globalThis.__MINDAR_FOVY = FOV_OVERRIDE || (video.videoHeight >= video.videoWidth ? 64 : 50);
  controller = new window.MINDAR.IMAGE.Controller({
    inputWidth: video.videoWidth, inputHeight: video.videoHeight, maxTrack: 1,
    missTolerance: 6, warmupTolerance: 3,
    onUpdate: d => {
      if (d.type !== 'updateMatrix') return;
      updates++;
      if (d.worldMatrix) { anchorM.fromArray(d.worldMatrix).multiply(postMatrix); tracked = true; lastSeen = performance.now(); }
      else tracked = false;
    },
  });
  P.fromArray(controller.getProjectionMatrix());
  if (!targetURL) {
    const b64 = (await import(SHEET.mind)).default;
    const bin = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
    targetURL = URL.createObjectURL(new Blob([bin], { type: 'application/octet-stream' }));
  }
  const { dimensions } = await controller.addImageTargets(targetURL);
  [mw, mh] = dimensions[0];
  postMatrix.compose(new THREE.Vector3(mw / 2, mw / 2 + (mh - mw) / 2, 0), new THREE.Quaternion(), new THREE.Vector3(mw, mw, mw));
  if (!rt) { buildExtraction(); buildCharacter(); buildWatermark(); buildNameReader(); }
  if (data.nameBoxes && NAME_READING) loadOCR();
  else { extractMat.uniforms.uVideo.value = videoTex; patchMat.uniforms.uVideo.value = videoTex; }
  resize();
  await controller.dummyRun(video);
  controller.processVideo(video);
  $('controls').hidden = false;
  hasTexture = false;
  setState('scanning');
}

$('start-btn').addEventListener('click', async () => {
    try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: false, video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 960 } } });
    await startWith(stream);
  } catch (e) {
    const err = $('start-err');
    err.hidden = false;
    err.textContent = 'The camera didn\'t start. Allow camera access in your browser settings, or use a photo of the page instead.';
    $('start').hidden = false;
  }
});

let photoCanvas = null, photoTimer = null;
async function usePhoto(file) {
  const bmp = await createImageBitmap(file);
  const k = Math.min(1, 1280 / Math.max(bmp.width, bmp.height));
  photoCanvas = photoCanvas || document.createElement('canvas');
  photoCanvas.width = Math.round(bmp.width * k); photoCanvas.height = Math.round(bmp.height * k);
  const g = photoCanvas.getContext('2d');
  const draw = () => g.drawImage(bmp, 0, 0, photoCanvas.width, photoCanvas.height);
  draw(); clearInterval(photoTimer); photoTimer = setInterval(draw, 100);
  if (video.srcObject && video.srcObject.getTracks) video.srcObject.getTracks().forEach(tr => tr.stop());
  await startWith(photoCanvas.captureStream(10));
}
$('photo-btn').addEventListener('click', () => $('file').click());
$('photo-btn2').addEventListener('click', () => $('file').click());
$('file').addEventListener('change', e => { const f = e.target.files[0]; if (f) usePhoto(f); e.target.value = ''; });
$('again').addEventListener('click', () => { hasTexture = false; hideBubble(); setState('scanning'); });

/* ---------- recording ---------- */
let rec = null, chunks = [], recStart = 0, recTimer = null, clipBlob = null, clipType = 'video/webm';
const MAX_MS = 15000;
function pickType() {
  const types = ['video/mp4;codecs=avc1', 'video/mp4', 'video/webm;codecs=vp9', 'video/webm;codecs=vp8', 'video/webm'];
  return types.find(t => window.MediaRecorder && MediaRecorder.isTypeSupported(t)) || '';
}
function stopRec() { if (rec && rec.state !== 'inactive') rec.stop(); }
$('rec').addEventListener('click', () => {
  if (rec && rec.state === 'recording') { stopRec(); return; }
  const stream = canvas.captureStream(30);
  const type = pickType();
  try { rec = new MediaRecorder(stream, type ? { mimeType: type, videoBitsPerSecond: 6e6 } : undefined); }
  catch (e) { $('hint').hidden = false; $('hint').textContent = 'Recording isn\'t supported in this browser.'; return; }
  clipType = rec.mimeType || type || 'video/webm';
  chunks = [];
  rec.ondataavailable = e => e.data.size && chunks.push(e.data);
  rec.onstop = () => {
    clearInterval(recTimer);
    $('rec').classList.remove('on'); $('timer').hidden = true; $('rec-ring').style.strokeDashoffset = 289;
    clipBlob = new Blob(chunks, { type: clipType.split(';')[0] });
    const clip = $('clip'); clip.src = URL.createObjectURL(clipBlob); clip.play().catch(() => {});
    $('save-note').hidden = true;
    $('result').hidden = false;
  };
  rec.start(250); recStart = performance.now();
  $('rec').classList.add('on'); $('timer').hidden = false;
  recTimer = setInterval(() => {
    const ms = performance.now() - recStart;
    const s = Math.floor(ms / 1000);
    $('timer').textContent = `0:${String(s).padStart(2, '0')}`;
    $('rec-ring').style.strokeDashoffset = 289 * (1 - Math.min(1, ms / MAX_MS));
    if (ms >= MAX_MS) stopRec();
  }, 100);
});
$('retake').addEventListener('click', () => { $('result').hidden = true; });
const isIOS = /iPhone|iPad|iPod/.test(navigator.userAgent) || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
function clipFile() {
  const ext = clipBlob.type.includes('mp4') ? 'mp4' : 'webm';
  return new File([clipBlob], `my-${sheetKey}-came-alive.${ext}`, { type: clipBlob.type });
}
function note(t) { const n = $('save-note'); n.hidden = false; n.textContent = t; }
function download(file) {
  const a = document.createElement('a'); a.href = URL.createObjectURL(clipBlob); a.download = file.name;
  document.body.appendChild(a); a.click(); a.remove();
}
async function shareFile(file) {
  if (navigator.canShare && navigator.canShare({ files: [file] })) {
    try { await navigator.share({ files: [file], title: `My ${SHEET.name.toLowerCase()} came alive!` }); return 'shared'; }
    catch (e) { return e.name === 'AbortError' ? 'cancelled' : 'failed'; }
  }
  return 'unsupported';
}
$('save').addEventListener('click', async () => {
  if (!clipBlob) return;
  const file = clipFile();
  if (isIOS) {
    // On iPhone the only way into the Photos app is the share sheet's "Save Video" action.
    note('Tap “Save Video” in the menu (scroll down if you don’t see it). It goes to your Photos.');
    const r = await shareFile(file);
    if (r === 'unsupported' || r === 'failed') { download(file); note('Saved to Files › Downloads. Open it there and tap Share › Save Video to add it to Photos.'); }
    return;
  }
  download(file);
  note('Saved to your phone’s Downloads. It also shows up in your Gallery or Photos app.');
});
$('share').addEventListener('click', async () => {
  if (!clipBlob) return;
  const file = clipFile();
  const r = await shareFile(file);
  if (r === 'unsupported' || r === 'failed') { download(file); note('Sharing isn’t available here, so the video was saved to your downloads instead.'); }
});

/* ---------- test hook (used by automated checks; harmless in production) ---------- */
window.__ar = {
  get state() { return state; }, get tracked() { return tracked; }, get updates() { return updates; },
  extractPNG() {
    if (!rt) return null;
    const w = rt.width, h = rt.height, px = new Uint8Array(w * h * 4);
    renderer.readRenderTargetPixels(rt, 0, 0, w, h, px);
    const c = document.createElement('canvas'); c.width = w; c.height = h;
    const g = c.getContext('2d'), img = g.createImageData(w, h);
    for (let y = 0; y < h; y++) img.data.set(px.subarray((h - 1 - y) * w * 4, (h - y) * w * 4), y * w * 4);
    g.putImageData(img, 0, 0); return c.toDataURL('image/png');
  },
  start: usePhoto,
  get name() { return childName; },
  get nameInfo() { const i = nameInfo ? { ...nameInfo } : null; if (i && i.image) { i.imagePNG = i.image.toDataURL(); delete i.image; } return i; },
};

requestAnimationFrame(animate);
