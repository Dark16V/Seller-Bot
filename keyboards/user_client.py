from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.callbackdata import *
from dotenv import load_dotenv
from urllib.parse import quote
import os
import ast

load_dotenv()

ADMINS = ast.literal_eval(os.getenv("ADMINS", "[]"))

class UserIBK():
    @staticmethod
    async def menu(user_id):
        menu = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Купить 🛒', callback_data='buy'),
                    InlineKeyboardButton(text='Профиль 👤', callback_data='profile')
                ],
                [
                    InlineKeyboardButton(text='Пополнить 💳', callback_data='inc_balance'),
                    InlineKeyboardButton(text='FAQ ❔', url='https://telegra.ph/FAQ--CHasto-zadavaemye-voprosy-09-17-2')
                ]
            ]
        )
        if user_id in ADMINS:
            menu.inline_keyboard.append(
                [InlineKeyboardButton(text='Админ панель ⚙️', callback_data='admin_panel')]
            )
        return menu


    @staticmethod
    async def back_on_profile():
        back = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='profile')
                ]
            ]
        )

        return back
    
    @staticmethod
    async def back_on_main_page():
        back = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='⬅️ На главную', callback_data='back_to_menu')
                ]
            ]
        )

        return back


    @staticmethod
    async def categories_products():
        produects = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Proxy 🛡️', callback_data='buy_proxy'),
                    InlineKeyboardButton(text='VPN 🌐', callback_data='buy_vpn')
                ],
                [
                    InlineKeyboardButton(text='Servers 🖥️', callback_data='buy_servers'),
                ],
                [
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='back_to_menu')
                ]
            ]
        )
        return produects
    


    @staticmethod
    async def get_categories_keyboard():
        categories = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='🔹IPv4', callback_data='cat_ipv4'),
                    InlineKeyboardButton(text='🔹IPv6', callback_data='cat_ipv6')
                ],
                [
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='buy')
                ]
            ]
        )

        return categories

    @staticmethod
    async def profile_keyboard():
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Пополнить 💳', callback_data='inc_balance'),
                    InlineKeyboardButton(text='Мои заказы 🛍️', callback_data='my_orders')
                ],
                [
                    InlineKeyboardButton(text='Мои прокси 💼', callback_data='my_proxies')
                ],
                [
                    InlineKeyboardButton(text='Тех Поддержка 🤝', callback_data='help')
                ],
                [
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='back_to_menu')
                ]

            ]
        )
        return keyboard

    
    
    @staticmethod
    async def confirm_order():
        confirm = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='💳 Оплатить', callback_data='confirm_order'),
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='back_to_menu')
                ]
            ]
        )
        return confirm
    
    @staticmethod
    async def need_inc_balance():
        confirm = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='💵 Пополнить баланс', callback_data='inc_balance')
                ],
                [
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='back_to_menu')
                ]
            ]
        )
        return confirm
    
    
    
    
    
    @staticmethod
    async def amount_proxy():
        prices = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='🔹1', callback_data=CallbackDataProxy(action="amount_proxy", amount=1).pack()),
                    InlineKeyboardButton(text='🔹3', callback_data=CallbackDataProxy(action="amount_proxy", amount=3).pack()),

                ],
                [
                    InlineKeyboardButton(text='🔹5', callback_data=CallbackDataProxy(action="amount_proxy", amount=5).pack()),
                    InlineKeyboardButton(text='🔹10', callback_data=CallbackDataProxy(action="amount_proxy", amount=10).pack()),
                ],
                [
                    InlineKeyboardButton(text='Другое количество', callback_data='my_amount_proxy')
                ],
                [
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='buy_proxy')
                ]
            ]
        )
        return prices
    

    

    
    @staticmethod
    async def accept():
        buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Продолжить ✔️ ', callback_data=f'accept')
                ],
                [
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='buy_proxy')
                ]
            ]
        )
        return buttons
    
    @staticmethod
    async def my_proxies():
        buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Получить мои прокси', callback_data=f'get_my_proxies')
                ],
                [
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='profile')
                ]
            ]
        )
        return buttons
    
    
    

    @staticmethod
    async def continue_vpn():
        buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Приобрести 🛒', callback_data='continue_vpn')
                ],
                [
                    InlineKeyboardButton(text='Инструкции по использованию 💡', callback_data='instr')
                ],
                [
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='buy')
                ]
            ]
        )
        return buttons
    

    @staticmethod
    async def choose_amount_vpn():
        encoded_text = quote('Здравствуйте, хотел бы купить VPN в количестве: ...')
        url = f"https://t.me/Code_Adm?text={encoded_text}"
        prices = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='🔹1', callback_data=CallbackDataVPNAmount(action="amount_vpn", amount=1).pack()),
                    InlineKeyboardButton(text='🔹2', callback_data=CallbackDataVPNAmount(action="amount_vpn", amount=2).pack()),
                    InlineKeyboardButton(text='🔹3', callback_data=CallbackDataVPNAmount(action="amount_vpn", amount=3).pack())
                ],
                [
                    InlineKeyboardButton(text='🔹5', callback_data=CallbackDataVPNAmount(action="amount_vpn", amount=5).pack()),
                    InlineKeyboardButton(text='🔹10', callback_data=CallbackDataVPNAmount(action="amount_vpn", amount=10).pack())
                ],
                [
                    InlineKeyboardButton(text='Своё количество', url=url)
                ],
                [
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='buy_vpn')
                ]
            ]
        )
        return prices
    

    @staticmethod
    async def pay_vpn_order(amount: int):
        buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Оплатить 💳', callback_data=CallbackDataVPN(action="pay_vpn_order", amount=amount).pack()),
                    InlineKeyboardButton(text='Отмена ❌', callback_data='buy')
                ]
            ]
        )
        return buttons
    
    @staticmethod
    async def succes_pay_url(text):
        encoded_text = quote(text)
        url = f"https://t.me/Code_Adm?text={encoded_text}"
        buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Получить товар', url=url)
                ],
                [
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='back_to_menu')
                ]
            ]
        )
        return buttons
    
    @staticmethod
    async def help(text):
        encoded_text = quote(text)
        url = f"https://t.me/Code_Adm?text={encoded_text}"
        buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Обратится', url=url)
                ],
                [
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='back_to_menu')
                ]
            ]
        )
        return buttons
    
    
    
    @staticmethod
    async def select_country_proxy(category_dict):
        countries_list = [(name.capitalize(), code) for name, code in category_dict.items()]

        keyboard = []
        for i in range(0, len(countries_list), 2):
            row = [
                InlineKeyboardButton(
                    text=countries_list[i][0],
                    callback_data=CallbackDataProxyCountry(action="country", country=countries_list[i][1]).pack()
                )
            ]
            if i + 1 < len(countries_list):
                row.append(
                    InlineKeyboardButton(
                        text=countries_list[i + 1][0],
                        callback_data=CallbackDataProxyCountry(action="country", country=countries_list[i + 1][1]).pack()
                    )
                )
            keyboard.append(row)

        # Кнопка назад
        keyboard.append([InlineKeyboardButton(text='⬅️ Назад', callback_data='buy_proxy')])

        return InlineKeyboardMarkup(inline_keyboard=keyboard)


    
    @staticmethod
    async def select_type():
        buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='♦️ HTTPS', callback_data='http'),
                    InlineKeyboardButton(text='♦️ SOCKS5', callback_data='socks')
                    
                ],
                [
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='buy_proxy')
                ]
            ]
        )
        return buttons
    

    
    
    @staticmethod
    async def select_coin():
        buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='USDT', callback_data='usdt')
                    
                ],
                [
                    InlineKeyboardButton(text='TON', callback_data='ton')
                ],
                [
                    InlineKeyboardButton(text='TRX', callback_data='trx')
                    
                ],
                [
                    InlineKeyboardButton(text='BTC', callback_data='btc')
                ],
                [
                    InlineKeyboardButton(text='ETH', callback_data='eth')
                    
                ],
                [
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='inc_balance')
                ]
            ]
        )
        return buttons
    

    @staticmethod
    async def select_period():
        buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='7 дней', callback_data=CallbackDataSelectPeriod(action="period", period=7).pack()),
                    InlineKeyboardButton(text='14 дней', callback_data=CallbackDataSelectPeriod(action="period", period=14).pack())
                ],
                [
                    InlineKeyboardButton(text='1 месяц', callback_data=CallbackDataSelectPeriod(action="period", period=30).pack()),
                    InlineKeyboardButton(text='2 месяца', callback_data=CallbackDataSelectPeriod(action="period", period=60).pack())
                ],
                [
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='buy_proxy')
                ]
            ]
        )
        return buttons
    

    @staticmethod
    async def period_prolong():
        buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='7 дней', callback_data=CallbackDataSelectPeriod(action="period_prolong", period=7).pack()),
                    InlineKeyboardButton(text='14 дней', callback_data=CallbackDataSelectPeriod(action="period_prolong", period=14).pack())
                ],
                [
                    InlineKeyboardButton(text='1 месяц', callback_data=CallbackDataSelectPeriod(action="period_prolong", period=30).pack())
                ]
            ]
        )
        return buttons
    

    @staticmethod
    async def accept_prolong():
        buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Оплатить 💳', callback_data='pay_prolong'),
                ],
                [
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='back_to_menu')
                ]
            ]
        )
        return buttons
    

    @staticmethod
    async def select_type_instr():
        buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='IOS 🍏', callback_data='ios'),
                    InlineKeyboardButton(text='Android 📱', callback_data='android')
                    
                ],
                [
                    InlineKeyboardButton(text='Windows 💠', callback_data='winda'),
                    InlineKeyboardButton(text='Mac OS 💻', callback_data='ios')
                ],
                [
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='buy_vpn')
                ]
            ]
        )
        return buttons
    
    @staticmethod
    async def con_ios():
        buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Продолжить ➡️', callback_data='con_ios')
                ],
                [
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='buy_vpn')
                ]
            ]
        )
        return buttons
    

    @staticmethod
    async def back_on_vpn():
        back = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='buy_vpn')
                ]
            ]
        )

        return back
    

    @staticmethod
    async def con_andr():
        buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Продолжить ➡️', callback_data='con_andr')
                ],
                [
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='buy_vpn')
                ]
            ]
        )
        return buttons
    

    @staticmethod
    async def sub():
        button = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Подписаться ✅', url='t.me/ProxyCloudCH')
                ],
                [
                    InlineKeyboardButton(text='Проверить 🔍', callback_data='check_sub')
                ]
            ]
        )
        return button

