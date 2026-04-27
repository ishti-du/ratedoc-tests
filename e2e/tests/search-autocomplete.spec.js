import { test, expect } from "@playwright/test";

const cases = [
  { query: "Stomach", suggestion: "Gastroenterology" },
  { query: "Heart", suggestion: "Cardiology" },
];

test.describe("Home page search autocomplete", () => {
  for (const { query, suggestion } of cases) {
    test(`${query} suggests ${suggestion}`, async ({ page }) => {
      const departmentsResponse = page.waitForResponse(
        (response) => response.url().includes("/api/v1/departments") && response.ok(),
        { timeout: 30_000 }
      );
      await page.goto("/");
      await departmentsResponse;

      const searchInput = page.getByPlaceholder("Search by disease or condition...");
      await expect(searchInput).toBeVisible();
      await searchInput.fill(query);

      await expect(page.getByRole("button", { name: new RegExp(suggestion, "i") })).toBeVisible({
        timeout: 10_000,
      });
    });
  }
});
