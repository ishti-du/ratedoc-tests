# RateDoc Tests

A repository for testing the RateDoc application (http://159.89.231.16:3000/).

For Swagger UI for API documents, visit: http://159.89.231.16:3001/docs

## Project Structure
- `e2e/`: End-to-end UI tests using Playwright (Python).
- `api/`: API tests using Postman/Newman (Node.js).

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
1. Activate the virtual environment (if not already activated):
   ```bash
   source venv/bin/activate
   ```
2. Run tests using pytest:
   ```bash
   pytest -s --headed --slowmo 500 tests/ --base-url http://159.89.231.16:3000
   ```

## API Testing (Newman CLI)
### Setup
1. Install Node.js (LTS).
2. Install dependencies:
   ```bash
   cd api
   npm install
   ```
### Execution
Run:
```bash
newman run /workspaces/ratedoc-tests/api/collections/Ian_Grinarml_RateDoc_Cities.postman_collection.json -e /workspaces/ratedoc-tests/api/environments/Ian_Grinarml_Staging.postman_environment.json
```