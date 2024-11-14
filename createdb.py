# createdb.py
from core.configs import settings
from core.database import engine
import asyncio

async def create_all_tables() -> None:
    import models.__all_models
     
    async with engine.begin() as conn:
        print('Iniciando a criação de tabelas...')
        await conn.run_sync(settings.DB_BaseModel.metadata.drop_all)
        print('Todas as tabelas foram removidas.')
        await conn.run_sync(settings.DB_BaseModel.metadata.create_all)
        print('Todas as tabelas foram criadas.')

if __name__ == "__main__":
    print('Executando o script de criação de tabelas...')
    asyncio.run(create_all_tables())
    print('Script de criação de tabelas concluído.')