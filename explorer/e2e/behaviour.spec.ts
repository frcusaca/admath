// Copyright © 2026-present CAehi.us
// SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
import { readFileSync } from "node:fs";
import { expect, test } from "@playwright/test";
import { LIBRARY, q, STANDALONE } from "./helpers";

test.describe("standalone page", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(STANDALONE);
  });

  test("starts like the original: a first, b second, +45°", async ({ page }) => {
    await expect(q(page, "#read .eq")).toContainText("⟨a, b⟩ = (4)(3) + (0)(3) = 12");
    await expect(q(page, "#read")).toContainText("+45°");
    await expect(q(page, "#f0")).toBeChecked();
    await expect(q(page, "#s1")).toBeChecked();
    await expect(page.locator("main")).toHaveCount(1);
  });

  test("the standalone page shows the copyright notice and license", async ({ page }) => {
    await expect(q(page, "footer.foot")).toHaveText("Copyright © 2026-present CAehi.us. Prosperity Public License 3.0.0.");
  });

  test("dragging a tip moves the vector and updates every view", async ({ page }) => {
    const box = (await q(page, "#plot").boundingBox())!;
    // paper → screen: viewBox is 552 wide starting at −16; one step is 520/17
    const toScreen = (x: number, y: number) => ({
      x: box.x + ((260 + (x * 520) / 17 + 16) / 552) * box.width,
      y: box.y + ((260 - (y * 520) / 17 + 16) / 552) * box.height,
    });
    const from = toScreen(3, 3);
    const to = toScreen(-2, 5);
    await page.mouse.move(from.x, from.y);
    await page.mouse.down();
    await page.mouse.move(to.x, to.y, { steps: 8 });
    await page.mouse.up();
    await expect(q(page, "#vx1")).toHaveValue("-2");
    await expect(q(page, "#vy1")).toHaveValue("5");
    await expect(q(page, "#read .eq")).toContainText("= −8");
    await expect(q(page, "#gm0-1")).toHaveText("−0.37");
  });

  test("keyboard: radios, the pair table and the table inputs keep focus after redraws", async ({ page }) => {
    await q(page, "#s1").focus();
    await page.keyboard.press("ArrowDown"); // 2nd → c
    await expect(q(page, "#s2")).toBeChecked();
    await expect(q(page, "#s2")).toBeFocused();
    await expect(q(page, "#read .eq")).toContainText("⟨a, c⟩");

    await q(page, "#gm3-4").focus();
    await page.keyboard.press("Enter");
    await expect(q(page, "#read .eq")).toContainText("⟨d, e⟩");
    await expect(q(page, "#gm3-4")).toBeFocused();

    await q(page, "#vx0").fill("-6");
    await expect(q(page, "#vx0")).toBeFocused();
    await expect(q(page, "#vl0")).toHaveText("6");
  });

  test("focus is visible on buttons reached by keyboard", async ({ page }) => {
    await q(page, "#swap").focus();
    await page.keyboard.press("Tab");
    const outline = await q(page, "#spin").evaluate((el) => getComputedStyle(el).outlineStyle);
    await expect(q(page, "#spin")).toBeFocused();
    expect(outline).toBe("solid");
  });

  test("the diagonal of the pair table is skipped by Tab and does nothing", async ({ page }) => {
    await expect(q(page, "#gm2-2")).toHaveAttribute("tabindex", "-1");
    await q(page, "#gm2-2").click();
    await expect(q(page, "#read .eq")).toContainText("⟨a, b⟩");
  });

  test("Spin animates, locks the editors, and puts the vector back", async ({ page }) => {
    await q(page, "#spin").click();
    await expect(q(page, "#spin")).toHaveText("Stop");
    await expect(q(page, "#add")).toBeDisabled();
    await expect(q(page, "#copy")).toBeDisabled();
    await expect(q(page, "#vx0")).toBeDisabled();
    await page.waitForTimeout(400);
    await q(page, "#spin").click();
    await expect(q(page, "#spin")).toHaveText("Spin b once around");
    await expect(q(page, "#vx1")).toHaveValue("3");
    await expect(q(page, "#vy1")).toHaveValue("3");
    expect(await q(page, "#trace .dot").count()).toBeGreaterThan(0);
  });

  test("blue and orange follow the sign only", async ({ page }) => {
    // left turn and right turn of the same size: same colour
    await q(page, "#vy1").fill("-3");
    await expect(q(page, "#plot path.arc")).toHaveClass(/pos/);
    await expect(q(page, "#read")).toContainText("clockwise");
    // right angle: neither colour
    await q(page, "#vx1").fill("0");
    await expect(q(page, "#plot path.arc")).toHaveClass(/flat/);
    await expect(q(page, "#plot path.square")).toHaveCount(1);
  });

  test("Copy as NumPy writes Python to the clipboard and shows it", async ({ page, context }) => {
    await context.grantPermissions(["clipboard-read", "clipboard-write"]);
    await q(page, "#vx1").fill("-2.5");
    await q(page, "#copy").click();
    const expected =
      "a = np.array([4, 0])\nb = np.array([-2.5, 3])\nc = np.array([0, 5])\nd = np.array([-4, 2])\ne = np.array([-2, -4])";
    await expect(q(page, "#code")).toHaveValue(expected);
    await expect(q(page, "#copymsg")).toHaveText("Copied. Paste it into a code cell.");
    expect(await page.evaluate(() => navigator.clipboard.readText())).toBe(expected);
    await q(page, "#vx0").fill("1");
    await expect(q(page, "#copymsg")).toContainText("changed");
  });

  test("Copy as NumPy still shows the code when the clipboard is blocked", async ({ page }) => {
    await page.evaluate(() => {
      Object.defineProperty(navigator, "clipboard", { value: undefined, configurable: true });
      document.execCommand = () => false;
    });
    await q(page, "#copy").click();
    await expect(q(page, "#code")).toBeVisible();
    await expect(q(page, "#copymsg")).toContainText("Select the code below");
    await expect(q(page, "#code")).toBeFocused();
  });

  test("add and remove vectors", async ({ page }) => {
    await q(page, "#add").click();
    await expect(q(page, "#vt tbody tr")).toHaveCount(6);
    await expect(q(page, "#read .eq")).toContainText("⟨b, f⟩");
    await q(page, "#del5").click();
    await expect(q(page, "#vt tbody tr")).toHaveCount(5);
  });
});

