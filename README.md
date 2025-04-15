# FoodLoop Backend API Documentation

This document outlines the API endpoints for the FoodLoop backend, built with Flask. The API supports user authentication, surplus food management, and request handling for a platform connecting food providers (Farmers, Retailers) and NGOs.

**Base URL**: `http://localhost:5000/api` (adjust based on deployment)

**Authentication**: Some endpoints require a JWT token, obtained via the `/api/login` endpoint, to be included in the `Authorization` header as `Bearer <token>`.

---

## Table of Contents
1. [Authentication Routes](#authentication-routes)
   - [Sign Up](#sign-up)
   - [Login](#login)
   - [Auth Status](#auth-status)
   - [Logout](#logout)
2. [Surplus Food Routes](#surplus-food-routes)
   - [Add Surplus Food](#add-surplus-food)
   - [Get User's Surplus Food](#get-users-surplus-food)
   - [Get All Surplus Food (NGOs Only)](#get-all-surplus-food-ngos-only)
3. [Request Routes](#request-routes)
   - [Send Request for Surplus Food](#send-request-for-surplus-food)
   - [Get Requests](#get-requests)

---

## Authentication Routes

### Sign Up
**Create a new user account.**

- **Method**: POST
- **URL**: `/api/signup`
- **Authentication**: None
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string",
    "role": "string" // One of: "Farmer", "Retailer", "NGO"
  }
  ```
- **Responses**:
  - **201 Created**:
    ```json
    {
      "message": "User created successfully"
    }
    ```
  - **400 Bad Request**:
    ```json
    {
      "error": "Username, email, and password are required"
    }
    ```
  - **409 Conflict**:
    ```json
    {
      "error": "Username already exists, please choose another"
    }
    ```
    or
    ```json
    {
      "error": "Email address is already registered, you might want to log in instead"
    }
    ```

### Login
**Authenticate a user and obtain a JWT token.**

- **Method**: POST
- **URL**: `/api/login`
- **Authentication**: None
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "email": "string",
    "password": "string",
    "remember": boolean // Optional, defaults to false
  }
  ```
- **Responses**:
  - **200 OK**:
    ```json
    {
      "message": "Login successful",
      "token": "string" // JWT token
    }
    ```
  - **400 Bad Request**:
    ```json
    {
      "error": "Email and password are required"
    }
    ```
  - **401 Unauthorized**:
    ```json
    {
      "error": "Invalid email or password"
    }
    ```

### Auth Status
**Check if the user is authenticated and retrieve user details.**

- **Method**: GET
- **URL**: `/api/auth/status`
- **Authentication**: None (returns authenticated status)
- **Responses**:
  - **200 OK (Authenticated)**:
    ```json
    {
      "authenticated": true,
      "user": {
        "username": "string",
        "email": "string",
        "role": "string"
      }
    }
    ```
  - **200 OK (Not Authenticated)**:
    ```json
    {
      "authenticated": false
    }
    ```

### Logout
**Log out the current user.**

- **Method**: POST
- **URL**: `/api/logout`
- **Authentication**: None (session-based, clears session)
- **Responses**:
  - **200 OK**:
    ```json
    {
      "message": "Logged out successfully"
    }
    ```

---

## Surplus Food Routes

### Add Surplus Food
**Add a new surplus food item (for Farmers/Retailers).**

- **Method**: POST
- **URL**: `/api/surplus`
- **Authentication**: Required (JWT token)
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "foodName": "string",
    "quantity": "string",
    "expirationDate": "string", // Format: YYYY-MM-DD
    "location": "string"
  }
  ```
- **Responses**:
  - **201 Created**:
    ```json
    {
      "added": true,
      "id": integer // ID of the created food item
    }
    ```
  - **400 Bad Request**:
    ```json
    {
      "error": "data is empty"
    }
    ```
    or
    ```json
    {
      "error": "Missing required fields"
    }
    ```
  - **401 Unauthorized**:
    ```json
    {
      "error": "Authentication required"
    }
    ```

### Get User's Surplus Food
**Retrieve surplus food items added by the authenticated user.**

- **Method**: GET
- **URL**: `/api/surplus`
- **Authentication**: Required (JWT token)
- **Responses**:
  - **200 OK**:
    ```json
    [
      {
        "id": integer,
        "name": "string",
        "quantity": "string",
        "expiry": "string",
        "location": "string",
        "status": "string" // e.g., "available"
      },
      ...
    ]
    ```
  - **404 Not Found**:
    ```json
    {
      "error": "food items not available"
    }
    ```
  - **401 Unauthorized**:
    ```json
    {
      "error": "Authentication required"
    }
    ```

### Get All Surplus Food (NGOs Only)
**Retrieve all available surplus food items (for NGOs).**

- **Method**: GET
- **URL**: `/api/all-surplus`
- **Authentication**: Required (JWT token)
- **Query Parameters**:
  - `term` (optional): Filter by food name (partial match).
  - `location` (optional): Filter by location (partial match).
  - Example: `/api/all-surplus?term=apple&location=New%20York`
- **Responses**:
  - **200 OK**:
    ```json
    [
      {
        "id": integer,
        "name": "string",
        "quantity": "string",
        "expiry": "string",
        "location": "string",
        "status": "string",
        "provider": "string" // Username of the provider
      },
      ...
    ]
    ```
  - **200 OK (No Results)**:
    ```json
    []
    ```
  - **403 Forbidden**:
    ```json
    {
      "error": "Unauthorized access"
    }
    ```
  - **401 Unauthorized**:
    ```json
    {
      "error": "Authentication required"
    }
    ```

---

## Request Routes

### Send Request for Surplus Food
**Send a request for a specific surplus food item (for NGOs).**

- **Method**: POST
- **URL**: `/api/surplus/<id>/request`
  - `<id>`: Integer ID of the surplus food item.
- **Authentication**: Required (JWT token)
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "quantity": "string",
    "notes": "string", // Optional
    "pickup_date": "string" // Optional, format: YYYY-MM-DD
  }
  ```
- **Responses**:
  - **201 Created**:
    ```json
    {
      "status": "Request added successfully"
    }
    ```
  - **400 Bad Request**:
    ```json
    {
      "error": "No data received"
    }
    ```
    or
    ```json
    {
      "error": "Quantity is required"
    }
    ```
    or
    ```json
    {
      "error": "NGO ID is required"
    }
    ```
  - **404 Not Found**:
    ```json
    {
      "error": "Food item not found"
    }
    ```
  - **401 Unauthorized**:
    ```json
    {
      "error": "Authentication required"
    }
    ```

### Get Requests
**Retrieve requests made to or by the authenticated user.**

- **Method**: GET
- **URL**: `/api/requests`
- **Authentication**: Required (JWT token)
- **Query Parameters**:
  - `type` (optional): Either `made` (for NGOs) or `received` (for Farmers/Retailers). Defaults to `received`.
  - Example: `/api/requests?type=made`
- **Responses**:
  - **200 OK**:
    ```json
    [
      {
        "id": integer,
        "food_name": "string",
        "quantity": "string",
        "notes": "string",
        "pickup_date": "string",
        "response_date": "string",
        "request_date": "string",
        "provider_id": integer,
        "provider_name": "string",
        "requester_id": integer,
        "requester_name": "string",
        "status": "string"
      },
      ...
    ]
    ```
  - **400 Bad Request**:
    ```json
    {
      "error": "Invalid request type for user role"
    }
    ```
  - **401 Unauthorized**:
    ```json
    {
      "error": "Authentication required"
    }
    ```

---

## Notes for Frontend Team
- **JWT Token**: After a successful login, store the `token` from the `/api/login` response and include it in the `Authorization` header for protected routes (e.g., `Bearer <token>`).
- **Error Handling**: Always check for `error` fields in responses to handle failures gracefully (e.g., display user-friendly messages for 400, 401, 403, or 404 errors).
- **Role-Based Access**:
  - Only NGOs can access `/api/all-surplus`.
  - Only NGOs can send requests via `/api/surplus/<id>/request`.
  - Farmers/Retailers can add surplus food and view received requests.
- **Date Formats**: Use `YYYY-MM-DD` for fields like `expirationDate` and `pickup_date`.
- **CORS**: The API supports cross-origin requests (`origins=["*"]`), so no additional CORS configuration is needed on the frontend.

---

## Example Workflow
1. **User Registration**:
   - Frontend sends a POST request to `/api/signup` with `username`, `email`, `password`, and `role`.
   - On success (201), redirect to the login page.
2. **User Login**:
   - Frontend sends a POST request to `/api/login` with `email` and `password`.
   - On success (200), store the `token` and use it for subsequent requests.
3. **Check Authentication**:
   - On page load, call `/api/auth/status` to verify if the user is logged in and display user-specific UI (e.g., Farmer vs. NGO dashboard).
4. **Add Surplus Food** (Farmer/Retailer):
   - Send a POST request to `/api/surplus` with food details.
   - Display the new item in the user's food list.
5. **View Surplus Food**:
   - Farmers/Retailers: Call `/api/surplus` to list their own items.
   - NGOs: Call `/api/all-surplus` to browse all available items.
6. **Request Food** (NGO):
   - Send a POST request to `/api/surplus/<id>/request` to request a specific food item.
7. **View Requests**:
   - NGOs: Call `/api/requests?type=made` to see their requests.
   - Farmers/Retailers: Call `/api/requests?type=received` to see requests for their food.

---
