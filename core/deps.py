from sqlalchemy.ext.asyncio import AsyncSession
from core.database import session


async def get_session():
    session : AsyncSession = session()
    try:
        yield session
    finally:
        await session.close()