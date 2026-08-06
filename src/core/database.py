from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.configs import settings

engine: AsyncEngine | None = None
Session: sessionmaker | None = None

if not settings.is_development:
    engine = create_async_engine(settings.DATABASE_URL)
    Session = sessionmaker(
        autocommit=False,
        autoflush=False,
        expire_on_commit=False,
        class_=AsyncSession,
        bind=engine,
    )
