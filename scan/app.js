import * as THREE from 'three';
import './lib/mindar-image.prod.js';
/* Camera field of view (vertical, degrees). MindAR assumes 45, but phone main cameras see about 64 degrees along
   the long side of the picture and about 50 along the short side. ?fov= overrides it for testing. */
const FOV_OVERRIDE = Number(new URLSearchParams(location.search).get('fov')) || 0;

/* ---------- sheet config: each QR code opens ?s=<sheet> (and &size=letter on US Letter pages) ---------- */
const NAMES = { hedgehog: 'Hedgehog', gift: 'Gift Box', bell: 'Bell', stocking: 'Stocking', snowman: 'Snowman', gingerbread: 'Gingerbread Man',
  penguin: 'Penguin', tree: 'Christmas Tree', owl: 'Owl', santa: 'Santa', house: 'Gingerbread House', bunny: 'Bunny', fox: 'Fox', reindeer: 'Reindeer', bear: 'Polar Bear' };
const params = new URLSearchParams(location.search);
const sheetKey = NAMES[params.get('s')] ? params.get('s') : 'penguin';
const paperSize = params.get('size') === 'letter' ? 'letter' : 'a4';
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
function partMesh(polys, origin, order) {
  const m = new THREE.Mesh(partGeometry(polys, origin),
    new THREE.MeshBasicMaterial({ map: rt.texture, transparent: true, depthTest: false, depthWrite: false, side: THREE.DoubleSide }));
  m.renderOrder = order;
  return m;
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
  root.add(bodyG);
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
  const pg = new THREE.ShapeGeometry(sil.map(poly => new THREE.Shape(poly.map(([x, y]) => toLocal(x, y)))));
  patch = new THREE.Mesh(pg, patchMat);
  patch.position.z = 0.0005; patch.renderOrder = 1;
  anchor.add(patch);

  const sw = (data.region[2] - data.region[0]) * scaleT() / mw;
  shadow = new THREE.Mesh(new THREE.PlaneGeometry(sw * 0.8, sw * 0.16), dot(1, 'rgba(0,0,0,1)', 0.32));
  shadow.position.set(B.x, B.y + 0.01, 0.001); shadow.renderOrder = 2;
  anchor.add(shadow);


  bodyG.add(partMesh(data.body, BP, 6));
  for (const p of data.parts) {
    const o = toLocal(...p.pivot), parentOrigin = p.parent === 'root' ? B : BP;
    const piv = new THREE.Group(); piv.position.set(o.x - parentOrigin.x, o.y - parentOrigin.y, 0); piv.userData = { base: piv.position.clone(), motion: p.motion };
    piv.add(partMesh(p.polys, o, p.order));
    (p.parent === 'root' ? root : bodyG).add(piv); rigParts.push(piv);
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
  snow = new THREE.Points(sg, new THREE.PointsMaterial({ size: 0.034, color: 0x9fd3ff, map: new THREE.CanvasTexture(sc), transparent: true, depthTest: false, depthWrite: false, opacity: 0 }));
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
function grabName() {
  mvp.copy(P).multiply(anchorM);
  renderer.setRenderTarget(nameRT); renderer.clear(); renderer.render(nameScene, orthoCam); renderer.setRenderTarget(null);
  const w = nameRT.width, h = nameRT.height, px = new Uint8Array(w * h * 4);
  renderer.readRenderTargetPixels(nameRT, 0, 0, w, h, px);
  const g = new Float32Array(w * h);           // grey, top row first
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
    const i = ((h - 1 - y) * w + x) * 4; g[y * w + x] = (px[i] * 0.299 + px[i + 1] * 0.587 + px[i + 2] * 0.114) / 255;
  }
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
async function readName() {
  childName = null; nameInfo = { status: 'reading' };
  if (!nameRT) { nameInfo = { status: 'no-boxes' }; return; }
  const { g, w, h } = grabName();
  const found = findBoxes(g, w, h);
  if (window.__debugStrip) { const c = document.createElement('canvas'); c.width = w; c.height = h; const x = c.getContext('2d'), im = x.createImageData(w, h); for (let i = 0; i < w * h; i++) { const v = g[i] * 255; im.data[i * 4] = im.data[i * 4 + 1] = im.data[i * 4 + 2] = v; im.data[i * 4 + 3] = 255; } x.putImageData(im, 0, 0); window.__debugStrip = c.toDataURL(); }
  if (!found || found.lineStrength < 4) { nameInfo = { status: 'boxes-not-found', ...(found ? { lineStrength: found.lineStrength } : {}) }; return; }
  const ink = [], cells = [];
  for (const b of found.boxes) {                       // box interior, inset to stay clear of the printed lines
    const ic = (b.c1 - b.c0) * 0.15, ir = (b.r1 - b.r0) * 0.13;
    const cw = Math.max(4, Math.round(b.c1 - b.c0 - 2 * ic)), ch = Math.max(4, Math.round(b.r1 - b.r0 - 2 * ir));
    const cell = new Float32Array(cw * ch); let dark = 0;
    for (let y = 0; y < ch; y++) for (let x = 0; x < cw; x++) { const v = sampleRot(g, w, h, found.rot, b.c0 + ic + x, b.r0 + ir + y); cell[y * cw + x] = v; if (v < 0.5) dark++; }
    ink.push(dark / (cw * ch)); cells.push({ cell, cw, ch });
  }
  const filled = ink.map(v => v > 0.03);
  let n = 0; while (n < filled.length && filled[n]) n++;
  nameInfo = { status: 'checked', angle: found.angle, scale: found.scale, lineStrength: found.lineStrength, ink: ink.map(v => +v.toFixed(3)), letters: n };
  if (n < 2 || filled.slice(n).some(Boolean)) { nameInfo.status = 'no-name'; return; }
  if (ink.slice(0, n).some(v => v > 0.42)) { nameInfo.status = 'messy'; return; }   // scribbles fill boxes far more than letters do
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
    for (let k = 0; k < cw * ch; k++) { const v = cell[k] < 0.55 ? 0 : 255; img.data[k * 4] = img.data[k * 4 + 1] = img.data[k * 4 + 2] = v; img.data[k * 4 + 3] = 255; }
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
  if (text.length === n && looksLikeName && minConf >= NAME_MIN_CONF) {
    const variants = [];
    for (const thr of [0.45, 0.65]) {
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
  nameInfo.agree = agree;
  if (agree) {
    childName = text[0].toUpperCase() + text.slice(1).toLowerCase();
    nameInfo.status = 'read';
    showBubble();
  } else nameInfo.status = 'unsure';
}
const NAME_MIN_CONF = 92;

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
}
function hideBubble() { childName = null; if (bubble) bubble.visible = false; }
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
  if (s === 'alive') popT = 0;
}

const easeOutBack = t => { const c1 = 1.9, c3 = c1 + 1; return 1 + c3 * Math.pow(t - 1, 3) + c1 * Math.pow(t - 1, 2); };
const camLocal = new THREE.Vector3(), inv = new THREE.Matrix4();

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
    else { extract(); if (now - stateT > 1300) { hasTexture = true; setState('alive'); readName(); } }
  }
  if (state === 'alive' && !visible) setState('scanning');

  anchor.matrix.copy(anchorM);
  anchor.visible = visible && state === 'alive';

  if (state === 'alive') {
    popT = Math.min(1, popT + 1 / 55);
    // stand up facing the phone
    inv.copy(anchorM).invert(); camLocal.set(0, 0, 0).applyMatrix4(inv);
    const target = THREE.MathUtils.clamp(Math.atan2(-(camLocal.y - B.y), camLocal.z), 0.3, 1.35);
    standAngle += (target - standAngle) * 0.08;
    const pop = easeOutBack(popT);
    root.rotation.x = standAngle * pop;
    const beat0 = t * 2 * Math.PI * 1.15;
    const lift = 0.05 * pop + 0.018 * Math.abs(Math.sin(beat0)) * Math.max(0, popT - 0.6) / 0.4;
    root.position.z = 0.002 + lift;
    root.scale.setScalar(1 + 0.07 * pop);
    shadow.material.opacity = 0.18 + 0.2 * Math.min(1, popT * 2);
    root.visible = true; shadow.visible = true;
    patchMat.uniforms.uOpacity.value = Math.min(0.96, popT * 1.4);
    const d = Math.max(0, popT - 0.6) / 0.4, beat = t * 2 * Math.PI * 1.15;
    const base = bodyG.userData.base, hopS = Math.abs(Math.sin(beat));
    bodyG.position.copy(base); bodyG.rotation.z = 0; bodyG.scale.set(1, 1, 1);
    if (data.motion === 'dance') {
      bodyG.rotation.z = 0.13 * Math.sin(beat) * d;
      bodyG.position.y = base.y + 0.025 * hopS * d;
    } else if (data.motion === 'bounce') {
      const squash = Math.pow(1 - hopS, 4) * d;
      bodyG.position.y = base.y + 0.05 * hopS * d;
      bodyG.scale.set(1 + 0.08 * squash, 1 - 0.08 * squash, 1);
      bodyG.rotation.z = 0.05 * Math.sin(beat * 0.5) * d;
    } else if (data.motion === 'swing') {
      bodyG.rotation.z = 0.28 * Math.sin(beat * 0.8) * d;
    }
    for (const piv of rigParts) {
      const m = piv.userData.motion, sg = m.sign || 1, ph = m.phase || 0, sp = m.speed || 1;
      piv.position.copy(piv.userData.base); piv.rotation.z = 0; piv.scale.set(1, 1, 1);
      if (m.type === 'rot') piv.rotation.z = m.amp * Math.sin(beat * sp + ph) * d;
      else if (m.type === 'flap') piv.rotation.z = sg * (m.base + m.amp * (0.5 + 0.5 * Math.sin(beat * 2 + ph))) * d;
      else if (m.type === 'tap') piv.rotation.z = sg * m.amp * Math.max(0, Math.sin(beat + ph)) * d;
      else if (m.type === 'pop') { const k = Math.pow(Math.max(0, Math.sin(beat)), 2) * d; piv.position.y += m.amp * k; piv.rotation.z = -0.22 * k; }
      else if (m.type === 'twinkle') { piv.rotation.z = t * 1.6 * d; piv.scale.setScalar(1 + 0.18 * Math.sin(t * 5) * d); }
    }
    const blink = (t % 3.2) < 0.14;
    lids.forEach(l => { l.visible = blink && d > 0.5; });
    shadow.scale.set(1 - 0.25 * hopS * d * (data.motion === 'swing' ? 0 : 1), 1, 1);
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
  if (data.nameBoxes) loadOCR();
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
