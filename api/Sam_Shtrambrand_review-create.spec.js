import { test, expect } from "@playwright/test";
import {
  getAuthToken,
  authHeaders,
  getDoctorSlug,
  createReviewViaApi,
  todayDate,
} from "../helpers/api-helpers.js";

const API = process.env.API_URL || "http://159.89.231.16:3001";

test.describe("Create Review -- API", () => {
  let token;
  let doctorSlug;
  let createdReviewId;

  test.beforeAll(async ({ request }) => {
    token = await getAuthToken(request);
    doctorSlug = await getDoctorSlug(request, token);
  });

  test.afterAll(async ({ request }) => {
    if (createdReviewId) {
      await request.delete(`${API}/api/v1/reviews/${createdReviewId}`, {
        headers: authHeaders(token),
      });
      console.log(`[cleanup] Deleted review: ${createdReviewId}`);
    }
  });

  // -------------------------------------------------------------------------
  test("POST /api/v1/reviews -- creates a review with all required fields", async ({
    request,
  }) => {
    const reviewBody = await createReviewViaApi(request, token, {
      provider_slug: doctorSlug,
      rating: 4,
      comment: `Automated test review ${Date.now()}`,
    });

    const review = reviewBody.data || reviewBody;
    createdReviewId = review.id || review._id || review.review_id;

    expect(createdReviewId).toBeTruthy();
    console.log(`[reviews] Created review ID: ${createdReviewId}`);
  });

  // -------------------------------------------------------------------------
  test("POST /api/v1/reviews -- returns 422 when provider_slug is missing", async ({
    request,
  }) => {
    const response = await request.post(`${API}/api/v1/reviews`, {
      headers: authHeaders(token),
      data: {
        provider_type: "doctor",
        rating: 4,
        comment: "Missing provider_slug",
        visit_date: todayDate(),
        extra_info: {},
      },
    });

    expect(response.status()).toBe(422);
    const body = await response.json();
    expect(JSON.stringify(body)).toMatch(/provider_slug/i);
  });

  // -------------------------------------------------------------------------
  test("POST /api/v1/reviews -- returns 422 when provider_type is missing", async ({
    request,
  }) => {
    const response = await request.post(`${API}/api/v1/reviews`, {
      headers: authHeaders(token),
      data: {
        provider_slug: doctorSlug,
        rating: 4,
        comment: "Missing provider_type",
        visit_date: todayDate(),
        extra_info: {},
      },
    });

    expect(response.status()).toBe(422);
    const body = await response.json();
    expect(JSON.stringify(body)).toMatch(/provider_type/i);
  });

  // -------------------------------------------------------------------------
  test("POST /api/v1/reviews -- returns 422 when visit_date is missing", async ({
    request,
  }) => {
    const response = await request.post(`${API}/api/v1/reviews`, {
      headers: authHeaders(token),
      data: {
        provider_type: "doctor",
        provider_slug: doctorSlug,
        rating: 4,
        comment: "Missing visit_date",
        extra_info: {},
      },
    });

    expect(response.status()).toBe(422);
    const body = await response.json();
    expect(JSON.stringify(body)).toMatch(/visit_date/i);
  });

  // -------------------------------------------------------------------------
  test("POST /api/v1/reviews -- returns 401 without token", async ({
    request,
  }) => {
    const response = await request.post(`${API}/api/v1/reviews`, {
      headers: { "Content-Type": "application/json" },
      data: {
        provider_type: "doctor",
        provider_slug: doctorSlug,
        rating: 4,
        comment: "Should be rejected",
        visit_date: todayDate(),
        extra_info: {},
      },
    });

    expect(response.status()).toBe(401);
  });
});