test("reduced motion: Spin draws the whole curve at once", async ({ browser }) => {
  const page = await browser.newPage({ reducedMotion: "reduce" });
  await page.goto(STANDALONE);
  await q(page, "#spin").click();
  await expect(q(page, "#spin")).toHaveText("Spin b once around");
  await expect(q(page, "#trace .dot")).toHaveCount(181);
  await page.close();
});

test("dark theme follows the system, and the theme option overrides it", async ({ browser }) => {
  const page = await browser.newPage({ colorScheme: "dark" });
  await page.goto(STANDALONE);
  const paper = () => page.evaluate(() => getComputedStyle(document.body).getPropertyValue("--paper").trim());
  expect(await paper()).toBe("#101c17");
  await page.evaluate(() => document.body.setAttribute("data-theme", "light"));
  expect(await paper()).toBe("#eaf0df");
  await page.close();
});

test("the ES module mounts two independent explorers with their own vectors and names", async ({ page }) => {
  // Serve the real ES module from a fake origin, exactly as a page would import it.
  await page.route("https://explorer.test/**", (route) => {
    const path = new URL(route.request().url()).pathname;
    if (path === "/angle-explorer.js") {
      return route.fulfill({ contentType: "text/javascript", body: readFileSync(LIBRARY, "utf-8") });
    }
    return route.fulfill({
      contentType: "text/html",
      body: `<!doctype html><meta charset="utf-8">
        <style>body { text-align: center; font: 30px serif; } #plot { color: red; }</style>
        <div id="one"></div><div id="two"></div>
        <script type="module">
          import { mountAngleExplorer } from "./angle-explorer.js";
          window.h1 = mountAngleExplorer(document.getElementById("one"), { vectors: [[1, 2], [3, -1]], names: ["u", "w"], header: false });
          window.h2 = mountAngleExplorer(document.getElementById("two"), { vectors: [[0, 5], [5, 0], [1, 1]], theme: "dark" });
        </script>`,
    });
  });
  await page.goto("https://explorer.test/");
  const one = page.locator("#one");
  const two = page.locator("#two");
  await expect(one.locator("#read .eq")).toContainText("⟨u, w⟩ = (1)(3) + (2)(−1) = 1");
  await expect(two.locator("#read .eq")).toContainText("⟨a, b⟩ = (0)(5) + (5)(0) = 0");
  await expect(one.locator("h1")).toHaveCount(0);
  await expect(one.locator("[role=region]")).toHaveCount(1);
  await expect(one.locator("footer")).toHaveCount(0);   // embedded explorers carry no footer by default
  // radios in different explorers are different groups
  await two.locator("#s2").check();
  await expect(one.locator("#s1")).toBeChecked();
  // page CSS does not leak in
  const align = await one.locator("#tip").evaluate((el) => getComputedStyle(el).textAlign);
  expect(align).toBe("start");
  await expect(two).toHaveAttribute("data-theme", "dark");
  expect(await page.evaluate(() => (window as any).h1.toNumpy())).toBe("u = np.array([1, 2])\nw = np.array([3, -1])");
  // fonts are installed once for the whole page
  expect(await page.locator("style#angle-explorer-fonts").count()).toBe(1);
});
