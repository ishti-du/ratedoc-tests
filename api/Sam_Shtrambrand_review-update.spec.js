import { test, expect } from "@playwright/test";
import {
  getAuthToken,
  authHeaders,
  getDoctorSlug,
  createReviewViaApi,
  todayDate,
} from "../helpers/api-helpers.js";

const API = process.env.API_URL || "http://159.89.231.16:3001";

test.describe("Update Review -- API", () => {
  let token;
  let doctorSlug;
  let reviewId;

  test.beforeAll(async ({ request }) => {
    token = await getAuthToken(request);
    doctorSlug = await getDoctorSlug(request, token);

    const body = await createReviewViaApi(request, token, {
      provider_slug: doctorSlug,
      rating: 3,
      comment: `Review for update tests ${Date.now()}`,
    });

    const review = body.data || body;
    reviewId = review.id || review._id || review.review_id;

    expect(reviewId).toBeTruthy();
    console.log(`[update] Review ID for update tests: ${reviewId}`);
  });

  test.afterAll(async ({ request }) => {
    if (reviewId) {
      await request.delete(`${API}/api/v1/reviews/${reviewId}`, {
        headers: authHeaders(token),
      });
      console.log(`[update] Cleanup: deleted review ${reviewId}`);
    }
  });

  // -------------------------------------------------------------------------
  test("PUT /api/v1/reviews/{id} -- updates rating and comment", async ({
    request,
  }) => {
    const response = await request.put(
      `${API}/api/v1/reviews/${reviewId}`,
      {
        headers: authHeaders(token),
        data: {
          rating: 5,
          comment: `Updated comment ${Date.now()}`,
          visit_date: todayDate(),
          extra_info: {},
        },
      }
    );

    const body = await response.json();
    console.log(`[update] PUT status: ${response.status()}`);
    console.log(`[update] PUT body: ${JSON.stringify(body).slice(0, 300)}`);

    expect(response.status()).toBe(200);

    const review = body.data || body;
    expect(review.rating ?? review.data?.rating).toBe(5);
  });

  // -------------------------------------------------------------------------
  test("PUT /api/v1/reviews/{id} -- returns 401 without token", async ({
    request,
  }) => {
    const response = await request.put(
      `${API}/api/v1/reviews/${reviewId}`,
      {
        headers: { "Content-Type": "application/json" },
        data: {
          rating: 1,
          comment: "Should be rejected",
          visit_date: todayDate(),
          extra_info: {},
        },
      }
    );

    expect(response.status()).toBe(401);
  });

  // -------------------------------------------------------------------------
  test("PUT /api/v1/reviews/{id} -- returns 404 for a non-existent review", async ({
    request,
  }) => {
    const response = await request.put(
      `${API}/api/v1/reviews/00000000-0000-0000-0000-000000000000`,
      {
        headers: authHeaders(token),
        data: {
          rating: 1,
          comment: "Non-existent",
          visit_date: todayDate(),
          extra_info: {},
        },
      }
    );

    expect([404, 403]).toContain(response.status());
  });

  // -------------------------------------------------------------------------
  for (const action of ["approve", "reject", "pending"]) {
    test(`PUT /api/v1/admin/reviews/{id}/${action} -- skipped if not admin`, async ({
      request,
    }) => {
      const response = await request.put(
        `${API}/api/v1/admin/reviews/${reviewId}/${action}`,
        { headers: authHeaders(token) }
      );

      console.log(`[update] Admin ${action} status: ${response.status()}`);

      if (response.status() === 403) {
        test.skip();
        return;
      }

      expect(response.status()).toBe(200);
    });
  }
});