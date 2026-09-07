# AI Farming Agent Backend Learning Guide

This guide explains what we have built so far, how the pieces work together,
and what to study next. The project currently covers FastAPI, PostgreSQL,
async SQLAlchemy, Alembic migrations, password hashing, JWT authentication,
and protected endpoints.

## 1. Progress so far

### Phase 3: Backend structure

The backend was divided by responsibility:

```text
backend/
|-- api/         HTTP routes and authentication dependencies
|-- core/        Configuration and security utilities
|-- database/    SQLAlchemy base, engine, and sessions
|-- models/      SQLAlchemy database table definitions
|-- schemas/     Pydantic request and response validation
|-- services/    Reusable application and CRUD logic
|-- alembic/     Database migration scripts
|-- main.py      FastAPI application entry point
`-- .env         Local secrets and connection settings (not committed)
```

Keeping these responsibilities separate makes the project easier to test,
change, and understand.

### Phase 4: First FastAPI endpoints

We created:

```text
GET  /      -> Hello AI Farmer
POST /chat  -> {"message": "Hello Farmer"}
```

`main.py` creates the FastAPI application. A route decorator connects an HTTP
method and path to a Python function:

```python
@app.get("/")
def root():
    return "Hello AI Farmer"
```

Uvicorn is the development ASGI server:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

In `main:app`, `main` means `main.py` and `app` means the FastAPI object inside
that file. `--reload` restarts the development server after code changes.

### Phase 5: PostgreSQL and CRUD

We added three database resources:

```text
users
chat_history
forecast_history
```

Each resource supports CRUD:

```text
Create -> POST
Read   -> GET
Update -> PUT
Delete -> DELETE
```

PostgreSQL runs through Docker Compose. `asyncpg` is the asynchronous
PostgreSQL driver, while SQLAlchemy provides the Python ORM and query API.

The database URL uses this format:

```text
postgresql+asyncpg://username:password@host:port/database
```

It is stored in `backend/.env`, not directly in source code.

### Phase 6: Authentication

We implemented this flow:

```text
Register
   |
   v
Hash password with Argon2
   |
   v
Store user and password hash in PostgreSQL
   |
   v
Login with email and password
   |
   v
Return a signed JWT access token
   |
   v
Send token in Authorization header
   |
   v
Access protected endpoint
```

The authentication endpoints are:

```text
POST /auth/register
POST /auth/login
GET  /auth/me
GET  /auth/protected
```

## 2. How the backend layers work together

For a request such as `POST /auth/register`, the flow is:

```text
Swagger, curl, or frontend
        |
        v
api/auth.py route
        |
        v
schemas/user.py validates input
        |
        v
core/security.py hashes the password
        |
        v
models/user.py represents the database row
        |
        v
database/session.py commits through SQLAlchemy
        |
        v
PostgreSQL stores the new user
        |
        v
UserRead schema creates a safe response
```

The response schema deliberately excludes `hashed_password`.

## 3. SQLAlchemy concepts to learn

### Model

A SQLAlchemy model is a Python class mapped to a database table:

```python
class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True)
```

The class is used in Python; `users` is the table used by PostgreSQL.

### Engine

The engine knows how to connect to PostgreSQL:

```python
engine = create_async_engine(settings.database_url)
```

Creating the engine does not create application tables. Alembic manages the
table structure.

### Session

A session represents one unit of database work:

```python
db.add(user)
await db.commit()
await db.refresh(user)
```

- `add()` starts tracking a new object.
- `commit()` permanently saves the transaction.
- `refresh()` reloads database-generated fields such as IDs and timestamps.
- `rollback()` cancels a failed transaction.

One session is provided per API request by the `get_db()` dependency.

### Query

SQLAlchemy builds SQL using Python expressions:

```python
statement = select(User).where(User.email == email)
user = await db.scalar(statement)
```

Concepts to practice:

- `select()`
- `where()`
- `order_by()`
- `join()`
- `commit()` and `rollback()`
- primary keys, unique constraints, indexes, and foreign keys

## 4. Alembic: the important mental model

Alembic is database version control. Git versions source files; Alembic
versions the database structure.

The normal workflow is:

```text
1. Change a SQLAlchemy model
2. Generate a migration
3. Inspect the generated migration
4. Apply the migration
5. Commit the model and migration together
```

### Generate a migration

Run from `backend/`:

```powershell
.\.venv\Scripts\python.exe -m alembic revision --autogenerate -m "describe the change"
```

`--autogenerate` compares SQLAlchemy metadata with the current database.
Alembic then writes a new file under `alembic/versions/`.

Always inspect that file. Autogeneration is assistance, not a replacement for
review.

### Apply migrations

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

`head` means the newest migration.

### Check the current revision

```powershell
.\.venv\Scripts\python.exe -m alembic current
```

### View migration history

```powershell
.\.venv\Scripts\python.exe -m alembic history
```

### Roll back one migration

```powershell
.\.venv\Scripts\python.exe -m alembic downgrade -1
```

Only downgrade after checking whether it would delete columns or data.

### What went wrong during our first migrations

An early migration contained only:

```python
def upgrade():
    pass
