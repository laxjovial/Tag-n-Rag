# JWT Authentication Guide

## 1. What is JWT?
JSON Web Token (JWT) is an open standard (RFC 7519) that defines a compact and self-contained way for securely transmitting information between parties as a JSON object. In our application, we use JWTs to handle user authentication.

When a user logs in with their username and password, the backend verifies their credentials and, if successful, returns a JWT. This token is then sent with every subsequent request to protected API endpoints to prove that the user is authenticated.

## 2. How It's Used in Our Application
1.  **Login:** A user sends their credentials to the `/auth/login` endpoint.
2.  **Token Creation:** The server validates the credentials, and if they are correct, it creates a JWT. This token contains a "payload" with information about the user (specifically, their username) and an expiration time.
3.  **Signing:** The token is then "signed" using a secret key known only to the server. This signature ensures that the token cannot be tampered with by a client or an attacker.
4.  **Token Storage:** The signed token is sent back to the user's browser, where it is stored in the Streamlit session state.
5.  **Authenticated Requests:** For any request to a protected endpoint (e.g., uploading a document), the frontend sends the JWT in the `Authorization` header.
6.  **Token Verification:** The backend receives the token, verifies its signature using the secret key, and checks that it has not expired. If the token is valid, the request is processed. If not, a 401 Unauthorized error is returned.

## 3. Configuration
The JWT system is configured using environment variables, which should be set in your `.env` file.

```
# --- JWT Authentication ---
# Generate a strong secret key using: openssl rand -hex 32
SECRET_KEY="a_very_secret_key_that_should_be_in_env"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

*   **`SECRET_KEY`**: This is the most critical piece. It is the secret key used to sign and verify tokens. It must be kept private. A new, strong key should be generated for any production deployment. You can generate one using the `openssl` command provided in the comments.
*   **`ALGORITHM`**: This is the hashing algorithm used to sign the token. `HS256` is a common and secure choice.
*   **`ACCESS_TOKEN_EXPIRE_MINUTES`**: This defines how long a token is valid after it has been issued. A shorter expiration time is generally more secure. After this time, the user will need to log in again.
