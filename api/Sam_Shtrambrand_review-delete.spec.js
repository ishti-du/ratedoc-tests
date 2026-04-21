import { test, expect } from "@playwright/test";
import {
  getAuthToken,
  authHeaders,
  getDoctorSlug,
  createReviewViaApi,
} from "../helpers/api-helpers.js";

const API = process.env.API_URL || "http://159.89.231.16:3001";

test.describe("Delete Review -- API", () => {
  let token;
  let doctorSlug;
  let reviewIdToDelete;

  test.beforeAll(async ({ request }) => {
    token = await getAuthToken(request);
    doctorSlug = await getDoctorSlug(request, token);

    const body = await createReviewViaApi(request, token, {
      provider_slug: doctorSlug,
      rating: 2,
      comment: `Disposable review for delete test ${Date.now()}`,
    });

    const review = body.data || body;
    reviewIdToDelete = review.id || review._id || review.review_id;

    expect(reviewIdToDelete).toBeTruthy();
    console.log(`[delete] Review to delete: ${reviewIdToDelete}`);
  });

  // -------------------------------------------------------------------------
  test("DELETE /api/v1/reviews/{id} -- deletes own review and returns 200 or 204", async ({
    request,
  }) => {
    const response = await request.delete(
      `${API}/api/v1/reviews/${reviewIdToDelete}`,
      { headers: authHeaders(token) }
    );

    console.log(`[delete] Delete status: ${response.status()}`);
    expect([200, 204]).toContain(response.status());

    const verify = await request.get(
      `${API}/api/v1/reviews/${reviewIdToDelete}`,
      { headers: authHeaders(token) }
    );

    console.log(`[delete] Verify status after delete: ${verify.status()}`);
    expect([404, 403]).toContain(verify.status());

    reviewIdToDelete = null;
  });

  // -------------------------------------------------------------------------
  test("DELETE /api/v1/reviews/{id} -- returns 404 for a non-existent review", async ({
    request,
  }) => {
    const response = await request.delete(
      `${API}/api/v1/reviews/00000000-0000-0000-0000-000000000000`,
      { headers: authHeaders(token) }
    );

    expect([404, 403]).toContain(response.status());
  });

  // -------------------------------------------------------------------------
  test("DELETE /api/v1/reviews/{id} -- returns 401 without token", async ({
    request,
  }) => {
    const tempBody = await createReviewViaApi(request, token, {
      provider_slug: doctorSlug,
      rating: 1,
      comment: "Target for 401 delete test",
    });

    const tempReview = tempBody.data || tempBody;
    const tempId = tempReview.id || tempReview._id || tempReview.review_id;

    const response = await request.delete(
      `${API}/api/v1/reviews/${tempId}`,
      { headers: { "Content-Type": "application/json" } }
    );

    expect(response.status()).toBe(401);

    // Clean up
    await request.delete(`${API}/api/v1/reviews/${tempId}`, {
      headers: authHeaders(token),
    });
  });
});