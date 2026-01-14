import asyncio
from aiogram import Bot, Dispatcher
from ruentrainerbot.core.config import settings
from ruentrainerbot.core.logging import configure_logging, get_logger
from ruentrainerbot.db.queries import create_tables
from ruentrainerbot.db.session import engine
from ruentrainerbot.middlewares.log_context import LogContextMiddleware

async def main():
    configure_logging(debug=settings.debug,
                      log_level=getattr(settings, 'log_level', 'INFO')
                      )
    bot = Bot(token=settings.token)
    dp = Dispatcher()
    dp.update.middleware(LogContextMiddleware)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

    if settings.debug:
        await create_tables(engine)

if __name__ == '__main__':
    print('Сервер запущен')
    asyncio.run(main())
