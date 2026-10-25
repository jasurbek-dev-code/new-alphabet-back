from typing import Any, AsyncGenerator, Dict
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from config import settings

db_url = settings.async_database_url
engine_kwargs: Dict[str, Any] = {"echo": settings.DEBUG}

if db_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # PostgreSQL / Supabase sozlamalari
    engine_kwargs["pool_pre_ping"] = True
    engine_kwargs["pool_recycle"] = 300

    # PgBouncer (Transaction mode) da asyncpg prepared statementlar bilan ishlashi uchun
    if "pgbouncer=true" in db_url.lower() or ":6543" in db_url:
        engine_kwargs["connect_args"] = {
            "statement_cache_size": 0,
            "prepared_statement_cache_size": 0,
        }
        # asyncpg query parameterlarida 'pgbouncer' parametrini tozalash (asyncpg tanimaydi)
        parsed = urlparse(db_url)
        query_params = parse_qs(parsed.query)
        query_params.pop("pgbouncer", None)
        new_query = urlencode(query_params, doseq=True)
        db_url = urlunparse(parsed._replace(query=new_query))

engine = create_async_engine(db_url, **engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    # Ensure all models are imported so Base.metadata knows about them
    import models  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
