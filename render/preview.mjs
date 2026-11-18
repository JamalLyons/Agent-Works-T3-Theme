// README preview: idle factory for 10 s, then the "agent working" light overlay flickers on.
// Captures the overlay (lights.svg) on transparent frames and composites it over the rendered scene frames.
import puppeteer from 'puppeteer-core';
import fs from 'node:fs';
const [svgPath, outDir] = process.argv.slice(2);
const W = 1440, H = 960, FPS = 15, N = 300;
const BRAVE = process.env.BRAVE || '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser';
fs.mkdirSync(outDir, { recursive: true });
const svg = fs.readFileSync(svgPath, 'utf8').replace('<svg ', `<svg width='${W}' height='${H}' `);
const browser = await puppeteer.launch({ executablePath: BRAVE, headless: true, args: ['--force-color-profile=srgb'] });
const page = await browser.newPage();
await page.setViewport({ width: W, height: H });
await page.setContent(`<style>html,body{margin:0;background:transparent}</style>${svg}`);
for (let i = 0; i < N; i++) {
  await page.evaluate((t) => document.getAnimations().forEach((a) => { a.pause(); a.currentTime = t * 1000; }), i / FPS);
  await page.screenshot({ path: `${outDir}/l${String(i).padStart(4, '0')}.png`, omitBackground: true });
}
await browser.close();
