from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaAnimation
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram import F

from keyboards import IBK
from keyboards.callbackdata import *

from db import async_session

import os

from services import DbManager



class StartMenu():
    def __init__(self, dp, bot):
        self.dp = dp
        self.bot = bot
        self.menu_id = 'CgACAgIAAxkBAAIH6GjRo2k_oLP65EprZiB1pdDQOJaaAAJvfwACf0UYStj_a-he8dkwNgQ'
        self.catalogue_id = 'CgACAgIAAxkBAAIH6mjRo4ma7X3Y24IjssLWagpGTWWoAAJufwACf0UYStlfz2QPcZf4NgQ'
        self.profile_id = 'CgACAgIAAxkBAAIH5WjRoqbrAejuu_HCvqVNUIU8buRHAAJwfwACf0UYSl2nBRkiLySpNgQ'
        self.db_manager = DbManager(async_session)


    async def send_media(self, file_name: str, file_id: str):
        animation = file_id
        try:
            await self.bot.get_file(animation)
            return animation
        except TelegramBadRequest:
            animation = FSInputFile(os.path.join("media", file_name))
            return animation

    async def reg_handler(self):
        self.dp.message(CommandStart())(self.send_welcome)
        self.dp.callback_query(F.data == 'back_to_menu')(self.back_to_menu)
        self.dp.callback_query(F.data == 'buy')(self.select_product)
        self.dp.callback_query(F.data == 'help')(self.help)
        self.dp.callback_query(F.data == 'profile')(self.profile_callback)
        self.dp.callback_query(F.data == 'check_sub')(self.check_sub)


    async def send_welcome(self, message: Message, new_user = False, user_id = None):
        animation = await self.send_media('menu.gif', self.menu_id)
        await message.delete()
        uid = user_id if user_id else message.from_user.id

        if new_user == True:
            msg = await message.answer("<b>☁️ Добро пожаловать в ProxyCloud!</b>\n\n"
                            "<b>🛩️ У нас представлены популярные ресурсы для безопасности Premium качества, и по самой низкой цене</b>\n\n"
                            "<b>ℹ️ Наши резервные ссылки:</b>\n"
                            "<b>— codehousegroup.t.me</b>\n"
                            "<b>— codehousech.com</b>\n"
                            "<b>— proxycloudch.t.me</b>\n\n"
                            " ➖➖➖➖➖\n\n"
                            "<b>↪️ Начни прямо сейчас, выбрав интересующий раздел в меню!</b>")
            try:
                await self.bot.unpin_chat_message(chat_id=message.chat.id)
            except TelegramBadRequest:
                pass

            await self.bot.pin_chat_message(chat_id=uid, message_id=msg.message_id)
        await message.answer_animation(animation=animation, caption="☁️ <b>ГЛАВНОЕ МЕНЮ</b>", reply_markup=await IBK.menu(user_id=uid))


    async def check_sub(self, call: CallbackQuery):
        await call.answer()
        message = call.message
        uid = call.from_user.id
        await self.send_welcome(message=message, new_user=True, user_id=uid)
        


    async def back_to_menu(self, call: CallbackQuery, state: FSMContext):
        await call.answer(' ')
        await state.clear()

        animation = await self.send_media('menu.gif', self.menu_id)
        await call.message.edit_media(media=InputMediaAnimation(media=animation, caption="<b>☁️ ГЛАВНОЕ МЕНЮ</b>"), reply_markup=await IBK.menu(call.from_user.id))



    async def select_product(self, call: CallbackQuery):
        await call.answer()
        animation = await self.send_media('catalogue.gif', self.catalogue_id)
        await call.message.edit_media(media=InputMediaAnimation(media=animation, caption="<b>⚡️Выберите товар</b>"), reply_markup=await IBK.categories_products())

        

    async def help(self, call: CallbackQuery):
        await call.answer()
        animation = await self.send_media('profile.gif', self.profile_id)
        text = f'Здравствуйте, мой айди аккаунта id{call.from_user.id}. Хочу обратиться по вопросу..'
        await call.message.edit_media(media=InputMediaAnimation(media=animation, 
                                            caption="❓ <b>По всем вопросам:</b>"),
                                            reply_markup=await IBK.help(text=text))
        

    async def profile_callback(self, call: CallbackQuery, user):
        await call.answer(' ')

        animation = await self.send_media('profile.gif', self.profile_id)

        await call.message.edit_media(media=InputMediaAnimation(media=animation, 
                                            caption=f"*🪐Ваш ID:* `{user.telegram_id}`\n*💲Ваш баланс:* `{user.balance:.2f} $`", 
                                            parse_mode="Markdown"),
                                            reply_markup=await IBK.profile_keyboard())