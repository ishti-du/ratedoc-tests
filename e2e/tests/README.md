# End-to-End (E2E) Tests – RateDoctor

This directory contains end-to-end (E2E) tests for the RateDoctor application using **Playwright**, **Python**, and **pytest**.

These tests simulate real user interactions in a browser to validate application behavior and UI functionality.

## Requirements

All dependencies are listed in `requirements.txt`:

## test_helpful_review.py
- Tests the Helpful and Not Helpful button functionality in the review section
- Ensures UI state updates correctly after user actions
  
## test_pending_provider.py
- Tests workflow for Pending Providers
- Approves a pending provider and verifies that system stats update correctly
- Confirms that the provider appears in search results via: "View Site" navigation
- Search functionality reflecting newly approved provider

# Setup Instructions

1. Create a virtual environment

```base
python -m venv venv
```

2. Activate the virtual environment

```bash
Windows:
venv\Scripts\activate
macOS / Linux:
source venv/bin/activate
```
3. Install dependencies

```bash
pip install -r requirements.txt
```

4. Install Playwright browser binaries (Chromium)

```bash
playwright install chromium
```

# Running the E2E Tests

Run all tests in verbose mode:
```bash
pytest test_helpful_toggle.py -v
```

```bash
pytest test_pending_providers.py -v
```



