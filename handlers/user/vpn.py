from aiogram.types import CallbackQuery, FSInputFile, InputMediaAnimation
from aiogram.exceptions import TelegramBadRequest
from aiogram import F

from keyboards import IBK
from keyboards.callbackdata import *

from db import get_db, async_session
from models.order import Order

from utils.loguru import logger

import os
import uuid

from services import DbManager




class VPNClient():
    def __init__(self, dp, bot):
        self.dp = dp
        self.bot = bot
        self.menu_id = 'CgACAgIAAxkBAAMFaMKDp4R4ZNpd4G3rbPbvVfMAAbA0AAJvfwACf0UYSpntdLDLaMBZNgQ'
        self.catalogue_id = 'CgACAgIAAxkBAAMLaMKEG9RnqxCELyg5SiWaFZXyWl0AAm5_AAJ_RRhKiu5ZRQOxWgw2BA'
        self.profile_id = 'CgACAgIAAxkBAAMOaMKETaEfPD7btpw6-xltJHM6MQMAAnB_AAJ_RRhKvaDK5arl6C82BA'
        self.db_manager = DbManager(async_session)


    async def reg_handler(self):
        self.dp.callback_query(F.data == 'buy_vpn')(self.watch_vpn)
        self.dp.callback_query(F.data == 'continue_vpn')(self.choose_amount_vpn)
        self.dp.callback_query(CallbackDataVPNAmount.filter(F.action == 'amount_vpn'))(self.choose_amount_vpn_callback)
        self.dp.callback_query(CallbackDataVPN.filter(F.action == 'pay_vpn_order'))(self.pay_vpn_order)


    async def send_media(self, file_name: str, file_id: str):
        animation = file_id
        try:
            await self.bot.get_file(animation)
            return animation
        except TelegramBadRequest:
            animation = FSInputFile(os.path.join("media", file_name))
            return animation 


    async def watch_vpn(self, call: CallbackQuery):
        await call.answer()
        
        animation = await self.send_media('catalogue.gif', self.catalogue_id)
        await call.message.edit_media(
            media=InputMediaAnimation(
                media=animation,
                caption=(
                    "🌐 <b>VPN — ваш надёжный доступ в свободный интернет</b>\n\n"
                    "🔒 Наш VPN обеспечивает:\n"
                    "• Полную анонимность и защиту данных\n"
                    "• Доступ к любым сайтам и сервисам без блокировок\n"
                    "• Высокую скорость соединения без ограничений\n"
                    "• Простая установка и настройка\n\n"
                    "💳 <b>Как проходит покупка:</b>\n"
                    "1️⃣ Оплачиваете чек на количество ключей (VPN), которое хотите.\n"
                    "2️⃣ Пересылаете этот чек нашему саппорту.\n"
                    "3️⃣ Получаете персональный VPN-ключ.\n"
                    "4️⃣ Используете его по инструкции в разделе «Инструкции по использованию 💡».\n\n"
                    "🚀 Всё просто: платите → получаете ключ → подключаетесь!"
                )
            ),
            reply_markup=await IBK.continue_vpn()
        )


    async def choose_amount_vpn(self, call: CallbackQuery):
        await call.answer()

        animation = await self.send_media('catalogue.gif', self.catalogue_id)
        await call.message.edit_media(media=InputMediaAnimation(media=animation, 
                                            caption="🎲 <i>Выбери количество VPN:</i>"), 
                                            reply_markup=await IBK.choose_amount_vpn())
        




    async def choose_amount_vpn_callback(self, call: CallbackQuery, callback_data: CallbackDataVPNAmount):
        await call.answer()
        amount = callback_data.amount

        animation = await self.send_media('catalogue.gif', self.catalogue_id)
        await call.message.edit_media(media=InputMediaAnimation(media=animation, 
                                            caption=f"➖➖➖📝 <b>Ваш заказ:</b>➖➖➖\n\n🛡 <b>Товар:</b> <b>VPN</b>\n⚡️ <b>Количество:</b> <code>{amount}</code>\n💲 <b>К оплате:</b> <code>{amount * 2}$</code>"), 
                                            reply_markup=await IBK.pay_vpn_order(amount=amount))
        

        
    async def pay_vpn_order(self, call: CallbackQuery, callback_data: CallbackDataVPN):
        await call.answer()

        track_number = str(uuid.uuid4())[:8]

        logger.info(f"[{track_number}] Начало обработки заказа (user={call.from_user.id}, category=VPN)")

        amount = callback_data.amount

        order = Order(
                    track_number=track_number,
                    user_id=call.from_user.id,
                    category='VPN',
                    requested=amount,
                    status="in_progress"
                )
        
        async for sess in get_db():
            try:
                user = await self.db_manager.get_user(id=call.from_user.id)
                if user.balance < amount * 2:
                    animation = await self.send_media('catalogue.gif', self.catalogue_id)
                    await call.message.edit_media(media=InputMediaAnimation(media=animation, caption="У вас не достаточно средств ❌"), reply_markup=await IBK.back_on_main_page())
                    return
                
                await self.db_manager.update_user(id=call.from_user.id, balance=(amount * 2) * -1)
                
                logger.info(f"[{track_number}] Списание {amount * 2} с баланса пользователя {user.telegram_id}")
                await call.message.delete()
                await call.message.answer("✅ <b>Вы успешно оплатили товар!</b>")
                text = (
                    "➖➖➖🧾 Чек➖➖➖\n\n"
                    f"🆔 Трек-номер заказа: {track_number}\n"
                    f"👤 Ваш ID: {call.from_user.id}\n"
                    f"📂 Категория: VPN\n"
                    f"⚡️ Количество: {amount}"
                )

                await call.message.answer(text)
                await call.message.answer(
                    "<b>Спасибо за покупку! Чтобы получить товар нажмите на кнопку ниже ⬇️</b>",
                    reply_markup=await IBK.succes_pay_url(text)
                )

                

                order.status = 'succes'
                sess.add(order)
                await sess.commit()
                logger.info(f"[{track_number}]заказ успешено проведен {user.telegram_id}")

            except Exception as e:
                error_msg = str(e)

                logger.error(f"[{track_number}] Ошибка при обработке заказа: {error_msg}")
                order.status = 'error'

                sess.add(order)
                await sess.commit()

                await call.message.answer(
                    f'❌ Ошибка при обработке заказа.\n'
                    f'🆔 Трек-номер: `{track_number}`\nОбратитесь в поддержку ‼️',
                    parse_mode="Markdown"
                )