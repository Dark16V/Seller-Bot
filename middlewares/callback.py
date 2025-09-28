from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery
from sqlalchemy import select
from models.user import User  

from keyboards import IBK


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
        # member = await event.bot.get_chat_member(chat_id='@ProxyCloudCH', user_id=telegram_id)
        # if not member.status in ("member", "administrator", "creator"):
        #     await event.answer()
        #     await event.bot.send_message(chat_id=telegram_id, text='<b>ℹ️ Для использования бота подпишитесь на наш информационный канал ⬇️</b>', reply_markup=await IBK.sub())
        #     return

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
