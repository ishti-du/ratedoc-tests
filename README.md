# RateDoctor.io API Testing – Team 3

## Author
Anatoly Barabanov

---

# Overview

This folder contains Postman/Newman API test collections created for the RateDoctor.io project.

The API tests validate Team 3 backend endpoints related to:
- Departments
- Doctors
- Hospitals
- Authentication
- Hospital approval workflow

---

# Tested Endpoints

## 1. GET /api/v1/departments

### Purpose

Verify that the departments endpoint works correctly.

### Validations

- Status code is 200
- Response is JSON
- Departments list exists

---

## 2. POST /api/v1/auth/login

### Purpose

Authenticate admin user and retrieve JWT access token.

### Validations

- Successful login response
- Access token exists

### Token Handling

The token is automatically saved into the Postman environment variable:

```javascript
adminToken
```

### Example Test Script

```javascript
let json = pm.response.json();

let token =
    json.access_token ||
    json.token ||
    json.data?.access_token;

pm.test("Login success", function () {
    pm.expect(pm.response.code).to.be.oneOf([200, 201]);
});

pm.test("Token exists", function () {
    pm.expect(token).to.exist;
});

pm.environment.set("adminToken", token);
```

---

## 3. PUT /api/v1/hospitals/{slug}/approve

### Purpose

Verify that an admin can approve hospitals.

### Authorization

Bearer Token:

```text
{{adminToken}}
```

### Validations

- Authorized request succeeds
- Proper response status returned
- Authentication works correctly

---

## 4. GET /api/v1/doctors/{slug}/hospitals

### Purpose

Verify that doctor-hospital relationships can be retrieved.

### Validations

- Successful response
- JSON response
- Hospital data exists

---

# Technologies Used

- Postman
- Newman CLI
- REST API Testing
- JSON Validation

---

# Running Tests

## Using Postman

1. Import the exported collection JSON
2. Select the correct environment
3. Run requests individually or use Collection Runner

---

## Using Newman CLI

From the `api` directory:

```bash
npm install
```

Run tests:

```bash
npm test
```

or:

```bash
newman run Anatoly_Barabanov_Team3_API_Tests.json
```

---

# Notes

- Tests are independent
- Authentication token is dynamically saved after login
- Real API endpoints are used
- Real hospital and doctor slugs are tested
