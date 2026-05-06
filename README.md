# RateDoc Tests

A repository for testing the RateDoc application (http://159.89.231.16:3000/).

For Swagger UI for API documents, visit: http://159.89.231.16:3001/docs

## Project Structure
- `e2e/`: End-to-end UI tests using Playwright (Python).
- `api/`: API tests using Postman/Newman (Node.js).

### Download
download the github repo and open a terminal at the folder

## UI Testing (Playwright Python)
### Setup
1. Create and activate a virtual environment:
   ```bash
   cd e2e
   python3 -m venv venv
   source venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install-deps
   playwright install
   ```

### Execution

Run all e2e tests:
```bash
pytest tests/ --base-url http://159.89.231.16:3000/
```

Run only Gabriel Silva's tests:
```bash
pytest tests/Gabriel_Silva_test_home_add_provider.py tests/Gabriel_Silva_test_doctor_review_delete.py -v --base-url http://159.89.231.16:3000/
```

Run a single test file:
```bash
pytest tests/Gabriel_Silva_test_home_add_provider.py -v --base-url http://159.89.231.16:3000/
pytest tests/Gabriel_Silva_test_doctor_review_delete.py -v --base-url http://159.89.231.16:3000/
```

### Gabriel Silva's Tests — Step-by-Step

```bash
# 1. Go to the e2e folder
cd e2e

# 2. Activate the virtual environment
source venv/bin/activate

# 3. Run the tests
pytest tests/Gabriel_Silva_test_home_add_provider.py tests/Gabriel_Silva_test_doctor_review_delete.py -v --base-url http://159.89.231.16:3000/
```

Expected result: **5 passed**

## API Testing (Newman CLI)
### Setup
1. Install Node.js (LTS).
2. Install dependencies:
   ```bash
   cd api
   npm install
   ```

### Execution

Run the default collection:
```bash
npm test
```

Run Gabriel Silva's admin API tests:
```bash
newman run collections/Gabriel_Silva_RateDoc_Admin.postman_collection.json \
  -e environments/Gabriel_Silva_Staging.postman_environment.json
```

Run any collection manually:
```bash
newman run collections/<collection_file>.json -e environments/<environment_file>.json
```

### Gabriel Silva's Tests — Step-by-Step

```bash
# 1. Go to the api folder
cd api

# 2. Install dependencies (only needed once)
npm install

# 3. Run the collection
newman run collections/Gabriel_Silva_RateDoc_Admin.postman_collection.json \
  -e environments/Gabriel_Silva_Staging.postman_environment.json
```

Expected result: **20/20 assertions passed**
