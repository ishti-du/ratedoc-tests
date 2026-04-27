import { test } from "@playwright/test";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { login } from "../helpers/auth.js";

const testDir = path.dirname(fileURLToPath(import.meta.url));
const authFile = path.resolve(testDir, "../.auth/user.json");

test("sign in and save authenticated browser state", async ({ page }) => {
  await login(page);
  await page.context().storageState({ path: authFile });
});
