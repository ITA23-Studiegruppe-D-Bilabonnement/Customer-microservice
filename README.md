# User Management Service

This Flask-based microservice provides functionality for managing users, including registration, login, and deletion.

## Endpoints

- **Register a new user**

    - **URL**: `/register`
    - **Method**: `POST`
    - **Description**: Creates a new user account.
    - **Request Body**:

        ```json
        {
            "email": "johndoe@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "securepassword123"
        }
        ```

    - **Response**:
        - `200 OK`: User successfully created.
        - `400 Bad Request`: Missing required fields.
        - `409 Conflict`: Email already in use.

- **Login a user**

    - **URL**: `/login`
    - **Method**: `POST`
    - **Description**: Authenticates a user and returns a JWT token.
    - **Request Body**:

        ```json
        {
            "email": "johndoe@example.com",
            "password": "securepassword123"
        }
        ```

    - **Response**:
        - `200 OK`: Login successful, returns a JWT token.
        - `400 Bad Request`: Missing email or password.
        - `401 Unauthorized`: Incorrect email or password.

- **Delete a user**

    - **URL**: `/delete/<id>`
    - **Method**: `DELETE`
    - **Description**: Deletes a specific user by ID.
    - **Response**:
        - `200 OK`: User deleted successfully.
        - `400 Bad Request`: User not found.
        - `500 Internal Server Error`: Unexpected error.

## Environment Variables
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JWT_SECRET_KEY` | Yes | - | Secret key for JWT token generation |
| `PORT` | No | 5000 | Port to run the service on |
| `SQLITE_DB_PATH` | Yes | - | Path to SQLite database file |

## Database

The service uses SQLite for persistent user storage. The database schema is as follows:

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    password TEXT NOT NULL
);