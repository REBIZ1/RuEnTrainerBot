import structlog
from typing import Any, Awaitable, Callable, Dict, Optional
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update


class LogContextMiddleware(BaseMiddleware):
    """
    Автоматически добавляет
    контекст текущего Telegram апдейта в логи structlog
    """
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        ctx: Dict[str, Any] = {}
        update = data.get('update')
        from_user = data.get('event_from_user')
        chat = data.get('event_chat')
        if update is not None:
            ctx['update_id'] = update.update_id
        if from_user is not None:
            ctx['user_id'] = from_user.id
        if chat is not None:
            ctx['chat_id'] = chat.id

        structlog.contextvars.bind_contextvars(**ctx)
        try:
            return await handler(event, data)
        finally:
            structlog.contextvars.clear_contextvars()
