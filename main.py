import asyncio
from config import bot, dp
from utils.loguru import setup_logger, logger
from db import engine, Base
from handlers import reg_handlers


async def main():
    setup_logger(level='INFO')
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    await reg_handlers(dp)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

    
    
if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("Bot stopped!")
        