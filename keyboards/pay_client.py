from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.callbackdata import *


class PayIBK():
    @staticmethod
    async def prices_inc():
        prices = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='1 $ ', callback_data=CallbackDataAmount(action="amount", amount=1).pack()),
                    InlineKeyboardButton(text='5 $', callback_data=CallbackDataAmount(action="amount", amount=5).pack()),
                    InlineKeyboardButton(text='10 $', callback_data=CallbackDataAmount(action="amount", amount=10).pack())
                ],
                [
                    InlineKeyboardButton(text='15 $', callback_data=CallbackDataAmount(action="amount", amount=15).pack()),
                    InlineKeyboardButton(text='20 $', callback_data=CallbackDataAmount(action="amount", amount=20).pack())
                ],
                [
                    InlineKeyboardButton(text='Другая сумма', callback_data='my_num')
                ],
                [
                    InlineKeyboardButton(text='Активировать промокод', callback_data='use_promo')
                ],
                [
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='back_to_menu')
                ]
            ]
        )
        return prices
    


    @staticmethod
    async def methods(amount):
        methods = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='CryptoBot ', callback_data=f'cryptobot_{amount}')
                ],
                [
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='back_to_menu')
                ]
            ]
        )
        return methods
    

    @staticmethod
    async def choose_currency():
        menu = InlineKeyboardBuilder()
        cryptocurrencies  = ["USDT", "TON", "TRX", "BTC", "ETH"]

        for currency in cryptocurrencies:
            menu.button(text=currency, callback_data=CallbackDataCurrency(action="get_currency", currency=currency))

        return menu.adjust(1).as_markup()
    

    @staticmethod
    async def pay_crypto(url):
        pay = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Оплатить 💳', url=url),
                    InlineKeyboardButton(text='Отменить 🚫', callback_data='disable_pay'),
                ]
            ]
        )
        return pay