import { defineConfig } from "@playwright/test";

// Smoke tests for the rendered Quarto site (run `make site` first).
// A tiny static server serves ../_site over HTTP, as a real host would.
export default defineConfig({
  testDir: "e2e-site",
  reporter: [["list"]],
  use: { channel: "chrome", baseURL: "http://127.0.0.1:4877", viewport: { width: 1280, height: 1000 } },
  webServer: {
    command: "node scripts/serve.mjs ../_site 4877",
    url: "http://127.0.0.1:4877/index.html",
    reuseExistingServer: false,
  },
});
