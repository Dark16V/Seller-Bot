import asyncio
from time import time
from collections import defaultdict
from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.exceptions import TelegramRetryAfter

from loguru import logger


class QueueWithUserThrottlingMiddleware(BaseMiddleware):
    def __init__(self, workers: int = 3, base_rate: int = 30, user_delay: float = 0.5):
        super().__init__()
        self.queue = asyncio.Queue()
        self.workers = workers

        self.base_delay = 1 / base_rate
        self.current_delay = self.base_delay

        self.user_delay = user_delay
        self.user_last_call: Dict[int, float] = defaultdict(lambda: 0)

        self.lock = asyncio.Lock()

        for _ in range(workers):
            asyncio.create_task(self.worker())

        asyncio.create_task(self.cleanup_task())


    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        user_id = getattr(event.from_user, "id", None)
        now = time()

        if user_id:
            async with self.lock:
                last_call = self.user_last_call[user_id]
                if now - last_call < self.user_delay:
                    try:
                        await event.answer("⏳ Подождите немного, вы слишком часто нажимаете команды!")
                    except Exception as e:
                        logger.warning(f"Не удалось отправить сообщение антифлуда: {e}")
                    return
                self.user_last_call[user_id] = now

        await self.queue.put((handler, event, data))


    async def worker(self):
        while True:
            handler, event, data = await self.queue.get()
            try:
                await handler(event, data)

                if self.current_delay > self.base_delay:
                    self.current_delay = max(self.base_delay, self.current_delay * 0.9)

            except TelegramRetryAfter as e:
                self.current_delay = max(self.current_delay, e.retry_after + 0.5)
                logger.warning(f"⚠️ FloodWait {e.retry_after}s")
                await asyncio.sleep(e.retry_after)

            finally:
                self.queue.task_done()
                await asyncio.sleep(self.current_delay)


    async def cleanup_task(self):
        while True:
            await asyncio.sleep(3600)
            now = time()
            async with self.lock:
                before = len(self.user_last_call)
                self.user_last_call = {
                    uid: ts for uid, ts in self.user_last_call.items() if now - ts < 3600
                }
                after = len(self.user_last_call)
            logger.info(f"Очистка словаря")
