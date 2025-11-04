from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable
from sqlalchemy import select

from src.models.user import User 

from src.keyboards import IBK


class CheckUserMiddleware(BaseMiddleware):
    def __init__(self, session_maker):
        super().__init__()
        self.session_maker = session_maker 

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ):
        telegram_id = event.from_user.id
        referral_uid = None

        if event.text and event.text.startswith("/"):
            parts = event.text.split(maxsplit=1)
            args = parts[1] if len(parts) > 1 else None
            
            if args:
                if args.isdigit():
                    if int(args) != telegram_id:
                        referral_uid = int(args)

                        try:
                            await event.bot.send_message(chat_id=referral_uid, text="<b>У вас новый реферал!</b>")
                        except: pass
        
        async with self.session_maker() as session:
            result = await session.execute(
                select(User).where(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if not user:
                new_user = User(telegram_id=telegram_id, referral_uid=referral_uid)
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)
                data['user'] = new_user
                data['new_user'] = True
                return await handler(event, data)
            
            if user.is_baned:
                return

        data['user'] = user

        return await handler(event, data)
