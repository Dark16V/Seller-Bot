from aiogram.types import CallbackQuery
from aiogram import F

from keyboards.callbackdata import *

from db import async_session

from services import DbManager


class ServerClient():
    def __init__(self, dp, bot):
        self.dp = dp
        self.bot = bot
        self.menu_id = 'CgACAgIAAxkBAAMFaMKDp4R4ZNpd4G3rbPbvVfMAAbA0AAJvfwACf0UYSpntdLDLaMBZNgQ'
        self.catalogue_id = 'CgACAgIAAxkBAAMLaMKEG9RnqxCELyg5SiWaFZXyWl0AAm5_AAJ_RRhKiu5ZRQOxWgw2BA'
        self.profile_id = 'CgACAgIAAxkBAAMOaMKETaEfPD7btpw6-xltJHM6MQMAAnB_AAJ_RRhKvaDK5arl6C82BA'
        self.db_manager = DbManager(async_session)


    async def reg_handler(self):
        self.dp.callback_query(F.data == 'buy_servers')(self.buy_server)

    async def buy_server(self, call: CallbackQuery):
        await call.answer("На данный момент этот раздел временно не доступен‼️", show_alert=True)