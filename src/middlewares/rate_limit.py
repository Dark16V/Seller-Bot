import time
from collections import defaultdict
from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery

class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, limit: float = 2.0):
        super().__init__()
        self.limit = limit
        self._last_time = defaultdict(lambda: 0.0) 

    async def __call__(self, handler, event: CallbackQuery, data: dict):
        user_id = event.from_user.id
        now = time.monotonic()
        last = self._last_time[user_id]

        if now - last < self.limit:
            await event.answer(f"Анти-спам. Подожди‼️", show_alert=True)
            return

        self._last_time[user_id] = now

        return await handler(event, data)
