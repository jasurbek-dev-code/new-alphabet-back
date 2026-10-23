# Uzbek Latin Transliteration Backend API (Telegram Mini App)

A production-ready FastAPI backend for a Telegram Mini App that transliterates Uzbek text from the old Latin alphabet to the newly reformed alphabet (e.g. `Sh` $\to$ `Ş`, `Ch` $\to$ `Ç`, `O'` $\to$ `Ō`, `G'` $\to$ `Ğ`) and tracks user translation history.

---

## 📁 Project Structure

```
back/
├── .env                  # Environment variables (ignored in Git)
├── .env.example          # Template for environment configuration
├── config.py             # Pydantic Settings management
├── database.py           # SQLAlchemy async engine, session factory & Base
├── models.py             # User SQLAlchemy ORM model
├── schemas.py            # Pydantic schemas (TelegramUserData, AuthRequest, UserResponse)
├── main.py               # FastAPI application setup, CORS & lifespan events
├── requirements.txt      # Python dependencies
├── routers/
│   ├── __init__.py
│   └── auth.py           # /api/v1/auth/sync and /api/v1/auth/me endpoints
├── services/
│   ├── __init__.py
│   ├── telegram_auth.py  # HMAC-SHA256 validation for Telegram WebApp initData
│   ├── telegram_helper.py# Helper for generating signed initData (testing/mocking)
│   └── user_service.py   # User query & upsert logic
└── test_auth.py          # Unit tests for authentication
```

---

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and fill in your Telegram Bot Token:
```env
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxYZ
DATABASE_URL=sqlite+aiosqlite:///./app.db
# Or PostgreSQL for production:
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/uzbek_translit_db
```

### 3. Run the Server
```bash
uvicorn main:app --reload --port 8000
```

Interactive API documentation will be available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 🔒 Telegram WebApp Authentication (`initData` Verification)

The authentication uses Telegram's official cryptographic verification algorithm:
1. Parse query string and extract `hash`.
2. Sort remaining key-value pairs alphabetically and join with `\n` to build `data_check_string`.
3. Compute `secret_key = HMAC-SHA256("WebAppData", bot_token)`.
4. Compute `HMAC-SHA256(secret_key, data_check_string)`.
5. Compare with `hash` using constant-time comparison (`hmac.compare_digest`).
6. Validate `auth_date` against expiration timestamp.
7. Parse user data and synchronize with the database.

---

## 📡 API Endpoints

### `POST /api/v1/auth/sync`
Synchronizes the Telegram user with the database upon launching the Mini App.

**Request Body:**
```json
{
  "init_data": "query_id=...&user=%7B%22id%22%3A12345%2C...%7D&auth_date=...&hash=..."
}
```

**Response (`200 OK`):**
```json
{
  "user": {
    "telegram_id": 12345,
    "first_name": "Alisher",
    "last_name": "Navoiy",
    "username": "navoiy",
    "language_code": "uz",
    "created_at": "2026-10-22T13:00:00Z",
    "updated_at": "2026-10-22T13:00:00Z"
  },
  "is_new_user": true,
  "auth_date": "2026-10-22T13:00:00Z"
}
```

### `GET /api/v1/auth/me`
Fetches the current user profile using `Authorization: Bearer <initData>` header.
