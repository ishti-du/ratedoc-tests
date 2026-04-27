import { expect } from "@playwright/test";

export const REVIEW_DOCTOR = {
  name: "Dr. John Smith",
  slug: "dr-john-smith-7a055de9",
};

export function todayIsoDate() {
  return new Date().toISOString().split("T")[0];
}

export async function openReviewsTab(page, slug = REVIEW_DOCTOR.slug) {
  await page.goto(`/doctor/${slug}`);
  await expect(page.getByRole("heading", { name: REVIEW_DOCTOR.name, exact: true })).toBeVisible({
    timeout: 30_000,
  });

  const reviewsTab = page.getByRole("tab", { name: /reviews/i });
  if (await reviewsTab.isVisible().catch(() => false)) {
    await reviewsTab.click();
  }

  await expect(page.getByText(/Write a Review for/i)).toBeVisible({ timeout: 15_000 });
}

export function reviewForm(page) {
  return page.locator("form").filter({ hasText: /Write a Review for/i });
}

export async function setRating(page, label, rating) {
  const labelNode = reviewForm(page).getByText(label, { exact: false }).first();
  const group = labelNode.locator("xpath=ancestor::div[contains(@class, 'mb-4')][1]");
  const ratingRow = group.getByText("Poor").locator("xpath=ancestor::div[contains(@class, 'flex')][1]");
  await ratingRow.getByRole("button").nth(rating - 1).click();
}

export async function fillReviewForm(page, { comment, rating }) {
  const form = reviewForm(page);

  await setRating(page, "Listens & Answers Questions", rating);
  await setRating(page, "Explains Treatment Options", rating);
  await setRating(page, "Provides Effective Treatment", rating);
  await setRating(page, "Office Staff Cooperation", rating);
  await form.locator('input[type="date"]').fill(todayIsoDate());
  await setRating(page, "Your Overall Rating", rating);
  await form.getByPlaceholder("Share your experience...").fill(comment);
}

export async function deleteExistingReviewIfPresent(page) {
  const form = reviewForm(page);
  const deleteButton = form.getByRole("button", { name: /^Delete Review$/ });

  if (!(await deleteButton.isVisible().catch(() => false))) {
    return;
  }

  page.once("dialog", async (dialog) => {
    await dialog.accept();
  });

  await Promise.all([
    page.waitForResponse(
      (response) =>
        response.url().includes("/api/v1/reviews/") &&
        response.request().method() === "DELETE" &&
        response.ok(),
      { timeout: 30_000 }
    ),
    deleteButton.click(),
  ]);

  await expect(form.getByRole("button", { name: /^Submit Review$/ })).toBeVisible({
    timeout: 15_000,
  });
}
