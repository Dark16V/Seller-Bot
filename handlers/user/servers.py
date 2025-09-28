from aiogram.types import CallbackQuery
from aiogram import F

from keyboards.callbackdata import *

from db import async_session

from services import DbManager


class ServerClient():
    def __init__(self, dp, bot):
        self.dp = dp
        self.bot = bot
        self.menu_id = 'CgACAgIAAxkBAAIH6GjRo2k_oLP65EprZiB1pdDQOJaaAAJvfwACf0UYStj_a-he8dkwNgQ'
        self.catalogue_id = 'CgACAgIAAxkBAAIH6mjRo4ma7X3Y24IjssLWagpGTWWoAAJufwACf0UYStlfz2QPcZf4NgQ'
        self.profile_id = 'CgACAgIAAxkBAAIH5WjRoqbrAejuu_HCvqVNUIU8buRHAAJwfwACf0UYSl2nBRkiLySpNgQ'
        self.db_manager = DbManager(async_session)


    async def reg_handler(self):
        self.dp.callback_query(F.data == 'buy_servers')(self.buy_server)

    async def buy_server(self, call: CallbackQuery):
        await call.answer("На данный момент этот раздел временно не доступен‼️", show_alert=True)