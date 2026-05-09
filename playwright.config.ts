import { defineConfig } from '@playwright/test';

export default defineConfig({
  // folder where our test files live
  testDir: './tests',

  // how long each test can run before it fails
  timeout: 30000,

  use: {
    // the website we are testing
    baseURL: 'http://159.89.231.16:3000',

    // take a screenshot if a test fails
    screenshot: 'only-on-failure',
  },
});