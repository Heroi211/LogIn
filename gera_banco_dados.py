from core.configs import settings
from core.database import engine

async def create_all_tables() -> None:
    from models import __all_models
    print('certo, my friend')
    
    async with engine.begin() as connection:
        await connection.run_sync(settings.DB_BaseModel.metadata.drop_all)
        print('Ja deletei my friend, esquece...')
        await connection.run_sync(settings.DB_BaseModel.metadata.create_all)
    print ('tabelas criadas my friend')
    
if __name__=='__main__':
    import asyncio
    asyncio.run(create_all_tables())