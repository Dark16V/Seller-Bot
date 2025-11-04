from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
import os
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from src.middlewares.message import CheckUserMiddleware
from src.middlewares.callback import CheckUserCallbackMiddleware
from src.middlewares.rate_limit import ThrottlingMiddleware
from db import async_session
from constants import ipv4, ipv6, ipv4_cheep, proxy_info


load_dotenv()


class Config:
    def __init__(self):
        self.bot = Bot(token=os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        self.dp = Dispatcher()
        self.dp.message.middleware(CheckUserMiddleware(async_session))
        self.dp.callback_query.middleware(ThrottlingMiddleware(limit=0.5))
        self.dp.callback_query.middleware(CheckUserCallbackMiddleware(async_session))
        self.ipv4 = ipv4
        self.ipv6 = ipv6
        self.ipv4_cheep = ipv4_cheep
        self.proxy_info = proxy_info






config = Config()