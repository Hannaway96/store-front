# API Schema

**Store Front API** - Backend service endpoints for store front application.

**Version:** 1.0.0

## Base URL

```
http://localhost:8000
```

## Authentication

Most endpoints require JWT (JSON Web Token) authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

Access tokens expire after 60 minutes. Use the refresh endpoint to obtain a new access token.

---

## Endpoints

### Authentication Endpoints

#### 1. Register User

Register a new user account.

**Endpoint:** `POST /auth/register/`

**Authentication:** Not required (public endpoint)

**Request Body:**
```json
{
  "email": "string (email, required, max 255 chars)",
  "password": "string (required, min 8 chars, write-only)",
  "password_confirm": "string (required, write-only)",
  "first_name": "string (required, max 255 chars)",
  "last_name": "string (required, max 255 chars)",
  "date_of_birth": "date (required, format: YYYY-MM-DD, user must be 18+)"
}
```

**Response:** `201 Created`
```json
{
  "user": {
    "id": "integer (read-only)",
    "email": "string (email)",
    "first_name": "string",
    "last_name": "string",
    "date_of_birth": "date"
  },
  "tokens": {
    "access": "string (JWT access token)",
    "refresh": "string (JWT refresh token)"
  }
}
```

**Error Responses:**
- `400 Bad Request` - Invalid input data (e.g., passwords don't match, user under 18)
- `409 Conflict` - User with this email already exists

**Validation Rules:**
- Email must be valid and unique
- Password must be at least 8 characters
- Passwords must match
- User must be 18 years or older
- A profile is automatically created for the new user

---

#### 2. Login

Authenticate user and obtain JWT tokens.

**Endpoint:** `POST /auth/login/`

**Authentication:** Not required (public endpoint)

**Request Body:**
```json
{
  "email": "string (required)",
  "password": "string (required, write-only)"
}
```

**Response:** `200 OK`
```json
{
  "access": "string (JWT access token, read-only)",
  "refresh": "string (JWT refresh token, read-only)"
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid credentials

---

#### 3. Refresh Token

Obtain a new access token using a refresh token.

**Endpoint:** `POST /auth/refresh/`

**Authentication:** Not required (public endpoint)

**Request Body:**
```json
{
  "refresh": "string (required, min 1 char)"
}
```

**Response:** `200 OK`
```json
{
  "access": "string (JWT access token, read-only)",
  "refresh": "string (JWT refresh token, read-only)"
}
```

**Note:** Refresh tokens expire after 7 days. Tokens are rotated and blacklisted after use.

---

### User Endpoints

#### 4. Get User Details

Retrieve user information by ID.

**Endpoint:** `GET /users/{id}/`

**Authentication:** Required (JWT)

**Permissions:** User must be the owner of the account

**Path Parameters:**
- `id` (integer, required) - User ID

**Response:** `200 OK`
```json
{
  "id": "integer (read-only)",
  "email": "string (email)",
  "first_name": "string",
  "last_name": "string",
  "date_of_birth": "date"
}
```

**Error Responses:**
- `401 Unauthorized` - Missing or invalid authentication token
- `403 Forbidden` - User is not the owner of this account
- `404 Not Found` - User not found

---

#### 5. Update User (Full)

Update all user fields. All fields must be provided.

**Endpoint:** `PUT /users/{id}/`

**Authentication:** Required (JWT)

**Permissions:** User must be the owner of the account

**Path Parameters:**
- `id` (integer, required) - User ID

**Request Body:**
```json
{
  "email": "string (email, required, max 255 chars)",
  "first_name": "string (required, max 255 chars)",
  "last_name": "string (required, max 255 chars)",
  "date_of_birth": "date (required)"
}
```

**Response:** `200 OK`
```json
{
  "id": "integer (read-only)",
  "email": "string (email)",
  "first_name": "string",
  "last_name": "string",
  "date_of_birth": "date"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid input data
- `401 Unauthorized` - Missing or invalid authentication token
- `403 Forbidden` - User is not the owner of this account
- `404 Not Found` - User not found

---

#### 6. Update User (Partial)

Partially update user fields. Only provided fields will be updated.

**Endpoint:** `PATCH /users/{id}/`

**Authentication:** Required (JWT)

**Permissions:** User must be the owner of the account

**Path Parameters:**
- `id` (integer, required) - User ID

**Request Body:** (all fields optional)
```json
{
  "email": "string (email, max 255 chars)",
  "first_name": "string (max 255 chars)",
  "last_name": "string (max 255 chars)",
  "date_of_birth": "date"
}
```

**Response:** `200 OK`
```json
{
  "id": "integer (read-only)",
  "email": "string (email)",
  "first_name": "string",
  "last_name": "string",
  "date_of_birth": "date"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid input data
- `401 Unauthorized` - Missing or invalid authentication token
- `403 Forbidden` - User is not the owner of this account
- `404 Not Found` - User not found

---

### Profile Endpoints

#### 7. Get User Profile

Retrieve a user's public profile information.

**Endpoint:** `GET /users/{user__id}/profile/`

**Authentication:** Required (JWT)

**Permissions:** User must be authenticated (read-only access for any authenticated user)

**Path Parameters:**
- `user__id` (integer, required) - User ID

**Response:** `200 OK`
```json
{
  "display_name": "string (max 100 chars)",
  "bio": "string (max 500 chars)",
  "location": "string (max 100 chars)"
}
```

**Error Responses:**
- `401 Unauthorized` - Missing or invalid authentication token
- `404 Not Found` - Profile not found

---

#### 8. Update Profile (Full)

Update all profile fields. All fields must be provided.

**Endpoint:** `PUT /users/{user__id}/profile/`

**Authentication:** Required (JWT)

**Permissions:** User must be the owner of the profile

**Path Parameters:**
- `user__id` (integer, required) - User ID

**Request Body:**
```json
{
  "display_name": "string (max 100 chars)",
  "bio": "string (max 500 chars)",
  "location": "string (max 100 chars)"
}
```

**Response:** `200 OK`
```json
{
  "display_name": "string (max 100 chars)",
  "bio": "string (max 500 chars)",
  "location": "string (max 100 chars)"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid input data
- `401 Unauthorized` - Missing or invalid authentication token
- `403 Forbidden` - User is not the owner of this profile
- `404 Not Found` - Profile not found

---

#### 9. Update Profile (Partial)

Partially update profile fields. Only provided fields will be updated.

**Endpoint:** `PATCH /users/{user__id}/profile/`

**Authentication:** Required (JWT)

**Permissions:** User must be the owner of the profile

**Path Parameters:**
- `user__id` (integer, required) - User ID

**Request Body:** (all fields optional)
```json
{
  "display_name": "string (max 100 chars)",
  "bio": "string (max 500 chars)",
  "location": "string (max 100 chars)"
}
```

**Response:** `200 OK`
```json
{
  "display_name": "string (max 100 chars)",
  "bio": "string (max 500 chars)",
  "location": "string (max 100 chars)"
}
```

**Error Responses:**
- `400 Bad Request` - Invalid input data
- `401 Unauthorized` - Missing or invalid authentication token
- `403 Forbidden` - User is not the owner of this profile
- `404 Not Found` - Profile not found

---

## Data Models

### User Model
```json
{
  "id": "integer (read-only, auto-generated)",
  "email": "string (email, unique, max 255 chars)",
  "first_name": "string (max 255 chars)",
  "last_name": "string (max 255 chars)",
  "date_of_birth": "date (YYYY-MM-DD format)"
}
```

### Profile Model
```json
{
  "display_name": "string (max 100 chars, optional)",
  "bio": "string (max 500 chars, optional)",
  "location": "string (max 100 chars, optional)"
}
```

**Note:** Profile is automatically created when a user registers. Each user has exactly one profile.

---

## Token Information

### Access Token
- **Lifetime:** 60 minutes
- **Usage:** Include in `Authorization: Bearer <token>` header for authenticated requests
- **Format:** JWT (JSON Web Token)

### Refresh Token
- **Lifetime:** 7 days
- **Usage:** Use with `/auth/refresh/` endpoint to obtain new access token
- **Rotation:** Tokens are rotated and blacklisted after use
- **Format:** JWT (JSON Web Token)

---

## Common Error Responses

### 400 Bad Request
Invalid request data or validation errors.

### 401 Unauthorized
Missing or invalid authentication token.

### 403 Forbidden
User does not have permission to perform this action.

### 404 Not Found
The requested resource does not exist.

### 409 Conflict
Resource conflict (e.g., email already exists).

---

## API Documentation

Interactive API documentation is available at:
- **Swagger UI:** `http://localhost:8000/docs/`
- **OpenAPI Schema:** `http://localhost:8000/schema/`

---

## Notes

- All dates should be in `YYYY-MM-DD` format
- All endpoints accept `application/json` content type
- JWT tokens use Bearer authentication scheme
- User registration automatically creates a profile
- Users must be 18 years or older to register
- Email addresses must be unique across the system