```

This happened because the model metadata did not contain the intended model
changes when the migration was generated. Applying that migration changed the
recorded revision but created no columns. We corrected it by updating the
`User` model, generating another migration, inspecting its `op.add_column()`
operations, and applying it.

Lesson: update the model first, use `--autogenerate`, inspect the migration,
and only then run `upgrade head`.

## 5. Authentication concepts to learn

### Registration

Registration accepts a name, email, and password. Pydantic validates the
request before the route runs. The password must be at least eight characters.

The password is passed to Argon2:

```python
hashed_password = hash_password(password)
```

Only the generated hash is stored. Plaintext passwords must never be stored or
logged.

### Password hashing is not encryption

Encryption is reversible with a key. Password hashing is intentionally
one-way. Login verifies a candidate password against the stored hash:

```python
verify_password(received_password, stored_hash)
```

The project uses `pwdlib` with its recommended Argon2 configuration.

### Login

`POST /auth/login` receives form data:

```text
username = the user's email
password = the user's password
```

The field is called `username` because Swagger uses the standard OAuth2
password form. Our application interprets it as an email address.

Login performs these checks:

```text
1. Find the user by normalized email
2. Verify the password hash
3. Confirm the account is active
4. Create and return an access token
```

The API intentionally returns the same general error for an unknown email and
an incorrect password. This reveals less information to an attacker.

### JWT access token

The JWT currently contains claims similar to:

```json
{
  "sub": "3",
  "type": "access",
  "exp": "expiration time"
}
```

- `sub` identifies the user.
- `type` identifies the kind of token.
- `exp` limits how long the token is valid.

A JWT is signed, not encrypted. Anyone holding it may inspect its claims, so
never include a password, database secret, or sensitive personal data.

The signing secret lives in `.env`:

```env
JWT_SECRET_KEY=a-long-random-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Never commit the real secret.

### Bearer authentication

The client sends the JWT on later requests:

```http
Authorization: Bearer <access-token>
```

The `get_current_user()` dependency:

```text
1. Reads the bearer token
2. Verifies its signature and expiration
3. Reads the user ID from `sub`
4. Loads the user from PostgreSQL
5. Rejects missing or inactive users
6. Returns the authenticated User object
```

Routes become protected by depending on it:

```python
@router.get("/protected")
async def protected_endpoint(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return {"message": f"Welcome, {current_user.name}"}
```

Without a valid token, FastAPI returns `401 Unauthorized`.

## 6. Authentication testing workflow

Start PostgreSQL from the repository root:

```powershell
docker compose up -d postgres
```

Apply migrations from `backend/`:

```powershell
.\.venv\Scripts\python.exe -m alembic upgrade head
```

Start FastAPI:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Open Swagger:

```text
http://127.0.0.1:8000/docs
```

Test in this order:

1. `POST /auth/register`
2. `POST /auth/login`
3. Click Swagger's **Authorize** button
4. `GET /auth/me`
5. `GET /auth/protected`
6. Log out in Swagger and confirm the protected request returns `401`

