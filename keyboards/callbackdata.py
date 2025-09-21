from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton


class CallbackDataAmount(CallbackData, prefix="amount"):
    action: str
    amount: int

class CallbackDataCurrency(CallbackData, prefix="currency"):
    action: str
    currency: str

class CallbackDataUser(CallbackData, prefix="amount"):
    action: str
    id: int

class CallbackDataSelectPeriod(CallbackData, prefix="period"):
    action: str
    period: int

class CallbackDataProxyCountry(CallbackData, prefix='country'):
    action: str
    country: str

class CallbackDataVPNAmount(CallbackData, prefix='amount_vpn'):
    action: str
    amount: int

class CallbackDataVPN(CallbackData, prefix="pay_vpn_order"):
    action: str
    amount: int

class CallbackDataProxy(CallbackData, prefix="amount_proxy"):
    action: str
    amount: int


class OrdersPage(CallbackData, prefix="orders"):
    page: int

class ProxiesPage(CallbackData, prefix="proxies"):
    page: int

class ProlongProxy(CallbackData, prefix="prolong"):
    proxy_id: int

def build_orders_keyboard(page: int, total: int):
    builder = InlineKeyboardBuilder()

    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=OrdersPage(page=page - 1).pack()))
        
    if page * 1 < total:
        nav_buttons.append(InlineKeyboardButton(text="➡️", callback_data=OrdersPage(page=page + 1).pack()))


    if nav_buttons:
        builder.row(*nav_buttons)

    builder.row(
        InlineKeyboardButton(text="↩️ Назад", callback_data="profile")
    )

    return builder.as_markup()

def build_proxies_keyboard(page: int, total: int, proxy_id: int):
    builder = InlineKeyboardBuilder()

    nav_buttons = []
    if page > 1:
        nav_buttons.append(InlineKeyboardButton(text="⬅️", callback_data=ProxiesPage(page=page - 1).pack()))
        
    if page * 1 < total:
        nav_buttons.append(InlineKeyboardButton(text="➡️", callback_data=ProxiesPage(page=page + 1).pack()))


    builder.row(
        InlineKeyboardButton(text="Продлить", callback_data=ProlongProxy(proxy_id=proxy_id).pack())
    )

    builder.row(
        InlineKeyboardButton(text="Скачать все прокси (.txt)", callback_data='get_my_proxies')
    )

    if nav_buttons:
        builder.row(*nav_buttons)

    builder.row(
        InlineKeyboardButton(text="↩️ Назад", callback_data="profile")
    )

    return builder.as_markup()