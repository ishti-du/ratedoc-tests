const API_URL = process.env.API_URL || "http://159.89.231.16:3001";

// Returns today's date as YYYY-MM-DD
export function todayDate() {
  return new Date().toISOString().split("T")[0];
}

export async function getAuthToken(request) {
  const response = await request.post(`${API_URL}/api/v1/auth/login`, {
    data: {
      email: process.env.TEST_USER_EMAIL || "testuser@example.com",
      password: process.env.TEST_USER_PASSWORD || "TestPassword123!",
    },
  });

  if (!response.ok()) {
    throw new Error(`Login failed: ${response.status()} ${await response.text()}`);
  }

  const body = await response.json();
  const token =
    body.access_token       ||
    body.token              ||
    body.accessToken        ||
    body.data?.access_token ||
    body.data?.token;

  if (!token) {
    throw new Error(`No token found. Keys: ${Object.keys(body).join(", ")}`);
  }

  return token;
}

export function authHeaders(token) {
  return {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
    Accept: "application/json",
  };
}

export async function getDoctorSlug(request, token) {
  const response = await request.get(
    `${API_URL}/api/v1/doctors?page=1&size=1&status=approved`,
    { headers: authHeaders(token) }
  );

  const body = await response.json();
  const doctors = body.data || body.items || body.results || body;
  const slug = doctors[0].slug || doctors[0].username || doctors[0].id;

  console.log(`[helper] Using doctor slug: ${slug}`);
  return slug;
}

export async function createReviewViaApi(request, token, overrides = {}) {
  const providerSlug =
    overrides.provider_slug || (await getDoctorSlug(request, token));

  const payload = {
    provider_type: "doctor",
    provider_slug: providerSlug,
    rating: 4,
    comment: `Auto-generated review ${Date.now()}`,
    visit_date: todayDate(),
    extra_info: {
      // question_scores confirmed required by API 422 response
      question_scores: [],
    },
    ...overrides,
  };

  console.log(`[helper] POST payload: ${JSON.stringify(payload)}`);

  const response = await request.post(`${API_URL}/api/v1/reviews`, {
    headers: authHeaders(token),
    data: payload,
  });

  const responseBody = await response.json();
  console.log(`[helper] POST status: ${response.status()}`);
  console.log(`[helper] POST body: ${JSON.stringify(responseBody).slice(0, 500)}`);

  if (!response.ok()) {
    throw new Error(
      `Failed to create review: ${response.status()} ${JSON.stringify(responseBody)}`
    );
  }

  return responseBody;
}

export async function deleteReviewViaApi(request, token, reviewId) {
  const response = await request.delete(
    `${API_URL}/api/v1/reviews/${reviewId}`,
    { headers: authHeaders(token) }
  );

  return response.status();
}