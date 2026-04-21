import { defineConfig, devices } from "@playwright/test";
import dotenv from "dotenv";

dotenv.config();

export default defineConfig({
  testDir: "./tests",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,

  reporter: [
    ["html", { outputFolder: "playwright-report", open: "never" }],
    ["list"],
  ],

  use: {
    baseURL: process.env.BASE_URL || "http://159.89.231.16:3000",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    trace: "on-first-retry",
    actionTimeout: 15_000,
  },

  projects: [
    // --- Auth Setup ---------------------------------------------------------
    {
      name: "setup",
      testMatch: /auth\.setup\.js/,
    },

    // --- Public project: no login required ----------------------------------
    // Used for pages that are accessible without authentication.
    // autocomplete.spec.js runs here.
    {
      name: "public",
      testMatch: /autocomplete\.spec\.js/,
      use: {
        ...devices["Desktop Chrome"],
        // No storageState -- does not depend on setup
      },
    },

    // --- Authenticated project: requires saved session ----------------------
    // All other specs (reviews, etc.) run here.
    {
      name: "chromium",
      testIgnore: /autocomplete\.spec\.js/,
      use: {
        ...devices["Desktop Chrome"],
        storageState: ".auth/user.json",
      },
      dependencies: ["setup"],
    },

    // --- API tests (no browser) ---------------------------------------------
    {
      name: "api",
      testMatch: /api-tests\.spec\.js/,
      use: {
        extraHTTPHeaders: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
      },
    },
  ],

  timeout: 60_000,
});