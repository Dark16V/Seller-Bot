from aiogram.types import Message, CallbackQuery, InputMediaAnimation
from aiogram.filters import CommandStart
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram import F

from src.keyboards import IBK
from src.keyboards.callbackdata import *

from db import async_session

from src.services import DbManager

from src.utils.utils import get_media



class StartMenu():
    def __init__(self, config):
        self.dp = config.dp
        self.bot = config.bot
        self.db_manager = DbManager(async_session)


    async def reg_handler(self):
        self.dp.message(CommandStart())(self.send_welcome)
        self.dp.callback_query(F.data == 'back_to_menu')(self.back_to_menu)
        self.dp.callback_query(F.data == 'buy')(self.select_product)
        self.dp.callback_query(F.data == 'help')(self.help)
        self.dp.callback_query(F.data == 'profile')(self.profile_callback)
        self.dp.callback_query(F.data == 'check_sub')(self.check_sub)


    async def send_welcome(self, message: Message, state: FSMContext, new_user = False, user_id = None):
        await state.clear()
        animation = await get_media('menu')
        await message.delete()
        uid = user_id if user_id else message.from_user.id

        if new_user == True:
            msg = await message.answer("""<b>☁️ Добро пожаловать!</b>
                                       
<b>📂У нас представлены популярные ресурсы для безопасности Premium качества, и по самой низкой цене</b>
            
➖➖➖➖➖
            
<b>↪️ Начни прямо сейчас, выбрав интересующий раздел в меню!</b>""")
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

        animation = await get_media('menu')
        await call.message.edit_media(media=InputMediaAnimation(media=animation, caption="<b>☁️ ГЛАВНОЕ МЕНЮ</b>"), reply_markup=await IBK.menu(call.from_user.id))



    async def select_product(self, call: CallbackQuery):
        await call.answer()
        animation = await get_media('catalog')
        await call.message.edit_media(media=InputMediaAnimation(media=animation, caption="<b>⚡️Выберите товар</b>"), reply_markup=await IBK.categories_products())

        

    async def help(self, call: CallbackQuery):
        await call.answer()
        animation = await get_media('profile')
        text = f'Здравствуйте, мой айди аккаунта id{call.from_user.id}. Хочу обратиться по вопросу..'
        await call.message.edit_media(media=InputMediaAnimation(media=animation, 
                                            caption="❓ <b>По всем вопросам:</b>"),
                                            reply_markup=await IBK.help(text=text))
        

    async def profile_callback(self, call: CallbackQuery, user):
        await call.answer(' ')

        animation = await get_media('profile')
        ref_url = f'<code>https://t.me/{(await call.bot.get_me()).username}?start={call.from_user.id}</code>'
        count_ref = await self.db_manager.get_user_count_ref(uid=call.from_user.id)

        await call.message.edit_media(media=InputMediaAnimation(media=animation, 
                                            caption=f"<b>🪐Ваш ID:</b> <code>{user.telegram_id}</code>\n<b>💲Ваш баланс:</b> <code>{user.balance:.2f} $</code>\n<b>👥Количество ваших рефералов: {count_ref}</b>\n<b>🔗Ваша реферальная ссылка\n{ref_url}</b>", 
                                            parse_mode="HTML"),
                                            reply_markup=await IBK.profile_keyboard())
