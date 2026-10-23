# Uzbek Latin Transliteration Backend API (Telegram Mini App)

A production-ready FastAPI backend for a Telegram Mini App that transliterates Uzbek text from the old Latin alphabet to the newly reformed alphabet (e.g. `Sh` $\to$ `Ş`, `Ch` $\to$ `Ç`, `O'` $\to$ `Ō`, `G'` $\to$ `Ğ`) and tracks user translation history.

---

## 📁 Project Structure

```
back/
├── .env                  # Environment variables (ignored in Git)
├── .env.example          # Template for environment configuration
├── .gitignore            # Git ignore configuration
├── render.yaml           # Render.com Blueprint configuration
├── config.py             # Pydantic Settings management
├── database.py           # SQLAlchemy async engine, session factory & Base
├── models.py             # SQLAlchemy models (User, TranslationHistory)
├── schemas.py            # Pydantic schemas (Auth, User, Transliteration, History)
├── main.py               # FastAPI application setup, CORS & lifespan events
├── requirements.txt      # Python dependencies
├── routers/
│   ├── __init__.py
│   ├── auth.py           # /api/v1/auth/sync and /api/v1/auth/me endpoints
│   └── translations.py   # /api/v1/translate and /api/v1/history endpoints
├── services/
│   ├── __init__.py
│   ├── telegram_auth.py  # HMAC-SHA256 validation for Telegram WebApp initData
│   ├── telegram_helper.py# Helper for generating signed initData (testing/mocking)
│   ├── translation_service.py # Translation & history persistence service
│   ├── transliteration.py# Uzbek Latin to reformed alphabet converter
│   └── user_service.py   # User query & upsert logic
├── test_auth.py          # Unit tests for Telegram authentication
└── test_step2.py         # Integration tests for database & translation
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
Locally:
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

On Render (or cloud production servers):
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Interactive API documentation will be available at:
- Root: `http://localhost:8000/`
- Health check: `http://localhost:8000/health`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## ☁️ Deploying to Render

1. Create a new **Web Service** on [Render.com](https://render.com).
2. Connect your Git repository (root directory `back` if in a monorepo).
3. Set the following settings:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add the following **Environment Variables**:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from @BotFather
   - `DATABASE_URL`: Your PostgreSQL connection string (Render internal or external DB URL)
   - `APP_ENV`: `production`
   - `DEBUG`: `False`
   - `ALLOWED_ORIGINS`: `*` (or your frontend domains)
5. Alternatively, deploy automatically using the included `render.yaml` Blueprint.

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
Fetches the current user profile using the `Authorization: <initData>` header.

**Headers:**
```http
Authorization: query_id=...&user=...&auth_date=...&hash=...
```
*(Also supports `Authorization: Bearer <initData>`)*

**Response (`200 OK`):**
```json
{
  "telegram_id": 12345,
  "first_name": "Alisher",
  "last_name": "Navoiy",
  "username": "navoiy",
  "language_code": "uz",
  "created_at": "2026-10-22T13:00:00Z",
  "updated_at": "2026-10-22T13:00:00Z"
}
```

---

### `POST /api/v1/translate`
Transliterates text from traditional Uzbek Latin into the reformed alphabet (`Sh` $\to$ `Ş`, `Ch` $\to$ `Ç`, `O'` $\to$ `Ō`, `G'` $\to$ `Ğ`) and automatically persists the translation to history.

**Headers:**
```http
Authorization: <initData>
Content-Type: application/json
```

**Request Body:**
```json
{
  "text": "O'zbekiston shaxmat bo'yicha jahon chempioni bo'ldi."
}
```

**Response (`200 OK`):**
```json
{
  "id": 1,
  "original_text": "O'zbekiston shaxmat bo'yicha jahon chempioni bo'ldi.",
  "translated_text": "Ōzbekiston şaxmat bōyicha jahon çempioni bōldi.",
  "created_at": "2026-10-23T12:00:00Z"
}
```

---

### `GET /api/v1/history`
Retrieves a paginated list of previous translations for the authenticated user, sorted newest first.

**Headers:**
```http
Authorization: <initData>
```

**Query Parameters:**
- `page` (integer, default: `1`, min: `1`)
- `per_page` (integer, default: `20`, min: `1`, max: `100`)

**Response (`200 OK`):**
```json
{
  "total": 45,
  "page": 1,
  "per_page": 20,
  "items": [
    {
      "id": 1,
      "user_id": 12345,
      "original_text": "O'zbekiston shaxmat bo'yicha...",
      "translated_text": "Ōzbekiston şaxmat bōyicha...",
      "created_at": "2026-10-23T12:00:00Z"
    }
  ]
}
```

---

### `GET /health`
Health check endpoint for Render and uptime monitoring.

**Response (`200 OK`):**
```json
{
  "status": "healthy",
  "app": "Uzbek Reform Transliteration API",
  "environment": "production"
}
```

---

## 🧪 Testing

Run automated tests:
```bash
# Unit tests
pytest

# Integration tests
python test_step2.py
```
