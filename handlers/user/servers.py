from aiogram.types import CallbackQuery
from aiogram import F

from keyboards.callbackdata import *

from db import async_session

from services import DbManager


class ServerClient():
    def __init__(self, config):
        self.dp = config.dp
        self.bot = config.bot
        self.db_manager = DbManager(async_session)


    async def reg_handler(self):
        self.dp.callback_query(F.data == 'buy_servers')(self.buy_server)

    async def buy_server(self, call: CallbackQuery):
        await call.answer("На данный момент этот раздел временно не доступен‼️", show_alert=True)