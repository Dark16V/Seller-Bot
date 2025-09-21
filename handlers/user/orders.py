from aiogram.types import CallbackQuery, FSInputFile, InputMediaAnimation
from aiogram.exceptions import TelegramBadRequest
from aiogram import F

from keyboards import IBK
from keyboards.callbackdata import *

from db import async_session

import os

from services import DbManager




class OrdersClient():
    def __init__(self, dp, bot):
        self.dp = dp
        self.bot = bot
        self.menu_id = 'CgACAgIAAxkBAAMFaMKDp4R4ZNpd4G3rbPbvVfMAAbA0AAJvfwACf0UYSpntdLDLaMBZNgQ'
        self.catalogue_id = 'CgACAgIAAxkBAAMLaMKEG9RnqxCELyg5SiWaFZXyWl0AAm5_AAJ_RRhKiu5ZRQOxWgw2BA'
        self.profile_id = 'CgACAgIAAxkBAAMOaMKETaEfPD7btpw6-xltJHM6MQMAAnB_AAJ_RRhKvaDK5arl6C82BA'
        self.db_manager = DbManager(async_session)

    async def reg_handler(self):
        self.dp.callback_query(F.data == 'my_orders')(self.orders_handler)
        self.dp.callback_query(OrdersPage.filter())(self.orders_page_handler)


    async def send_media(self, file_name: str, file_id: str):
        animation = file_id
        try:
            await self.bot.get_file(animation)
            return animation
        except TelegramBadRequest:
            animation = FSInputFile(os.path.join("media", file_name))
            return animation 


    async def format_orders(self, orders, page: int = 1, len_page: int = 1):
        text = f"🧑‍💻 <b>Ваша история заказов:</b> {page}/{len_page}\n\n"
        for order in orders:
            text += (
                f"🆔 <b>ID заказа:</b> <code>{order.track_number}</code>\n"
                f"📂 <b>Категория:</b> <b>{order.category}</b>\n"
                f"🔢 <b>Количество:</b> <b>{order.requested}</b>\n"
                f"📌 <b>Статус:</b> <b>{order.status}</b>\n"
                f"⏰ <b>Время создания:</b> <code>{order.created_at}</code>\n\n"
            )
        return text
    

    async def orders_handler(self, callback: CallbackQuery):
        await callback.answer()

        animation = await self.send_media('profile.gif', self.profile_id)


        orders = await self.db_manager.get_order(user_id=callback.from_user.id)

        if not orders:
            await callback.message.edit_media(media=InputMediaAnimation(media=animation, caption="📭 <i>У вас пока нет заказов…</i>"), reply_markup=await IBK.back_on_profile())
            return

        page = 1
        start = (page - 1) * 1
        end = start + 1
        page_orders = orders[start:end]

        text = await self.format_orders(page_orders, len_page=len(orders))
        await callback.message.edit_media(media=InputMediaAnimation(media=animation, caption=text), 
                                          reply_markup=build_orders_keyboard(page, len(orders)))



        
    async def orders_page_handler(self, callback: CallbackQuery, callback_data: OrdersPage):
        page = callback_data.page
        orders = await self.db_manager.get_order(user_id=callback.from_user.id)
        animation = await self.send_media('profile.gif', self.profile_id)

        start = (page - 1) * 1
        end = start + 1
        page_orders = orders[start:end]

        text = await self.format_orders(page_orders, page=page, len_page=len(orders))
        await callback.message.edit_media(media=InputMediaAnimation(media=animation, caption=text), reply_markup=build_orders_keyboard(page, len(orders)))
        await callback.answer()