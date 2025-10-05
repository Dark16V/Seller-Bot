import asyncio
from config import config
from utils.loguru import setup_logger, logger
from db import engine, Base, backup_task
from handlers import reg_handlers


async def main():
    setup_logger(level='INFO')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    asyncio.create_task(backup_task(config.bot))

    await reg_handlers(config=config)

    await config.bot.delete_webhook(drop_pending_updates=True)
    await config.dp.start_polling(config.bot)

    
    
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("Bot stopped!")
        