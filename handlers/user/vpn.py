from aiogram.types import CallbackQuery, FSInputFile, InputMediaAnimation
from aiogram.exceptions import TelegramBadRequest
from aiogram import F

from keyboards import IBK
from keyboards.callbackdata import *

from db import get_db, async_session
from models.order import Order

from utils.loguru import logger
from utils.utils import get_media

import os
import uuid

from services import DbManager




class VPNClient():
    def __init__(self, config):
        self.dp = config.dp
        self.bot = config.bot
        self.db_manager = DbManager(async_session)


    async def reg_handler(self):
        self.dp.callback_query(F.data == 'buy_vpn')(self.watch_vpn)
        self.dp.callback_query(F.data == 'continue_vpn')(self.choose_amount_vpn)
        self.dp.callback_query(CallbackDataVPNAmount.filter(F.action == 'amount_vpn'))(self.choose_amount_vpn_callback)
        self.dp.callback_query(CallbackDataVPN.filter(F.action == 'pay_vpn_order'))(self.pay_vpn_order)


    async def watch_vpn(self, call: CallbackQuery):
        await call.answer()
        
        animation = await get_media('catalog')
        text_markdown = """🛸 *VPN это ваша безопасность — а значит наша забота.*

ℹ️ *Мы предоставляем:*
```
➖ используем самые защищенные технологии [V2Ray + VLESS]
➖ самая быстрые каналы связи [200-500 Мбит/с]
➖ выделено максимум трафика для каждого юзера [150 Gb/неделя]
➖ анонимность [не собираем данные об активности, не пишем логи]
➖ удобное подключение с любого устройства [Android, iOS, Windows, Mac]
➖ расширенное гео с быстрым подключением [🇺🇸, 🇳🇱, 🇸🇬, 🇩🇪, 🇭🇰, 🇫🇷, 🇬🇧, 🇰🇿, 🇺🇦, 🇵🇱]
```

💲 *Как происходит покупка?*
```
➖ Оплачиваете счет на сумму эквивалентной количества VPN ключей
➖ Пересылаете счет администрации по нажатию на кнопку
➖ Получаете ваш уникальный VPN-ключ, и используете его по инструкции из раздела
```"""

        await call.message.edit_media(
            media=InputMediaAnimation(
                media=animation,
                caption=text_markdown, parse_mode="Markdown"
            ),
            reply_markup=await IBK.continue_vpn()
        )


    async def choose_amount_vpn(self, call: CallbackQuery):
        await call.answer()

        animation = await get_media('catalog')
        await call.message.edit_media(media=InputMediaAnimation(media=animation, 
                                            caption="🎲 <i>Выбери количество VPN:</i>"), 
                                            reply_markup=await IBK.choose_amount_vpn())
        




    async def choose_amount_vpn_callback(self, call: CallbackQuery, callback_data: CallbackDataVPNAmount):
        await call.answer()
        amount = callback_data.amount

        animation = await get_media('catalog')
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
                    animation = await get_media('catalog')
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