from aiogram.types import CallbackQuery, Message, InputMediaAnimation
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from aiogram import F

from aiocryptopay import AioCryptoPay, Networks

from keyboards import IBK
from keyboards.callbackdata import *

from utils.state.state import PaymentState, UsePromo
from utils.utils import get_media

from services import DbManager

from dotenv import load_dotenv

from db import async_session

import os
import asyncio
from typing import Union
from datetime import datetime, timedelta


load_dotenv()

class Payment:
    def __init__(self, config):
        self.dp = config.dp
        self.bot = config.bot
        self.db_manger = DbManager(async_session)
        self.crypto = AioCryptoPay(token=os.getenv('CRYPTO_TOKEN'), network=Networks.MAIN_NET)


    async def reg_handler(self):
        self.dp.callback_query(F.data == 'inc_balance')(self.inc_balance_callback)
        self.dp.callback_query(F.data == 'my_num')(self.choose_num)
        self.dp.message(StateFilter(PaymentState.AMOUNT), F.text)(self.choose_payment_m)
        self.dp.callback_query(CallbackDataAmount.filter(F.action == 'amount'))(self.choose_payment_c)
        self.dp.callback_query(F.data.startswith("cryptobot_"), StateFilter(PaymentState.WALLET))(self.cryptobot_payment)
        self.dp.callback_query(CallbackDataCurrency.filter(F.action == 'get_currency'), StateFilter(PaymentState.COIN))(self.raise_crypt_pay)
        self.dp.callback_query(F.data == 'disable_pay', StateFilter(PaymentState.PAY_WAIT))(self.disable_pay)
        self.dp.callback_query(F.data == 'use_promo')(self.write_code)
        self.dp.message(StateFilter(UsePromo.code), F.text)(self.use_promo)


    
    async def calculate_currency_amount(self, wallet: str, amount: Union[int, float]) -> Union[int, float] | None:
        rates = await self.crypto.get_exchange_rates()

        for rate in rates:
            if rate.source == wallet and rate.target == "USD":
                
                if rate:
                    return round(amount / rate.rate, 4)
        
        return None
        

    async def inc_balance_callback(self, callback: CallbackQuery):
        await callback.answer()

        animation = await get_media('deposite')
        await callback.message.edit_media(media=InputMediaAnimation(media=animation, caption="💰 <b>Выбери сумму пополнения:</b>"), reply_markup=await IBK.prices_inc())


    async def choose_num(self, call: CallbackQuery, state: FSMContext):
        await call.answer(' ')

        animation = await get_media('deposite')
        await call.message.edit_media(media=InputMediaAnimation(media=animation, caption="<code>💳 Отправьте сумму пополнения:</code>"))
        await state.set_state(PaymentState.AMOUNT)


    async def choose_payment_m(self, m: Message, state: FSMContext):
        try:
            amount = float(m.text.replace(",", "."))
        except: return await m.answer("Введите число!")

        if amount < float(1):
            return await m.answer("<b>Неверный ввод ❕\nМинимальная сумма пополнения 1$</b>")

        await state.update_data(amount=amount)
        await m.answer("💳 <b>Выбери способ оплаты:</b>", reply_markup=await IBK.methods(amount))
        await state.set_state(PaymentState.WALLET)


    async def choose_payment_c(self, call: CallbackQuery, state: FSMContext, callback_data: CallbackDataAmount):
        await call.answer()
        amount = callback_data.amount

        await state.update_data(amount=amount)
        animation = await get_media('deposite')
        await call.message.edit_media(media=InputMediaAnimation(media=animation, caption="💳<b>Выбери способ оплаты:</b>"), reply_markup=await IBK.methods(amount))
        await state.set_state(PaymentState.WALLET)


    async def cryptobot_payment(self, call: CallbackQuery, state: FSMContext):
        await call.answer()
        animation = await get_media('deposite')
        await call.message.edit_media(media=InputMediaAnimation(media=animation, caption="💲<b>Выбери валюту:</b>"), reply_markup=await IBK.choose_currency())
        await state.set_state(PaymentState.COIN)


    async def raise_crypt_pay(self, call: CallbackQuery, callback_data: CallbackDataCurrency, state: FSMContext):
        await call.answer()
        await call.message.delete()
        data = await state.get_data()
        code = data.get('promocode')
        amount = data['amount']
        result = await self.db_manger.get_promo_users(user_id=call.from_user.id)
        promocode = result[0] if result[0] else None
        code = result[1].code if result[1] else None
        if promocode:
            if promocode.exspired_at and promocode.exspired_at < datetime.utcnow():
                await call.message.answer(f'<b>Промокод {code} истёк!\nПоэтому прибавок к пополнению не будет примененен </b>‼️')
                promocode = None
            else:
                await call.message.answer(f'<b>Будет применён промокод на +{promocode.discount}% к пополнению баланса!\n{amount}$ -> {round(amount * (1 + (promocode.discount / 100)), 2)}</b>$ ✅')
                await state.update_data(promocode=promocode.code_id)
        
        currency = callback_data.currency
        calculate_amount = await self.calculate_currency_amount(wallet=currency, amount=amount)
        

        if calculate_amount:
            invoice = await self.crypto.create_invoice(amount=calculate_amount, asset=currency, description="Пополнение баланса")

            msg = await call.message.answer(
                "<code>⚠️ Совершите платеж строго в течение 15 минут!</code>\n"
                "➖➖➖\n"
                "<code>↪️ Перейдите по ссылке чтобы оплатить счет:</code>", reply_markup=await IBK.pay_crypto(url=invoice.bot_invoice_url))

            task = asyncio.create_task(self._process_check_payment_user(state))
            await state.set_state(PaymentState.PAY_WAIT)

            calculate_amount = round(calculate_amount * (1 + (promocode.discount / 100)), 2) if promocode else calculate_amount
            await state.update_data(invoice_id=invoice.invoice_id, msg_id=msg.message_id, chat_id=call.from_user.id, task=task, amount=amount)

            


    async def _process_check_payment_user(self, state: FSMContext):
        data = await state.get_data()
        amount_inc = data.get('amount')
        invoice_id = data['invoice_id']
        chat_id = data['chat_id']
        msg_id = data['msg_id']
        promo_id = data['promocode'] if 'promocode' in data else None
        end_time = datetime.now() + timedelta(minutes=15)

        while datetime.now() < end_time:
            try:
                resp = await self.crypto.get_invoices(invoice_ids=[invoice_id])
                invoice_info = resp[0]
                status = invoice_info.status

                if status == "paid":
                    user = await self.db_manger.update_user(id=chat_id, balance=amount_inc)
                    if promo_id:
                        await self.db_manger.deactivate_promo_user(code_id=promo_id)
                    
                    if user.referral_uid:
                        try:
                            await self.bot.send_message(chat_id=user.referral_uid, text=f"<b>⚡️Ваш реферал принес вам: {round((amount_inc * 5) / 100, 2)}$</b>")
                        except Exception as e: print(e)


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


    async def disable_pay(self, call: CallbackQuery, state: FSMContext):
        await call.answer()
        await call.message.delete()
        data = await state.get_data()
        task = data.get('task')
        if task:
            task.cancel()
        await state.clear()
        animation = await get_media('menu')
        await call.message.answer_animation(animation=animation, caption="☁️ <b>ГЛАВНОЕ МЕНЮ</b>", reply_markup=await IBK.menu(user_id=call.from_user.id))

    async def write_code(self, call: CallbackQuery, state: FSMContext):
        await call.answer()
        text = """
❔Любой <b>«абуз»</b> системных промокодов <b>нарушает</b> правила сообщества, и ведет за собой <b>перманентую блокировку.</b>
↪️ <b>Введите промокод</b> без <b>«ковычек»</b>, например [<code>FREE25</code>]
"""
        await call.message.answer(text)
        await state.set_state(UsePromo.code)

    async def use_promo(self, m: Message, state: FSMContext):
        code = m.text.strip()
        promocode = await self.db_manger.get_promocode(code=code)

        if not promocode:
            return await m.answer('<b>Неправильно введен промокод❕</b>')

        if promocode.exspired_at and promocode.exspired_at < datetime.utcnow():
            await self.db_manger.del_all(code=code)
            return await m.answer('<b>Промокод истёк ❕</b>')

        if promocode.usage_limit and promocode.used_count >= promocode.usage_limit:
            return await m.answer('<b>Промокод достиг лимита использования ❕</b>')

        used_promo = await self.db_manger.get_promo_users(user_id=m.from_user.id)
        if used_promo[0]:
            return await m.answer('<b>Вы уже использовали промокод ранее ❕</b>')

        await self.db_manger.use_promocode(user_id=m.from_user.id, promocode=promocode)
        await m.answer(f'Промокод {promocode.code} успешно применён! Вы получите +{promocode.discount}% при следующем пополнении баланса.', reply_markup=await IBK.back_on_main_page())
        await state.clear()