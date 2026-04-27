import { expect } from "@playwright/test";

export const TEST_USER = {
  email: process.env.TEST_USER_EMAIL || "samshtram@gamil.com",
  password: process.env.TEST_USER_PASSWORD || "beansandcheese",
  name: "Sam",
};

export async function login(page, user = TEST_USER) {
  await page.goto("/auth");

  await expect(page.getByRole("heading", { name: "Welcome back" })).toBeVisible();
  const form = page.locator("form");
  await form.getByLabel("Email").fill(user.email);
  await form.getByLabel("Password").fill(user.password);

  await Promise.all([
    page.waitForURL((url) => !url.pathname.includes("/auth"), { timeout: 30_000 }),
    form.getByRole("button", { name: /^sign in$/i }).click(),
  ]);
}
