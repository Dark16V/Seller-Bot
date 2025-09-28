from aiogram.types import CallbackQuery, FSInputFile, Message, InputMediaAnimation
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram import F

from aiocryptopay import AioCryptoPay, Networks

from keyboards import IBK
from keyboards.callbackdata import *

from utils.state.state import PaymentState
from services import DbManager

from dotenv import load_dotenv

from db import async_session


import os
import asyncio
from typing import Union
from datetime import datetime, timedelta


load_dotenv()

class Payment:
    def __init__(self, dp, bot):
        self.dp = dp
        self.bot = bot
        self.db_manger = DbManager(async_session)
        self.crypto = AioCryptoPay(token=os.getenv('CRYPTO_TOKEN'), network=Networks.MAIN_NET)
        self.deposit_id = 'CgACAgIAAxkBAAIH7GjRo64029Jo4K1qJoTEqPsysskGAAJsfwACf0UYSjaww4363VsiNgQ'
        self.menu_id = 'CgACAgIAAxkBAAIH6GjRo2k_oLP65EprZiB1pdDQOJaaAAJvfwACf0UYStj_a-he8dkwNgQ'


    async def reg_handler(self):
        self.dp.callback_query(F.data == 'inc_balance')(self.inc_balance_callback)
        self.dp.callback_query(F.data == 'my_num')(self.choose_num)
        self.dp.callback_query(F.data == 'disable_pay')(self.disable_pay)
        self.dp.message(StateFilter(PaymentState.AMOUNT), F.text)(self.choose_payment_m)
        self.dp.callback_query(CallbackDataAmount.filter(F.action == 'amount'))(self.choose_payment_c)
        self.dp.callback_query(F.data.startswith("cryptobot_"), StateFilter(PaymentState.WALLET))(self.cryptobot_payment)
        self.dp.callback_query(CallbackDataCurrency.filter(F.action == 'get_currency'), StateFilter(PaymentState.COIN))(self.raise_crypt_pay)

    
    async def calculate_currency_amount(self, wallet: str, amount: Union[int, float]) -> Union[int, float] | None:
        rates = await self.crypto.get_exchange_rates()

        for rate in rates:
            if rate.source == wallet and rate.target == "USD":
                
                if rate:
                    return round(amount / rate.rate, 4)
        
        return None


    async def send_media(self, file_name: str, file_id: str):
        animation = file_id
        try:
            await self.bot.get_file(animation)
            return animation
        except TelegramBadRequest:
            animation = FSInputFile(os.path.join("media", file_name))
            return animation 
        

    async def inc_balance_callback(self, callback: CallbackQuery):
        await callback.answer()

        animation = await self.send_media('deposite.gif', self.deposit_id)
        await callback.message.edit_media(media=InputMediaAnimation(media=animation, caption="💰 <b>Выбери сумму пополнения:</b>"), reply_markup=await IBK.prices_inc())


    async def choose_num(self, call: CallbackQuery, state: FSMContext):
        await call.answer(' ')

        animation = await self.send_media('deposite.gif', self.deposit_id)
        await call.message.edit_media(media=InputMediaAnimation(media=animation, caption="<code>💳 Отправьте сумму пополнения:</code>"))
        await state.set_state(PaymentState.AMOUNT)


    async def choose_payment_m(self, m: Message, state: FSMContext):
        if not m.text.isdigit():
            return await m.answer("Нужно ввести именно число ‼️")
            
        amount = int(m.text)

        if amount < 1:
            return await m.answer('Сумма не должна быть меньше <b>1</b>')
            
        await state.update_data(amount=amount)
        await m.answer("💳 <b>Выбери способ оплаты:</b>", reply_markup=await IBK.methods(amount))
        await state.set_state(PaymentState.WALLET)


    async def choose_payment_c(self, call: CallbackQuery, state: FSMContext, callback_data: CallbackDataAmount):
        await call.answer()
        amount = callback_data.amount

        await state.update_data(amount=amount)
        animation = await self.send_media('deposite.gif', self.deposit_id)
        await call.message.edit_media(media=InputMediaAnimation(media=animation, caption="💳<b>Выбери способ оплаты:</b>"), reply_markup=await IBK.methods(amount))
        await state.set_state(PaymentState.WALLET)


    async def cryptobot_payment(self, call: CallbackQuery, state: FSMContext):
        await call.answer()
        animation = await self.send_media('deposite.gif', self.deposit_id)
        await call.message.edit_media(media=InputMediaAnimation(media=animation, caption="💲<b>Выбери валюту:</b>"), reply_markup=await IBK.choose_currency())
        await state.set_state(PaymentState.COIN)


    async def raise_crypt_pay(self, call: CallbackQuery, callback_data: CallbackDataCurrency, state: FSMContext):
        await call.answer()
        await call.message.delete()
        data = await state.get_data()

        amount = data['amount']
        currency = callback_data.currency
        calculate_amount = await self.calculate_currency_amount(wallet=currency, amount=amount)

        if calculate_amount:
            invoice = await self.crypto.create_invoice(amount=calculate_amount, asset=currency, description="Пополнение баланса")

            msg = await call.message.answer(
                "<code>⚠️ Совершите платеж строго в течение 15 минут!</code>\n"
                "➖➖➖\n"
                "<code>↪️ Перейдите по ссылке чтобы оплатить счет:</code>", reply_markup=await IBK.pay_crypto(url=invoice.bot_invoice_url))

            await state.update_data(invoice_id=invoice.invoice_id, msg_id=msg.message_id, chat_id=call.from_user.id)

            asyncio.create_task(self._process_check_payment_user(state))


    async def _process_check_payment_user(self, state: FSMContext):
        data = await state.get_data()
        amount_inc = data.get('amount')
        invoice_id = data['invoice_id']
        chat_id = data['chat_id']
        msg_id = data['msg_id']

        end_time = datetime.now() + timedelta(minutes=15)

        while datetime.now() < end_time:
            try:
                resp = await self.crypto.get_invoices(invoice_ids=[invoice_id])
                invoice_info = resp[0]
                status = invoice_info.status

                if status == "paid":
                    await self.db_manger.update_user(id=chat_id, balance=amount_inc)

                    await self.bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=msg_id,
                        text=f"<b>✅ Платёж успешно получен!</b>\nЗачислена сумма: {amount_inc}$",
                        reply_markup=await IBK.back_on_main_page()
                    )
                    await state.clear()
                    return

            except Exception as e:
                print(f"Ошибка при проверке оплаты: {e}")

            await asyncio.sleep(10)

        try:
            await self.crypto.delete_invoice(invoice_id=invoice_id)
        except Exception as e:
            print(f"Ошибка при удалении инвойса: {e}")

        await self.bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg_id,
            text="❌ Время оплаты истекло!"
        )
        await state.clear()


    async def disable_pay(self, call: CallbackQuery):
        await call.answer()
        await call.message.delete()
        animation = await self.send_media('menu.gif', self.menu_id)
        await call.message.answer_animation(animation=animation, caption="☁️ <b>ГЛАВНОЕ МЕНЮ</b>", reply_markup=await IBK.menu(user_id=call.from_user.id))