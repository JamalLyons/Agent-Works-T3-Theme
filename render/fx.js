// Effect layers for the Agent Works render. Runs in the page.
// Everything is a pure function of t (seconds) and periodic in LOOP, so the WebP loops seamlessly.
// Drawing is done in scene units (480x320) and scaled by S.
(() => {
  const LOOP = 20, TAU = Math.PI * 2;
  const W = 480, H = 320, FY = 282;
  const AMBER = '255,181,71';
  const S = window.AW_SCALE;
  const ph = (t, n = 1) => (TAU * n * t) / LOOP; // whole cycles per loop

  // deterministic PRNG
  let seed = 7;
  const rnd = () => ((seed = (seed * 16807) % 2147483647) / 2147483647);

  const mk = (id) => {
    const c = document.getElementById(id);
    c.width = W * S; c.height = H * S;
    const x = c.getContext('2d');
    x.setTransform(S, 0, 0, S, 0, 0);
    return x;
  };
  const shade = mk('shade');   // multiply: AO, vignette, calm center
  const light = mk('light');   // screen: shafts, motes, steam, embers
  const crt = mk('crt');       // static phosphor / scanline structure

  // window geometry (matches gen.py): glass x wx+2..wx+42, y 99..125; shaft hits floor shifted +20
  const WINS = [142, 296];
  const GLASS_Y0 = 99, GLASS_Y1 = 125;
  const shaftPoly = (wx, t) => {
    const sway = Math.sin(ph(t)) * 1.5;
    return [[wx + 2, GLASS_Y1], [wx + 42, GLASS_Y1], [wx + 64 + sway, FY + 6], [wx + 20 + sway, FY + 6]];
  };
  const inShaft = (wx, x, y) => {
    if (y < GLASS_Y1 || y > FY) return false;
    const k = (y - GLASS_Y1) / (FY + 6 - GLASS_Y1);
    const l = wx + 2 + 18 * k, r = wx + 42 + 22 * k;
    return x > l && x < r;
  };

  // dust motes: each orbits on integer-frequency paths so the loop closes
  const motes = [];
  for (const wx of WINS) {
    for (let i = 0; i < 70; i++) {
      motes.push({
        wx, bx: wx + 6 + rnd() * 50, by: GLASS_Y1 + 4 + rnd() * 150,
        ax: 2 + rnd() * 6, ay: 3 + rnd() * 9, fx: 1 + ((rnd() * 2) | 0), fy: 1 + ((rnd() * 2) | 0),
        p: rnd() * TAU, q: rnd() * TAU, tw: 1 + ((rnd() * 4) | 0), s: rnd() < 0.15 ? 0.9 : 0.5,
        a: 0.25 + rnd() * 0.5,
      });
    }
  }
  // backlit steam wisps drifting through the right shaft
  const wisps = [];
  for (let i = 0; i < 9; i++) wisps.push({ p: i / 9, x: 300 + rnd() * 30, r: 7 + rnd() * 8, a: 0.05 + rnd() * 0.05 });

  // static layers -----------------------------------------------------------
  function drawCRT() {
    // per-scene-pixel row structure + a faint phosphor bloom on each row
    crt.setTransform(1, 0, 0, 1, 0, 0);
    for (let y = 0; y < H * S; y++) {
      const r = y % S;
      const a = r === S - 1 ? 0.18 : r === 0 ? 0.0 : 0.04;
      if (a) { crt.fillStyle = `rgba(0,0,0,${a})`; crt.fillRect(0, y, W * S, 1); }
    }
    // fixed (non-animated) grain, so it costs nothing per frame
    const img = crt.getImageData(0, 0, W * S, H * S), d = img.data;
    for (let i = 0; i < d.length; i += 4) {
      const n = rnd();
      if (n < 0.02) { d[i] = d[i + 1] = d[i + 2] = 255; d[i + 3] = 10; }
      else if (n > 0.97) { d[i + 3] = Math.max(d[i + 3], 22); }
    }
    crt.putImageData(img, 0, 0);
  }

  function drawShade() {
    const c = shade;
    c.fillStyle = '#fff'; c.fillRect(0, 0, W, H);
    // ceiling falls off into darkness
    let gr = c.createLinearGradient(0, 0, 0, 120);
    gr.addColorStop(0, 'rgb(70,70,72)'); gr.addColorStop(1, 'rgb(255,255,255)');
    c.fillStyle = gr; c.fillRect(0, 0, W, 120);
    // calm center: lower contrast + darker behind the chat column
    gr = c.createLinearGradient(110, 0, 370, 0);
    gr.addColorStop(0, 'rgb(255,255,255)'); gr.addColorStop(0.18, 'rgb(196,196,198)');
    gr.addColorStop(0.82, 'rgb(196,196,198)'); gr.addColorStop(1, 'rgb(255,255,255)');
    c.fillStyle = gr; c.fillRect(110, 0, 260, H);
    // wall/floor contact
    gr = c.createLinearGradient(0, FY - 14, 0, FY + 3);
    gr.addColorStop(0, 'rgb(255,255,255)'); gr.addColorStop(1, 'rgb(120,120,122)');
    c.fillStyle = gr; c.fillRect(0, FY - 14, W, 17);
    // under-belt ambient occlusion
    const blob = (x, y, rx, ry, k) => {
      c.save(); c.translate(x, y); c.scale(rx, ry);
      const g2 = c.createRadialGradient(0, 0, 0, 0, 0, 1);
      g2.addColorStop(0, `rgb(${k},${k},${k + 2})`); g2.addColorStop(1, 'rgb(255,255,255)');
      c.fillStyle = g2; c.beginPath(); c.arc(0, 0, 1, 0, TAU); c.fill(); c.restore();
    };
    blob(240, 291, 230, 9, 110);
    blob(404, 292, 30, 6, 90);   // bin
    blob(458, 314, 30, 8, 110);  // crate stack
    for (const x of [57, 106, 184, 262, 318, 398]) blob(x, 290, 7, 2.2, 70); // belt legs
    for (const x of [62, 122, 393]) blob(x, 262, 9, 2, 120);  // robots on the belt line
    blob(14, 245, 18, 6, 150);   // control panel
    // vignette
    gr = c.createRadialGradient(240, 190, 120, 240, 190, 330);
    gr.addColorStop(0, 'rgb(255,255,255)'); gr.addColorStop(1, 'rgb(70,70,74)');
    c.fillStyle = gr; c.fillRect(0, 0, W, H);
  }

  // per-frame light layer ------------------------------------------------------
  function drawLight(t) {
    const c = light;
    c.clearRect(0, 0, W, H);
    // god-rays: layered translucent wedges with slow periodic breathing
    for (const wx of WINS) {
      const breathe = 0.85 + 0.15 * Math.sin(ph(t) + wx);
      for (let k = 0; k < 3; k++) {
        const p = shaftPoly(wx, t + k * 2);
        const gr = c.createLinearGradient(0, GLASS_Y1, 0, FY + 6);
        const a = [0.045, 0.03, 0.02][k] * breathe;
        gr.addColorStop(0, `rgba(225,228,232,${a * 1.6})`);
        gr.addColorStop(0.6, `rgba(210,214,220,${a})`);
        gr.addColorStop(1, `rgba(200,204,210,${a * 0.3})`);
        c.fillStyle = gr;
        c.beginPath();
        const sh = k * 2 - 2;
        c.moveTo(p[0][0] + sh, p[0][1]); c.lineTo(p[1][0] - sh, p[1][1]);
        c.lineTo(p[2][0] - sh * 2, p[2][1]); c.lineTo(p[3][0] + sh * 2, p[3][1]);
        c.closePath(); c.fill();
      }
      // pane-divider streaks (mullion shadows) inside the beam
      c.fillStyle = 'rgba(0,0,0,0)';
      // floor pool where the light lands
      c.save(); c.translate(wx + 42, FY + 8); c.scale(30, 5);
      const pool = c.createRadialGradient(0, 0, 0, 0, 0, 1);
      pool.addColorStop(0, `rgba(220,224,230,${0.10 * breathe})`); pool.addColorStop(1, 'rgba(220,224,230,0)');
      c.fillStyle = pool; c.beginPath(); c.arc(0, 0, 1, 0, TAU); c.fill(); c.restore();
      // glow around the glass itself
      c.save(); c.translate(wx + 22, (GLASS_Y0 + GLASS_Y1) / 2); c.scale(40, 26);
      const gl = c.createRadialGradient(0, 0, 0.3, 0, 0, 1);
      gl.addColorStop(0, 'rgba(200,205,212,0.10)'); gl.addColorStop(1, 'rgba(200,205,212,0)');
      c.fillStyle = gl; c.beginPath(); c.arc(0, 0, 1, 0, TAU); c.fill(); c.restore();
    }
    // backlit steam rolling across the right beam
    for (const w of wisps) {
      const u = (t / LOOP + w.p) % 1;
      const x = w.x + u * 30 + Math.sin(ph(t, 2) + w.p * 9) * 3;
      const y = 250 - u * 110;
      const r = w.r * (0.6 + u);
      const a = w.a * Math.sin(Math.PI * u);
      const g2 = c.createRadialGradient(x, y, 0, x, y, r);
      g2.addColorStop(0, `rgba(230,232,236,${a})`); g2.addColorStop(1, 'rgba(230,232,236,0)');
      c.fillStyle = g2; c.beginPath(); c.arc(x, y, r, 0, TAU); c.fill();
    }
    // dust motes: only lit while inside a beam; snap to half-pixels for a pixel-art feel
    for (const m of motes) {
      const x = m.bx + m.ax * Math.sin(ph(t, m.fx) + m.p);
      const y = m.by + m.ay * Math.sin(ph(t, m.fy) + m.q);
      if (!inShaft(m.wx, x, y)) continue;
      const tw = 0.55 + 0.45 * Math.sin(ph(t, m.tw * 3) + m.p);
      c.fillStyle = `rgba(240,240,236,${m.a * tw})`;
      const sx = Math.round(x * 2) / 2, sy = Math.round(y * 2) / 2;
      c.fillRect(sx, sy, m.s, m.s);
    }
    // embers: dim amber bulbs (lamps off) breathing very slightly
    for (const lx of [100.5, 382.5]) {
      const a = 0.10 + 0.03 * Math.sin(ph(t, 2) + lx);
      const g2 = c.createRadialGradient(lx, 177.5, 0, lx, 177.5, 9);
      g2.addColorStop(0, `rgba(${AMBER},${a})`); g2.addColorStop(1, `rgba(${AMBER},0)`);
      c.fillStyle = g2; c.beginPath(); c.arc(lx, 177.5, 9, 0, TAU); c.fill();
    }
    // press impact: amber flash on the beat (pr keyframe 9.5% of 4 s = 0.38 s)
    const pt = ((t % 4) + 4) % 4 - 0.38;
    if (pt >= 0 && pt < 0.6) {
      const a = 0.55 * Math.exp(-pt * 7);
      const g2 = c.createRadialGradient(356, 247, 0, 356, 247, 34);
      g2.addColorStop(0, `rgba(${AMBER},${a})`); g2.addColorStop(1, `rgba(${AMBER},0)`);
      c.fillStyle = g2; c.beginPath(); c.arc(356, 247, 34, 0, TAU); c.fill();
    }
    // welding arc flicker on the left wall (wo: on during first 44% of 5 s)
    const wt = ((t % 5) + 5) % 5;
    if (wt < 2.2) {
      const fl = 0.6 + 0.4 * Math.abs(Math.sin(t * 47));
      const g2 = c.createRadialGradient(14, 160, 0, 14, 160, 30);
      g2.addColorStop(0, `rgba(${AMBER},${0.30 * fl})`); g2.addColorStop(0.3, `rgba(255,220,170,${0.10 * fl})`);
      g2.addColorStop(1, `rgba(${AMBER},0)`);
      c.fillStyle = g2; c.beginPath(); c.arc(14, 160, 30, 0, TAU); c.fill();
    }
  }

  drawCRT();
  drawShade();
  window.AW_drawFx = drawLight;
})();
