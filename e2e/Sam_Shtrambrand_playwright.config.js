import { defineConfig, devices } from "@playwright/test";
import path from "node:path";
import { fileURLToPath } from "node:url";

const configDir = path.dirname(fileURLToPath(import.meta.url));

export default defineConfig({
  testDir: path.join(configDir, "tests"),
  testMatch: /.*(?:\.spec|\.setup)\.js/,
  outputDir: path.join(configDir, "test-results"),
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,

  reporter: [
    ["html", { outputFolder: path.join(configDir, "playwright-report"), open: "never" }],
    ["list"],
  ],

  use: {
    baseURL: process.env.BASE_URL || "http://159.89.231.16:3000/",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    trace: "on-first-retry",
    actionTimeout: 15_000,
    navigationTimeout: 30_000,
  },

  projects: [
    {
      name: "setup",
      testMatch: /auth\.setup\.js/,
    },
    {
      name: "public",
      testMatch: /search-autocomplete\.spec\.js/,
      use: {
        ...devices["Desktop Chrome"],
      },
    },
    {
      name: "authenticated",
      testMatch: /reviews\.spec\.js/,
      use: {
        ...devices["Desktop Chrome"],
        storageState: path.join(configDir, ".auth/user.json"),
      },
      dependencies: ["setup"],
    },
  ],

  timeout: 60_000,
});
