/**
 * SEARCH TESTS
 * ------------
 * Runs in serial mode with a single shared browser window.
 * One page is created in beforeAll and reused across all tests.
 */

import { test, expect, chromium } from "@playwright/test";

// ---------------------------------------------------------------------------
// Selectors
// ---------------------------------------------------------------------------
const SEARCH_INPUT    = 'input[placeholder="Search by disease or condition..."]';
const SEARCH_BUTTON   = 'button:has-text("Search")';
const RESULTS_HEADING = "Search Healthcare Providers";
const DOCTOR_CARD     = "h2, h3";

// ---------------------------------------------------------------------------
// Serial mode + shared page
// ---------------------------------------------------------------------------
test.describe.configure({ mode: "serial" });

test.describe("Search -- Disease to Doctor Results", () => {
  let page;

  test.beforeAll(async ({ browser }) => {
    // One browser context, one page, shared across every test in this file
    page = await browser.newPage();
  });

  test.afterAll(async () => {
    await page.close();
  });

  // -------------------------------------------------------------------------
  // Helper: fill search input and click Search, wait for API response
  // -------------------------------------------------------------------------
  async function performSearch(query) {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    const input = page.locator(SEARCH_INPUT);
    await expect(input).toBeVisible({ timeout: 10_000 });

    await input.clear();
    await input.fill(query);

    const [response] = await Promise.all([
      page.waitForResponse(
        (res) =>
          res.url().includes("/api/v1/doctors") &&
          res.url().includes(`search=${query}`) &&
          res.status() === 200,
        { timeout: 15_000 }
      ),
      page.locator(SEARCH_BUTTON).click(),
    ]);

    await expect(page).toHaveURL(
      new RegExp(`/search\\?.*q=${query}`),
      { timeout: 10_000 }
    );

    return response;
  }

  // =========================================================================
  // STOMACH
  // =========================================================================

  test("stomach: navigates to search results page", async () => {
    await performSearch("stomach");

    await expect(
      page.getByRole("heading", { name: RESULTS_HEADING })
    ).toBeVisible({ timeout: 10_000 });
  });

  test("stomach: URL contains q=stomach and type=doctor", async () => {
    const url = new URL(page.url());
    expect(url.searchParams.get("q")).toBe("stomach");
    expect(url.searchParams.get("type")).toBe("doctor");
  });

  test("stomach: at least one doctor card is returned", async () => {
    const firstDoctor = page.locator(DOCTOR_CARD).first();
    await expect(firstDoctor).toBeVisible({ timeout: 10_000 });

    const count = await page.locator(DOCTOR_CARD).count();
    console.log(`[search] Doctors returned for "stomach": ${count}`);
    expect(count).toBeGreaterThan(0);
  });

  test("stomach: API returns 200 with doctor array", async () => {
    const response = await performSearch("stomach");

    expect(response.status()).toBe(200);

    const body = await response.json();
    const doctors = body.data || body.results || body.items || body;

    expect(Array.isArray(doctors)).toBeTruthy();
    expect(doctors.length).toBeGreaterThan(0);
    console.log(`[search] API returned ${doctors.length} doctors for "stomach"`);
  });

  test("stomach: pressing Enter also triggers search", async () => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    const input = page.locator(SEARCH_INPUT);
    await expect(input).toBeVisible({ timeout: 10_000 });
    await input.fill("stomach");

    await Promise.all([
      page.waitForURL(/\/search\?.*q=stomach/, { timeout: 10_000 }),
      input.press("Enter"),
    ]);

    await expect(
      page.getByRole("heading", { name: RESULTS_HEADING })
    ).toBeVisible({ timeout: 10_000 });
  });

  // =========================================================================
  // HEART
  // =========================================================================

  test("heart: navigates to search results page", async () => {
    await performSearch("heart");

    await expect(
      page.getByRole("heading", { name: RESULTS_HEADING })
    ).toBeVisible({ timeout: 10_000 });
  });

  test("heart: URL contains q=heart and type=doctor", async () => {
    const url = new URL(page.url());
    expect(url.searchParams.get("q")).toBe("heart");
    expect(url.searchParams.get("type")).toBe("doctor");
  });

  test("heart: at least one doctor card is returned", async () => {
    const firstDoctor = page.locator(DOCTOR_CARD).first();
    await expect(firstDoctor).toBeVisible({ timeout: 10_000 });

    const count = await page.locator(DOCTOR_CARD).count();
    console.log(`[search] Doctors returned for "heart": ${count}`);
    expect(count).toBeGreaterThan(0);
  });

  test("heart: API returns 200 with doctor array", async () => {
    const response = await performSearch("heart");

    expect(response.status()).toBe(200);

    const body = await response.json();
    const doctors = body.data || body.results || body.items || body;

    expect(Array.isArray(doctors)).toBeTruthy();
    expect(doctors.length).toBeGreaterThan(0);
    console.log(`[search] API returned ${doctors.length} doctors for "heart"`);
  });

  test("heart: pressing Enter also triggers search", async () => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    const input = page.locator(SEARCH_INPUT);
    await expect(input).toBeVisible({ timeout: 10_000 });
    await input.fill("heart");

    await Promise.all([
      page.waitForURL(/\/search\?.*q=heart/, { timeout: 10_000 }),
      input.press("Enter"),
    ]);

    await expect(
      page.getByRole("heading", { name: RESULTS_HEADING })
    ).toBeVisible({ timeout: 10_000 });
  });

  // =========================================================================
  // CROSS-SEARCH
  // =========================================================================

  test("stomach and heart return different sets of doctors", async () => {
    await performSearch("stomach");
    const stomachDoctors = await page.locator(DOCTOR_CARD).allTextContents();

    await performSearch("heart");
    const heartDoctors = await page.locator(DOCTOR_CARD).allTextContents();

    console.log(`[search] Stomach doctors: ${stomachDoctors.length}`);
    console.log(`[search] Heart doctors:   ${heartDoctors.length}`);

    expect(stomachDoctors.join(",")).not.toBe(heartDoctors.join(","));
  });

  // =========================================================================
  // EDGE CASES
  // =========================================================================

  test("empty search input does not navigate away from home", async () => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    const input = page.locator(SEARCH_INPUT);
    await input.clear();

    await page.locator(SEARCH_BUTTON).click();
    await page.waitForTimeout(1_000);

    expect(page.url()).not.toMatch(/\/search/);
  });

  test("nonsense term shows empty or no-results state", async () => {
    await page.goto("/");
    await page.waitForLoadState("networkidle");

    const input = page.locator(SEARCH_INPUT);
    await input.fill("xyznonexistent999");

    await Promise.all([
      page.waitForURL(/\/search\?.*q=xyznonexistent999/, { timeout: 10_000 }),
      page.locator(SEARCH_BUTTON).click(),
    ]);

    const emptyVisible = await page
      .getByText(/no results|no doctors found|0 result|nothing found/i)
      .isVisible({ timeout: 5_000 })
      .catch(() => false);

    const doctorCount = await page.locator(DOCTOR_CARD).count();

    console.log(`[search] Nonsense -- emptyState: ${emptyVisible}, count: ${doctorCount}`);
    expect(emptyVisible || doctorCount === 0).toBeTruthy();
  });
});