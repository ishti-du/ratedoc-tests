# 2. Doctor Review Required Fields Validation

## File

```text
tests/test_review_required_fields.py
```

---

## Purpose

Verify validation for required review fields.

---

## Steps Tested

1. Login as regular user  
2. Open doctor profile page  
3. Locate review form  
4. Leave Visit Date empty  
5. Leave Overall Rating empty  
6. Submit review  

---

## Expected Result

- Submission is blocked  
- User remains on doctor page  
- Validation behavior appears  

---

## Technologies Used

- Playwright  
- Python  
- Pytest  

---

# Setup

Navigate to the `e2e` folder:

```bash
cd e2e
```

---

# Create Virtual Environment

## Windows

```bash
python -m venv venv
venv\Scripts\activate
```

## Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

# Install Dependencies

```bash
pip install -r requirements.txt
playwright install
```

---

# Running Tests

## Run All Tests

```bash
pytest tests/ --base-url http://159.89.231.16:3000/
```

---

## Run Theme Toggle Test

```bash
pytest tests/test_theme_button.py --base-url http://159.89.231.16:3000/ -v
```

---

## Run Review Validation Test

```bash
pytest tests/test_review_required_fields.py --base-url http://159.89.231.16:3000/ -v
```

---

# Run Tests in Visible Browser

```bash
pytest tests/test_review_required_fields.py --base-url http://159.89.231.16:3000/ --headed -v
```

---

# Notes

- Playwright uses Chromium browser automation  
- Tests validate real frontend workflows  
- UI automation interacts with live pages and forms  
- Review validation test uses a regular user account for realistic testing  
