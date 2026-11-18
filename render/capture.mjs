// Deterministic frame capture: seek every animation + the canvas layers to t, screenshot.
import fs from 'node:fs';
import path from 'node:path';
import { open } from './harness.mjs';
const [page_, outDir, scale = '3', fps = '15', only] = process.argv.slice(2);
const S = +scale, W = 480 * S, H = 320 * S, LOOP = 20, N = LOOP * +fps;
fs.mkdirSync(outDir, { recursive: true });
const { browser, page, seek } = await open({ width: W, height: H, args: ['--hide-scrollbars', '--disable-lcd-text'] });
await page.goto('file://' + path.resolve(page_), { waitUntil: 'load' });
const frames = only ? only.split(',').map(Number) : [...Array(N).keys()];
for (const i of frames) {
  const t = only ? i : i / +fps;
  await seek(t);
  const name = only ? `t${t}.png` : `f${String(i).padStart(4, '0')}.png`;
  await page.screenshot({ path: path.join(outDir, name), clip: { x: 0, y: 0, width: W, height: H } });
  if (!only && i % 30 === 0) process.stdout.write(`frame ${i}/${N}\n`);
}
await browser.close();
