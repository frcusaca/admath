import { defineConfig } from "@playwright/test";

// Uses the Chrome already installed on the machine (channel "chrome"),
// so `npx playwright install` is not needed. Run `make explorer` first.
export default defineConfig({
  testDir: "e2e",
  fullyParallel: true,
  reporter: [["list"]],
  use: { channel: "chrome", viewport: { width: 1200, height: 900 } },
});
