# SmartFlow
SmartFlow is a lightweight asynchronous web application for managing feedback and comments with positive/negative notation tracking. It supports JWT-based authentication and provides RESTful endpoints for creating, updating, and retrieving feedback notations.

## Stack
- Python 3.12
- Tornado
- Tortoise (ORM)
- aiosqlite (DB): sqlite that allows async operations
- JWT-based authentication

## Features
- Create, update, and get methods for feedback and comments
- Positive/negative notations for feedback and comments
- Summary of notations for feedback and comments
- User registration and login
- Server-side validation for input data
- JWT-secured endpoints for authentication


## Limitations
The app is currently using SQLite as its database, which is not suitable for production use. This means that if the container stops or is removed, all data will be lost(unless you use a volume).  
Bcause this is a small MVP app I have decided that SQLite is sufficient for now. However, as this app grows I would definitely switch to a more robust database like PostgreSQL with async support(Asyncpg).

## Installation

### Pull Docker
You can pull the Docker image from Docker Hub:
```bash
docker pull endellos/smartflow:latest
```

### Run the Docker container
```bash
docker run -p 8888:8888 endellos/smartflow:latest
```

## Deployed version
You can access the deployed version of SmartFlow at [https://smartflow-uwxq.onrender.com/](https://smartflow-uwxq.onrender.com/).  
It is a free tier, so it may take some time to start up. Please be patient.

## Usage
There is a `test.http` file in the root directory that contains example requests for testing the endpoints.

# SmartFlow API Endpoints

---

## 1. Health Check
- **Endpoint:** `/`  
- **Method:** `GET`  
- **Authentication:** No  
- **Description:** Returns a simple health check message to verify that the server is running.
- **Request Body:** None

**Example Request:**
```bash
curl -X GET http://localhost:8888/
```

**Example Response:**
```json
{
  "message": "App is running"
}
```

## 2. Register a User
- **Endpoint:** `/api/register`  
- **Method:** `POST`  
- **Authentication:** No  
- **Description:** Registers a new user with a username and password.  

**Request Body:**
```json
{
  "username": "user3",
  "password": "password2"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8888/api/register   -H "Content-Type: application/json"   -d '{
    "username": "user3",
    "password": "password2"
  }'
```

**Expected Response (200 OK):**
```json
{
  "message": "User registered",
  "id": 1
}
```

**Error Responses:**
```json
{
  "error": "Username required"
}
```
```json
{
  "error": "Username already exists"
}
```

## 3. Login
- **Endpoint:** `/api/login`  
- **Method:** `POST`  
- **Authentication:** No  
- **Description:** Logs in an existing user and returns a JWT token.  

**Request Body:**
```json
{
  "username": "user3",
  "password": "password2"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8888/api/login   -H "Content-Type: application/json"   -d '{
    "username": "user3",
    "password": "password2"
  }'
```

**Expected Response (200 OK):**
```json
{
  "token": "<JWT_TOKEN>"
}
```

> Use this token in the `Authorization: Bearer <JWT_TOKEN>` header for all authenticated endpoints.

## 4. Create Feedback
- **Endpoint:** `/api/feedback`  
- **Method:** `POST`  
- **Authentication:** Yes (JWT)  
- **Description:** Creates a new feedback entry with a note and rating.  

**Request Body:**
```json
{
  "note": "This is my feedback",
  "rating": 4
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8888/api/feedback   -H "Content-Type: application/json"   -H "Authorization: Bearer <JWT_TOKEN>"   -d '{
    "note": "This is my feedback",
    "rating": 4
  }'
```

**Expected Response (200 OK):**
```json
{
  "id": 1,
  "note": "This is my feedback",
  "message": "Feedback created"
}
```

**Error Response:**
```json
{
  "error": "Rating must be an integer between 1 and 5"
}
```

## 5. Get Feedback
- **Endpoint:**  
  - `/api/feedback` → all feedbacks  
  - `/api/feedback/{feedback_id}` → single feedback  

- **Method:** `GET`  
- **Authentication:** No  
- **Description:** Retrieves all feedback or a single feedback by ID.  

**Example Request (All Feedbacks):**
```bash
curl -X GET http://localhost:8888/api/feedback 
```

**Example Request (Single Feedback):**
```bash
curl -X GET http://localhost:8888/api/feedback/1 
```

**Expected Response (All Feedbacks):**
```json
{
  "feedbacks": [
    {
      "id": 1,
      "user_id": 2,
      "username": "user3",
      "note": "This is my feedback",
      "rating": 4
    }
  ]
}
```

**Single feedback (404 if not found):**
```json
{
  "error": "Feedback not found"
}
```

## 6. Post Comment
- **Endpoint:** `/api/comment`  
- **Method:** `POST`  
- **Authentication:** Yes (JWT)  
- **Description:** Creates a comment for a feedback.  

**Request Body:**
```json
{
  "feedback_id": 1,
  "content": "This is a comment"
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8888/api/comment   -H "Content-Type: application/json"   -H "Authorization: Bearer <JWT_TOKEN>"   -d '{
    "feedback_id": 1,
    "content": "This is a comment"
  }'
```

**Expected Response (200 OK):**
```json
{
  "id": 5,
  "text": "This is a comment",
  "message": "Comment created"
}
```

**Error Responses:**
```json
{
  "error": "Comment content is required"
}
```
```json
{
  "error": "Feedback not found"
}
```

## 7. Get Comments
- **Endpoint:**  
  - `/api/comment/{comment_id}` → single comment  
  - `/api/feedback/{feedback_id}/comments` → all comments for a feedback  

- **Method:** `GET`  
- **Authentication:** No  
- **Description:** Retrieves comments for a feedback or a single comment by ID.  

**Example Request (All Comments for Feedback 1):**
```bash
curl -X GET http://localhost:8888/api/feedback/1/comments
```

**Example Request (Single Comment 1):**
```bash
curl -X GET http://localhost:8888/api/comment/1
```

**Expected Response:**
```json
{
  "comments": [
    {
      "id": 5,
      "user_id": 2,
      "username": "user3",
      "feedback_id": 1,
      "content": "This is a comment"
    }
  ]
}
```

**404 if not found:**
```json
{
  "error": "No comments found"
}
```

## 8. Feedback Notations

### Create a Notation
- **Endpoint:** `/api/feedback/{feedback_id}/notations`  
- **Method:** `POST`  
- **Authentication:** Yes (JWT)  
- **Description:** Adds a new positive or negative notation to a feedback.  

**Request Body:**
```json
{
  "value": 1
}
```

**Example Request:**
```bash
curl -X POST http://localhost:8888/api/feedback/1/notations   -H "Content-Type: application/json"   -H "Authorization: Bearer <JWT_TOKEN>"   -d '{
    "value": 1
  }'
```

### Update a Notation
- **Endpoint:** `/api/feedback/{feedback_id}/notations`  
- **Method:** `PATCH`  
- **Authentication:** Yes (JWT)  
- **Description:** Updates an existing notation for a feedback.  

**Request Body:**
```json
{
  "value": -1
}
```

### Get Summary
- **Endpoint:** `/api/feedback/{feedback_id}/notations/summary`  
- **Method:** `GET`  
- **Authentication:** Yes (JWT)  (The reason this api need authentication is that it returns the user's notation)
- **Description:** Retrieves the total positive, negative, and current user’s notation value for a feedback.  

**Example Request:**
```bash
curl -X GET http://localhost:8888/api/feedback/1/notations/summary   -H "Authorization: Bearer <JWT_TOKEN>"
```

**Expected Response:**
```json
{
  "positive": 3,
  "negative": 1,
  "user_value": 1
}
```

## 9. Comment Notations

### Create a Notation
- **Endpoint:** `/api/comment/{comment_id}/notations`  
- **Method:** `POST`  
- **Authentication:** Yes (JWT)  (The reason this api need authentication is that it returns the user's notation)
- **Description:** Adds a positive or negative notation to a comment.  

**Request Body:**
```json
{
  "value": 1
}
```

### Update a Notation
- **Endpoint:** `/api/comment/{comment_id}/notations`  
- **Method:** `PATCH`  
- **Authentication:** Yes (JWT)  
- **Description:** Updates an existing notation for a comment.  

**Request Body:**
```json
{
  "value": 0
}
```

### Get Summary
- **Endpoint:** `/api/comment/{comment_id}/notations/summary`  
- **Method:** `GET`  
- **Authentication:** Yes (JWT)  
- **Description:** Retrieves the total positive, negative, and current user’s notation value for a comment.  

**Example Request:**
```bash
curl -X GET http://localhost:8888/api/comment/1/notations/summary   -H "Authorization: Bearer <JWT_TOKEN>"
```

**Expected Response:**
```json
{
  "positive": 2,
  "negative": 0,
  "user_value": 0
}
```

## Author

- **Margarita Stoyanova** – [GitHub](https://github.com/Endellos) | [Docker Hub](https://hub.docker.com/r/endellos)
