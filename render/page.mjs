// Builds render/build/page.html from out/factory.svg + out/anchors.json + fx.js
import fs from 'node:fs';
import path from 'node:path';
const [svgPath, outPath, scale = '3'] = process.argv.slice(2);
// scene anchors written by gen.py next to factory.svg; fx.js reads every position from here
const anchors = fs.readFileSync(path.join(path.dirname(svgPath), 'anchors.json'), 'utf8');
const FY = JSON.parse(anchors).floorY;
const S = +scale, W = 480 * S, H = 320 * S;
let svg = fs.readFileSync(svgPath, 'utf8')
  .replace(/@media \(prefers-reduced-motion:reduce\)\{[^}]*\{[^}]*\}\}/, '');
// unique ids per copy so the 3 inline copies don't clash
const copy = (tag) => svg.replace(/id='([^']+)'/g, `id='${tag}$1'`).replace(/url\(#([^)]+)\)/g, `url(#${tag}$1)`)
  .replace('<svg ', `<svg class='scene' width='${W}' height='${H}' `);
const html = `<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;background:#0c0d0e;overflow:hidden}
#st{position:relative;width:${W}px;height:${H}px;overflow:hidden;background:#25272a}
#st>*{position:absolute;left:0;top:0;width:${W}px;height:${H}px}
.scene{display:block}
/* bloom: threshold the bright pixels, blur, screen on top */
#bloom{filter:url(#thr) blur(${3 * S}px);mix-blend-mode:screen;opacity:.55}
#bloom2{filter:url(#thr) blur(${10 * S}px);mix-blend-mode:screen;opacity:.45}
/* floor reflection: mirrored copy about the floor line, faded */
#refl{transform-origin:0 ${FY * S}px;transform:scaleY(-1);filter:blur(${0.8 * S}px) brightness(.9);
  opacity:.16;mix-blend-mode:screen;
  -webkit-mask:linear-gradient(to bottom,transparent ${FY * S}px,#000 ${FY * S + 1}px,transparent ${320 * S}px)}
#shade{mix-blend-mode:multiply}
#light{mix-blend-mode:screen}
#crt{mix-blend-mode:normal}
#base .fg{filter:blur(.3px)}
#refl .fg,#refl .rl,#bloom .fg,#bloom2 .fg,#bloom .rl,#bloom2 .rl{display:none}
#glow{background:radial-gradient(ellipse 75% 70% at 50% 50%,rgba(200,210,205,.035),transparent 70%);mix-blend-mode:screen}
</style></head><body>
<svg width="0" height="0" style="position:absolute"><filter id="thr" color-interpolation-filters="sRGB">
<feColorMatrix type="matrix" values="1 0 0 0 0 0 1 0 0 0 0 0 1 0 0 0 0 0 1 0"/>
<feComponentTransfer><feFuncR type="linear" slope="4" intercept="-2.9"/><feFuncG type="linear" slope="4" intercept="-2.9"/><feFuncB type="linear" slope="4" intercept="-2.9"/></feComponentTransfer>
</filter></svg>
<div id="st">
<div id="base">${copy('a')}</div>
<div id="refl">${copy('r')}</div>
<canvas id="shade"></canvas>
<canvas id="light"></canvas>
<div id="bloom">${copy('b')}</div>
<div id="bloom2">${copy('c')}</div>
<div id="glow"></div>
<canvas id="crt"></canvas>
</div>
<script>window.AW_SCALE=${S};window.AW_ANCHORS=${anchors};</script>
<script>${fs.readFileSync(new URL('./fx.js', import.meta.url), 'utf8')}</script>
<script>
window.AW_seek = (t) => {
  for (const a of document.getAnimations()) { a.pause(); a.currentTime = t * 1000; }
  window.AW_drawFx(t);
};
window.AW_seek(0);
</script></body></html>`;
fs.writeFileSync(outPath, html);