Example registration body:

```json
{
  "name": "Test Farmer",
  "email": "farmer@example.com",
  "password": "Use-A-Test-Password-123"
}
```

Do not reuse real passwords in screenshots, examples, or development data.

## 7. Common HTTP status codes

```text
200 OK                    Successful read, update, or login
201 Created               Registration or resource creation succeeded
204 No Content            Deletion succeeded
401 Unauthorized          Missing, invalid, or expired authentication
403 Forbidden             Identity known but action not allowed
404 Not Found             Resource does not exist
409 Conflict              Email already registered
422 Unprocessable Content Request validation failed
500 Internal Server Error Unhandled application or database failure
```

Swagger always documents a possible `422` response for validated endpoints.
It is only an actual error when `422` appears under **Server response** after
executing a request.

## 8. Useful development terminals

### Terminal 1: PostgreSQL and migrations

```powershell
cd D:\Projects_New\ai-farming-agent
docker compose up -d postgres
cd backend
.\.venv\Scripts\python.exe -m alembic upgrade head
```

### Terminal 2: FastAPI server

```powershell
cd D:\Projects_New\ai-farming-agent\backend
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

### Terminal 3: tests and Git

```powershell
cd D:\Projects_New\ai-farming-agent
git status
```

The server terminal remains occupied because Uvicorn is a long-running
process. Use a separate terminal for requests, tests, migrations, and Git.

## 9. Git workflow

Keep `main` stable and develop one feature on a short-lived branch:

```powershell
git switch main
git pull origin main
git switch -c feature/example-feature
```

After implementing and testing:

```powershell
git add .
git commit -m "Describe the completed feature"
git push -u origin feature/example-feature
```

Create a pull request from the feature branch into `main`, review it, merge it,
and then update local `main`.

For the current authentication work:

```text
feature/authentication -> main
```

## 10. Security limitations and future improvements

The current implementation is a strong learning foundation, but production
authentication normally adds:

- HTTPS everywhere
- refresh tokens and token rotation
- logout or token revocation
- password-reset and email-verification flows
- login rate limiting and account lockout protection
- authorization roles and permissions
- secure HTTP-only cookies when appropriate
- secret management outside local `.env` files
- audit logs and security monitoring
- automated authentication and authorization tests

Authentication answers **who the user is**. Authorization answers **what that
user may do**. They are related but different responsibilities.

## 11. Recommended learning exercises

Complete these in order:

1. Register a second user and inspect the database row.
2. Confirm the stored password is an Argon2 hash, not plaintext.
3. Login with a wrong password and observe `401`.
4. Call a protected endpoint without a token and observe `401`.
5. Call it with a valid token and observe `200`.
6. Set `is_active` to false and confirm login or protected access is rejected.
7. Reduce token lifetime temporarily and observe expiration.
8. Protect chat history so users can only access their own records.
9. Add automated tests for registration, login, duplicate email, bad password,
   expired token, and protected access.
10. Add role-based authorization after understanding ownership checks.

## 12. Official references

- FastAPI security: https://fastapi.tiangolo.com/tutorial/security/
- FastAPI OAuth2 and JWT: https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
- SQLAlchemy asyncio: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
- Alembic tutorial: https://alembic.sqlalchemy.org/en/latest/tutorial.html
- pwdlib: https://frankie567.github.io/pwdlib/
- PyJWT: https://pyjwt.readthedocs.io/

## 13. The core lesson

The most important architecture to remember is:

```text
HTTP request
  -> FastAPI route
  -> Pydantic validation
  -> authentication dependency
  -> service/database operation
  -> SQLAlchemy session
  -> PostgreSQL
  -> safe Pydantic response
```

For database changes, remember:

```text
Change model -> generate migration -> inspect -> apply -> test -> commit
```

For authentication, remember:

```text
Register -> hash password -> login -> verify password -> issue JWT
-> send Bearer token -> verify JWT -> load current user -> authorize action
```
