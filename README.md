# RateDoc Tests

A repository for testing the RateDoc application (http://159.89.231.16:3000/).

For Swagger UI for API documents, visit: http://159.89.231.16:3001/docs

## Project Structure
- `e2e/`: End-to-end UI tests using Playwright (Python).
- `api/`: API tests using Postman/Newman (Node.js).

### Download
download the github repo and open a terminal at the folder

## UI Testing (Playwright Python)
Not completed

## API Testing (Newman CLI)
### Setup
1. Install Node.js (LTS).
2. Install dependencies:
   ```bash
   cd api
   npm install
   ```
3. Ensure testing files (Matthew_Kaplan_Test_ID_Photo.png and Matthew_Kaplan_Test_invalidfiletype) are in collections folder and named properly
### Execution

Run the default collection:
```bash
npm test
```

Run any collection manually:
```bash
newman run collections/<collection_file>.json -e environments/<environment_file>.json
```
Expected result: **28/28 assertions passed**

Run Matthew Kaplan's collection manually:
```bash
newman run collections/<Matthew_Kaplan_RateDoctor.postman_collection>.json -e environments/Matthew_Kaplan_Staging.postman_environment.json
```
Expected result: **28/28 assertions passed**
