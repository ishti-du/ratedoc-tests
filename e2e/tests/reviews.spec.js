import { test, expect } from "@playwright/test";
import {
  fillReviewForm,
  openReviewsTab,
  deleteExistingReviewIfPresent,
  reviewForm,
} from "../helpers/review-ui.js";

test.describe.serial("Doctor Review", () => {
  test.beforeEach(async ({ page }) => {
    await openReviewsTab(page);
  });

  test("signed-in user can create a review with comment and rating", async ({ page }) => {
    await deleteExistingReviewIfPresent(page);

    const comment = `E2E create review ${Date.now()} with a clear helpful comment.`;
    await fillReviewForm(page, { comment, rating: 4 });

    await Promise.all([
      page.waitForResponse(
        (response) =>
          response.url().includes("/api/v1/reviews") &&
          response.request().method() === "POST" &&
          response.ok(),
        { timeout: 30_000 }
      ),
      reviewForm(page).getByRole("button", { name: /^Submit Review$/ }).click(),
    ]);

    await expect(reviewForm(page).getByRole("button", { name: /^Update Review$/ })).toBeVisible({
      timeout: 15_000,
    });
    await expect(reviewForm(page).getByPlaceholder("Share your experience...")).toHaveValue(comment);
  });

  test("signed-in user can update their review comment and rating", async ({ page }) => {
    const form = reviewForm(page);

    if (await form.getByRole("button", { name: /^Submit Review$/ }).isVisible().catch(() => false)) {
      await fillReviewForm(page, {
        comment: `E2E setup review ${Date.now()} before update.`,
        rating: 3,
      });
      await Promise.all([
        page.waitForResponse(
          (response) =>
            response.url().includes("/api/v1/reviews") &&
            response.request().method() === "POST" &&
            response.ok(),
          { timeout: 30_000 }
        ),
        form.getByRole("button", { name: /^Submit Review$/ }).click(),
      ]);
      await expect(form.getByRole("button", { name: /^Update Review$/ })).toBeVisible({
        timeout: 15_000,
      });
    }

    const updatedComment = `E2E updated review ${Date.now()} with a new rating.`;
    await fillReviewForm(page, { comment: updatedComment, rating: 5 });

    await Promise.all([
      page.waitForResponse(
        (response) =>
          response.url().includes("/api/v1/reviews/") &&
          response.request().method() === "PUT" &&
          response.ok(),
        { timeout: 30_000 }
      ),
      form.getByRole("button", { name: /^Update Review$/ }).click(),
    ]);

    await expect(form.getByPlaceholder("Share your experience...")).toHaveValue(updatedComment);
    await expect(page.getByText(updatedComment)).toBeVisible({ timeout: 15_000 });
  });
});
