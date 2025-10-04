# ai-job-killer-Server ![MIT License](https://img.shields.io/badge/license-MIT-green)


**ai-job-killer-Server** is a **FastAPI-powered backend** designed for **user management and YouTube transcript extraction**. It provides **secure JWT-based authentication**, **real-time user handling**, and **easy access to YouTube transcripts**, all orchestrated with **PostgreSQL, Redis, and Docker** for **scalable, production-ready performance**.

With ai-job-killer-Server, developers can:
- **Onboard users instantly** with email verification  
- **Secure APIs** with JWT tokens for protected resources  
- **Fetch YouTube transcripts** in multiple languages, including optional SRT formatting  
- **Cache results efficiently** using Redis for fast API responses  
- **Deploy quickly** using Docker for reproducible, scalable infrastructure  

While ai-job-killer-Server focuses on user management and transcript extraction, these features provide a **ready-made foundation for building AI-driven content tools, blogging platforms, or research applications**.  

Step into the future of content-driven development with a **robust, scalable, and secure backend** that accelerates your projects.

## Table of Contents

- [Features](#features)  
- [Architecture](#architecture)  
- [Setup & Installation](#setup--installation)  
- [Docker Workflow](#docker-workflow)  
- [Authentication APIs](#authentication-apis)  
- [Transcript API](#transcript-api)  
- [Example Workflow](#example-workflow)  
- [Environment Variables](#environment-variables)  
- [License](#license)  

## Features

- **User authentication** (register/login) with JWT tokens  
- **YouTube transcript extraction** by video ID  
- Returns **cleaned text** and **SRT-formatted transcripts**  
- PostgreSQL database for storing user info  
- Redis caching for transcript storage  
- Dockerized, minimal-touch workflow  
- Swagger/OpenAPI docs at `/docs`  

## Architecture

- **FastAPI**: Main API server  
- **PostgreSQL**: User and application data  
- **Redis**: Transcript caching  
- **Docker**: Service orchestration  

## Setup & Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/ai-job-killer-server.git
cd ai-job-killer-server
````

2. **Create a `.env` file** with the following variables:

```dotenv
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=fastapi_db
POSTGRES_HOST=db
POSTGRES_PORT=5432

JWT_SECRET=ai-job-killer-secret-key
JWT_ALG=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-smtp-password
EMAIL_FROM="ai-job-killer <your-email@gmail.com>"
APP_BASE_URL=http://localhost:8000

REDIS_HOST=redis
REDIS_PORT=6379
```

3. **Build and run services:**

```bash
docker compose up --build
```

4. **Database import/export**:

* Export: `bash ./export_db.sh all`
* Import is automated on container startup if `db_dump.sql` exists


## Docker Workflow

* **db**: PostgreSQL, waits for readiness before import
* **redis**: Redis cache for caching transcripts
* **server**: FastAPI app, imports DB dump automatically
---

## Authentication APIs  

## 1. Signup  

**POST** `/auth/signup`  

### Request Body  
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "strongpassword123"
}
````

### Response

```json
{
  "id": 1,
  "email": "john@example.com",
  "is_verified": false
}
```

## 2. Verify Email

**POST** `/auth/verify-email`

### Request Body

```json
{
  "email": "john@example.com",
  "code": "123456"
}
```

### Response

```json
{
  "id": 1,
  "email": "john@example.com",
  "is_verified": true
}
```
## 3. Login

**POST** `/auth/login`

### Request Body

```json
{
  "email": "john@example.com",
  "password": "strongpassword123"
}
```

### Response

```json
{
  "access_token": "jwt-token-here",
  "token_type": "bearer"
}
```

## 4. Resend Verification Email

**POST** `/auth/resend-verification-code`

### Request Body

```json
{
  "email": "john@example.com"
}
```

## 5. Logout

**POST** `/auth/logout`

### Headers

```
Authorization: Bearer <jwt-token>
```

## 6. Refresh Token

**POST** `/auth/refresh-token`

### Headers

```
Authorization: Bearer <refresh-token>
```

### Response

```json
{
  "access_token": "new-jwt-token",
  "token_type": "bearer"
}
```

## 7. Forgot Password

**POST** `/auth/send-forgot-password-code`

### Request Body

```json
{
  "email": "john@example.com"
}
```

## 8. Reset Password

**POST** `/auth/reset-password`

### Request Body

```json
{
  "email": "john@example.com",
  "code": "123456",
  "new_password": "newSecurePassword123"
}
```

## 9. Get Current User (Profile)

**GET** `/auth/me`

### Headers

```
Authorization: Bearer <jwt-token>
```

### Response

```json
{
  "id": 1,
  "email": "john@example.com",
  "name": "John Doe",
  "is_verified": true
}
```
---
## Transcript API

### GET `/v1/transcripts?video_id={video_id}&language={language_code}`

Fetch a YouTube transcript (**JWT-protected endpoint**).

**Query Parameters:**

* `video_id` (string, required) – YouTube video ID
* `language` (string, optional) – e.g., `en`, `es`. Defaults to primary transcript language

**Success Response (200):**

```json
{
  "status": "success",
  "code": 200,
  "data": {
    "video_id": "abcd1234",
    "language": "en",
    "language_code": "en",
    "transcript": "Hello world...",
    "transcript_with_timestamps": "1\n00:00:00,000 --> 00:00:02,000\nHello\n..."
  }
}
```

**Error Responses:**

* **403** – Video private or transcript disabled

```json
{
  "status": "error",
  "code": 403,
  "message": "Video is private or transcript disabled",
  "error": "TranscriptsDisabled: Transcript not available"
}
```

* **404** – Video unavailable

```json
{
  "status": "error",
  "code": 404,
  "message": "Video unavailable",
  "error": "VideoUnavailable: Video deleted or private"
}
```

* **422** – Language not supported

```json
{
  "status": "error",
  "code": 422,
  "message": "Language not supported",
  "error": "NoTranscriptFound: Transcript unavailable in requested language"
}
```

* **500** – Internal server error

```json
{
  "status": "error",
  "code": 500,
  "message": "Transcript extraction failed",
  "error": "Internal server error details"
}
```

## Example Workflow

1. **User Registration**

```bash
POST /auth/signup
```

* User receives a verification email

2. **Email Verification**

```bash
POST /auth/verify-email
```

* Submit verification code

3. **Login**

```bash
POST /auth/login
```

* Receive JWT token in response

4. **Fetch Transcript**

```bash
GET /v1/transcripts?video_id=dQw4w9WgXcQ&language=en
Authorization: Bearer <jwt-token>
```

* Protected endpoint, requires valid JWT
* Returns structured JSON with transcript

---

## Environment Variables

| Variable                       | Description                    |
| ------------------------------ | ------------------------------ |
| POSTGRES\_USER                 | PostgreSQL username            |
| POSTGRES\_PASSWORD             | PostgreSQL password            |
| POSTGRES\_DB                   | Database name                  |
| POSTGRES\_HOST                 | DB host                        |
| POSTGRES\_PORT                 | DB port                        |
| JWT\_SECRET                    | Secret key for JWT             |
| JWT\_ALG                       | JWT algorithm (default: HS256) |
| ACCESS\_TOKEN\_EXPIRE\_MINUTES | Token expiry in minutes        |
| SMTP\_USER                     | Email sender username          |
| SMTP\_PASSWORD                 | Email sender password          |
| EMAIL\_FROM                    | Sender display name            |
| APP\_BASE\_URL                 | Base URL of the application    |
| REDIS\_HOST                    | Redis host                     |
| REDIS\_PORT                    | Redis port                     |

---

## License

**ai-job-killer-Server** is released under the **MIT License** © 2025 ai-job-killer.

### Permissions
You are free to:
- Use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the software  
- Use the software for private, academic, or commercial purposes

### Conditions
- Include the original copyright and license notice in all copies or substantial portions of the software

### Disclaimer
The software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose, and non-infringement. In no event shall the authors be liable for any claim, damages, or other liability arising from the use of the software.
