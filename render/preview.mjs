// README preview: idle factory for 10 s, then the "agent working" light overlay flickers on.
// Captures the overlay (lights.svg) on transparent frames and composites it over the rendered scene frames.
import fs from 'node:fs';
import { open } from './harness.mjs';
const [svgPath, outDir, fps = '15', scale = '3'] = process.argv.slice(2);   // match the scene frames from render.sh
const W = 480 * +scale, H = 320 * +scale, FPS = +fps, N = 20 * FPS;
fs.mkdirSync(outDir, { recursive: true });
const svg = fs.readFileSync(svgPath, 'utf8').replace('<svg ', `<svg width='${W}' height='${H}' `);
const { browser, page, seek } = await open({ width: W, height: H });
await page.setContent(`<style>html,body{margin:0;background:transparent}</style>${svg}`);
for (let i = 0; i < N; i++) {
  await seek(i / FPS);
  await page.screenshot({ path: `${outDir}/l${String(i).padStart(4, '0')}.png`, omitBackground: true });
}
await browser.close();
