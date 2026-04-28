# Keval Patel — RateDoc Tests

Tests for the two assigned cases:

| ID    | Page          | What we verify                                                                  |
| ----- | ------------- | ------------------------------------------------------------------------------- |
| TC7   | Home page     | Selecting a specialization (Cardiology) and clicking Search returns only Cardiology doctors. |
| TC26  | Hospitals page| Filtering by location (Cumilla) lists only hospitals in Cumilla.                |

Targets the staging environment:
- UI: http://159.89.231.16:3000/
- API: http://159.89.231.16:3001 (Swagger: http://159.89.231.16:3001/docs)

---

## E2E UI tests (Playwright + Python)

Files:
- `e2e/tests/Keval_Patel_test_tc7_specialization_search.py`
- `e2e/tests/Keval_Patel_test_tc26_hospital_location_filter.py`

### Setup
```bash
cd e2e
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install
```

### Run
```bash
# Just my tests:
pytest tests/Keval_Patel_test_tc7_specialization_search.py tests/Keval_Patel_test_tc26_hospital_location_filter.py -v

# With HTML report:
pytest tests/Keval_Patel_test_tc7_specialization_search.py tests/Keval_Patel_test_tc26_hospital_location_filter.py --html=report.html -v

# Headed (watch the browser):
pytest tests/Keval_Patel_test_tc7_specialization_search.py --headed -v
```

---

## API tests (Postman / Newman)

Files:
- `api/collections/Keval_Patel_RateDoc.postman_collection.json`
- `api/environments/Keval_Patel_Staging.postman_environment.json`

The collection is self-bootstrapping: it first looks up the Cardiology
department id and Cumilla city id from the API, then uses those values
in the filter requests.

### Setup
```bash
cd api
npm install         # installs newman locally
# or globally: npm install -g newman
```

### Run
```bash
# Using local newman:
npx newman run collections/Keval_Patel_RateDoc.postman_collection.json \
  -e environments/Keval_Patel_Staging.postman_environment.json

# Using global newman:
newman run collections/Keval_Patel_RateDoc.postman_collection.json \
  -e environments/Keval_Patel_Staging.postman_environment.json
```

### Importing into Postman (for live demo)
1. File → Import → drop in both JSON files.
2. Top-right environment selector → choose "Keval Patel - Staging".
3. Run the requests in order (the first two assign the lookup IDs to environment variables).

---

## What each request / test asserts

### TC7 — Specialization filter (Cardiology)
- **API**
  - `GET /api/v1/departments` — finds Cardiology id and stores it.
  - `GET /api/v1/doctors?department_id={id}` — every doctor's `specializations` field equals `Cardiology`.
  - `GET /api/v1/doctors?search=Cardiology` — same invariant on the search-style endpoint that backs the home page Search button.
- **UI**
  - Selecting "Cardiology" + clicking Search lands on `/search?q=Cardiology&type=doctor`.
  - At least one doctor card is rendered.
  - Every rendered doctor card includes the text "Cardiology".
  - No card carries a non-Cardiology tag (Dermatology / Pediatrics / etc.).

### TC26 — Hospital location filter (Cumilla)
- **API**
  - `GET /api/v1/cities` — finds Cumilla id and stores it.
  - `GET /api/v1/hospitals?city_id={cumilla_id}` — every hospital has `city_id === cumilla_id` and (when joined) `city.name === 'Cumilla'`.
  - `GET /api/v1/hospitals?city_id=1` — negative check that no Cumilla hospital leaks into a Dhaka filter.
  - `GET /api/v1/hospitals?city_id=999999` — invalid city returns empty list.
- **UI**
  - `/hospitals` renders the Location combobox.
  - Selecting "Cumilla" returns at least one hospital card.
  - Every hospital card mentions "Cumilla".
  - No hospital card mentions other major cities (Dhaka / Chittagong / Sylhet / etc.).
  - Unfiltered list size ≥ filtered list size (sanity check).

---

## Bugs found

### BUG-1 (TC7): Home-page specialization filter returns wrong specializations
- **Steps:** Home page → "Select Specialization" → "Cardiology" → Search.
- **Expected:** every doctor on `/search?q=Cardiology&type=doctor` is in Cardiology.
- **Actual:** Dr. John Smith (Dermatology) and Dr. Mohammad Rakibul Hasan Chowdhury (Dermatology) appear in the Cardiology result set.
- **Root cause guess:** clicking Search after picking a specialization navigates to `/search?q=<spec>&type=doctor`, which performs a free-text search across multiple fields rather than a strict `department_id` filter.
- **Caught by:** `test_all_results_are_in_cardiology`, `test_specialization_filter_excludes_other_specs` (marked `xfail` so the suite stays green; will flip to PASS automatically once fixed).

### Counter-example (TC26 works correctly)
The hospitals page Location filter does respect the selected city — every Cumilla query returns only Cumilla hospitals, both via UI and the underlying `/api/v1/hospitals?city_id=3` endpoint.

---

## Latest run summary
- Newman (API): **20/20 assertions pass** across 7 requests.
- Pytest (UI):   **7 pass, 2 xfail** (the 2 xfails document BUG-1 above).
