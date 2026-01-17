import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from ruentrainerbot.core.config import settings
from ruentrainerbot.core.logging import configure_logging, get_logger
from ruentrainerbot.db.queries import create_tables
from ruentrainerbot.db.session import engine
from ruentrainerbot.middlewares.log_context import LogContextMiddleware
from ruentrainerbot.handlers import routers

logger = get_logger(__name__)


async def main():
    configure_logging(
        debug=settings.debug,
        log_level=getattr(settings, 'log_level', 'INFO')
    )
    logger.info('Бот запущен', debug=settings.debug)
    if settings.debug:
        await create_tables(engine)
        logger.info('tables_created')

    bot = Bot(token=settings.token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.update.middleware(LogContextMiddleware())

    for r in routers:
        dp.include_router(r)

    try:
        await dp.start_polling(bot)
    except Exception:
        logger.exception('polling_failed')
        raise
    finally:
        await bot.session.close()
        logger.info('bot_stopped')


if __name__ == '__main__':
    asyncio.run(main())
