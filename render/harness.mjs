// Shared headless-Brave harness for capture.mjs and preview.mjs.
// seek(t) pauses every animation at t seconds (and redraws the canvas layers when the page has them),
// then waits two animation frames so the screenshot shows the seeked state, not the previous one.
import puppeteer from 'puppeteer-core';

const BRAVE = process.env.BRAVE || '/Applications/Brave Browser.app/Contents/MacOS/Brave Browser';

export async function open({ width, height, args = [] }) {
  const browser = await puppeteer.launch({ executablePath: BRAVE, headless: true,
    args: ['--force-color-profile=srgb', ...args] });
  const page = await browser.newPage();
  await page.setViewport({ width, height, deviceScaleFactor: 1 });
  const seek = async (t) => {
    await page.evaluate((t) => {
      for (const a of document.getAnimations()) { a.pause(); a.currentTime = t * 1000; }
      if (window.AW_drawFx) window.AW_drawFx(t);
    }, t);
    await page.evaluate(() => new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r))));
  };
  return { browser, page, seek };
}
