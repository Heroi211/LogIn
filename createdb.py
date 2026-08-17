# createdb.py
import asyncio
import logging

from core.database import engine

logger = logging.getLogger(__name__)


async def create_all_tables() -> None:
    import models.__all_models
    from core.generic import modelsGeneric

    async with engine.begin() as conn:
        logger.info("Iniciando a criação de tabelas...")
        await conn.run_sync(modelsGeneric.metadata.drop_all)
        logger.warning("Todas as tabelas foram removidas.")
        await conn.run_sync(modelsGeneric.metadata.create_all)
        logger.info("Todas as tabelas foram criadas.")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
    logger.info("Executando o script de criação de tabelas...")
    asyncio.run(create_all_tables())
    logger.info("Script de criação de tabelas concluído.")