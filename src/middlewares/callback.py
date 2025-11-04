from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery
from sqlalchemy import select
from src.models.user import User  

from src.keyboards import IBK


class CheckUserCallbackMiddleware(BaseMiddleware):
    def __init__(self, session_maker):
        super().__init__()
        self.session_maker = session_maker

    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any],
    ):
        telegram_id = event.from_user.id


        async with self.session_maker() as session:
                user = (await session.execute(select(User).where(User.telegram_id == telegram_id))).scalar_one_or_none()

                if not user:
                    new_user = User(telegram_id=telegram_id)
                    session.add(new_user)
                    await session.commit()
                    await session.refresh(new_user)

                    data['user'] = user
                    return await handler(event, data)
                
                if user.is_baned:
                    return
        
        data['user'] = user
        return await handler(event, data)
