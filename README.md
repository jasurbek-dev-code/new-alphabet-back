# Uzbek Latin Transliteration Backend API (Telegram Mini App)

FastAPI asosida yaratilgan Telegram Mini App backend qismi. Bu xizmat eski o'zbek lotin alifbosidagi matnlarni (`Sh`, `Ch`, `O'`, `G'`) isloh qilingan yangi alifboga (`Ş`, `Ç`, `Ō`, `Ğ`) transliteratsiya qiladi, Telegram foydalanuvchilarini autentifikatsiya qiladi va ularning tarjimalar tarixini saqlaydi.

---

## 📁 Loyiha strukturasi

```text
back/
├── .env                  # Muhit o'zgaruvchilari (Git'ga yuklanmaydi)
├── .gitignore            # Git e'tiborsiz qoldiradigan fayllar
├── render.yaml           # Render.com deploy konfiguratsiyasi
├── config.py             # Pydantic Settings konfiguratsiyasi
├── database.py           # SQLAlchemy async engine, session factory & Base
├── models.py             # Ma'lumotlar bazasi modellari (User, TranslationHistory)
├── schemas.py            # Pydantic validation schemalari
├── main.py               # FastAPI dasturi, CORS va lifespan hodisalari
├── requirements.txt      # Python kutubxonalari
├── routers/
│   ├── __init__.py
│   ├── auth.py           # /api/v1/auth/sync va /api/v1/auth/me endpointlari
│   └── translations.py   # /api/v1/translate va /api/v1/history endpointlari
├── services/
│   ├── __init__.py
│   ├── telegram_auth.py  # Telegram initData HMAC-SHA256 tekshiruvi
│   ├── telegram_helper.py# Test uchun Telegram initData yaratuvchi yordamchi
│   ├── translation_service.py # Transliteratsiya va tarix saqlash xizmati
│   ├── transliteration.py# Alifbo konvertatsiya mantiqi
│   └── user_service.py   # Foydalanuvchi qidirish va yangilash
└── test_auth.py          # Telegram autentifikatsiya testlari
```

---

## 🚀 Ishga tushirish

### 1. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 2. Muhit o'zgaruvchilarini sozlash
`back/.env` faylini yarating va quyidagi parametrlarni to'ldiring:
```env
TELEGRAM_BOT_TOKEN=your_bot_token_from_botfather
DATABASE_URL=sqlite+aiosqlite:///./app.db
# PostgreSQL uchun (masalan production muhitida):
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/uzbek_translit_db
APP_ENV=development
DEBUG=True
ALLOWED_ORIGINS=*
INIT_DATA_MAX_AGE_SECONDS=86400
```

### 3. Serverni ishga tushirish
Mahalliy kompyuterda:
```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Cloud serverlarda (Render, VPS):
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Interaktiv API hujjatlari:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health check: `http://localhost:8000/health`

---

## 📡 Asosiy API Endpointlar

### 1. `POST /api/v1/auth/sync`
Telegram WebApp ochilganda `initData` orqali foydalanuvchini tekshirish va bazaga sinxronlash.

### 2. `GET /api/v1/auth/me`
Joriy foydalanuvchi ma'lumotlarini olish. Header: `Authorization: <initData>` yoki `X-Telegram-Init-Data: <initData>`.

### 3. `POST /api/v1/translate`
Matnni yangi alifboga transliteratsiya qilish va avtomatik ravishda tarixga yozish.
```json
{
  "text": "O'zbekiston shaxmat chempioni bo'ldi"
}
```

### 4. `GET /api/v1/history`
Foydalanuvchining avvalgi tarjimalari ro'yxatini pagination bilan olish.
- Parametrlar: `page` (default: 1), `per_page` (default: 20).

---

## 🧪 Testlarni ishga tushirish

```bash
pytest
```
