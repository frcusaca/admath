// Copyright © 2026-present CAehi.us
// SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
/**
 * The port must look like the original page. Both are screenshotted in light and
 * dark, wide and phone-sized, and compared pixel by pixel. The only intended
 * differences, the new "Copy as NumPy" button and the copyright footer, are
 * hidden for the comparison.
 *
 * The original page loads its fonts from Google Fonts; without a network this
 * test is skipped rather than failed.
 */
import { expect, test } from "@playwright/test";
import pixelmatch from "pixelmatch";
import { PNG } from "pngjs";
import { ORIGINAL, STANDALONE } from "./helpers";

const cases = [
  { scheme: "light", width: 1200 },
  { scheme: "dark", width: 1200 },
  { scheme: "light", width: 390 },
  { scheme: "dark", width: 390 },
] as const;

for (const { scheme, width } of cases) {
  test(`matches the original: ${scheme}, ${width}px wide`, async ({ browser }) => {
    const shots: PNG[] = [];
    for (const url of [ORIGINAL, STANDALONE]) {
      const page = await browser.newPage({ viewport: { width, height: 900 }, colorScheme: scheme });
      await page.goto(url);
      if (url === STANDALONE) {
        await page.evaluate(() => {
          const s = document.createElement("style");
          s.textContent = "#copy, .foot { display: none !important; }";
          document.body.shadowRoot?.append(s);
        });
      } else {
        const fontsOk = await page.evaluate(async () => {
          await document.fonts.ready;
          return document.fonts.check('16px "Atkinson Hyperlegible"');
        });
        test.skip(!fontsOk, "Google Fonts not reachable, so the original page cannot be rendered faithfully");
      }
      await page.evaluate(() => document.fonts.ready);
      shots.push(PNG.sync.read(await page.screenshot({ fullPage: true })));
      await page.close();
    }
    const [a, b] = shots as [PNG, PNG];
    expect(b.height, "page height").toBe(a.height);
    const diff = new PNG({ width: a.width, height: a.height });
    const bad = pixelmatch(a.data, b.data, diff.data, a.width, a.height, { threshold: 0.1 });
    const ratio = bad / (a.width * a.height);
    expect(ratio, `${bad} pixels differ`).toBeLessThan(0.002);
  });
}
