// Deterministic frame capture: seek every animation + the canvas layers to t, screenshot.
import puppeteer from 'puppeteer-core';
import fs from 'node:fs';
import path from 'node:path';
const [page_, outDir, scale = '3', fps = '15', only] = process.argv.slice(2);
const S = +scale, W = 480 * S, H = 320 * S, LOOP = 20, N = LOOP * +fps;
const BRAVE = process.env.BRAVE || '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser';
fs.mkdirSync(outDir, { recursive: true });
const browser = await puppeteer.launch({ executablePath: BRAVE, headless: true,
  args: ['--hide-scrollbars', '--force-color-profile=srgb', '--disable-lcd-text'] });
const page = await browser.newPage();
await page.setViewport({ width: W, height: H, deviceScaleFactor: 1 });
await page.goto('file://' + path.resolve(page_), { waitUntil: 'load' });
const frames = only ? only.split(',').map(Number) : [...Array(N).keys()];
for (const i of frames) {
  const t = only ? i : i / +fps;
  await page.evaluate((t) => window.AW_seek(t), t);
  await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  const name = only ? `t${t}.png` : `f${String(i).padStart(4, '0')}.png`;
  await page.screenshot({ path: path.join(outDir, name), clip: { x: 0, y: 0, width: W, height: H } });
  if (!only && i % 30 === 0) process.stdout.write(`frame ${i}/${N}\n`);
}
await browser.close();
