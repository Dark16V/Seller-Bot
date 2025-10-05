from aiogram import BaseMiddleware
from aiogram.types import Message
from aiogram.filters import CommandObject
from typing import Callable, Dict, Any, Awaitable
from sqlalchemy import select

from models.user import User 

from keyboards import IBK


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
            print(args)
            
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

        member = await event.bot.get_chat_member(chat_id='@ProxyCloudCH', user_id=telegram_id)
        if not member.status in ("member", "administrator", "creator"):
            await event.bot.send_message(chat_id=telegram_id, text='<b>ℹ️ Для использования бота подпишитесь на наш информационный канал ⬇️</b>', reply_markup=await IBK.sub())
            return

        return await handler(event, data)
