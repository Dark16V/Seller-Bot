from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from src.keyboards.callbackdata import *


class AdminyIBK():
    @staticmethod
    async def admin_panel_keyboard():
        admin_panel = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text='Рассылка 📢', callback_data='mailing'),
                    InlineKeyboardButton(text='Статистика 📊', callback_data='statistics')
                ],
                [
                    InlineKeyboardButton(text='Пользователи', callback_data='users'),
                    InlineKeyboardButton(text='Админские команды', callback_data='admins_comm')
                ],
                [
                    InlineKeyboardButton(text='Создать промокод 💳', callback_data='add_promo')
                ],
                [
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='back_to_menu')
                ]])
        return admin_panel
    


    @staticmethod
    async def type_statistic():
        types = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text='Статистика по продажам 📈', callback_data='sale_statistic')
                ],
                [
                    InlineKeyboardButton(text='Статистика по пользователей 👤', callback_data='user_statistic')
                ],
                [
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='back_to_menu')
                ]])
        return types
    

    @staticmethod
    async def get_user_statistic():
        buttons = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text='Получить .txt юзеров', callback_data='get_txt_users')
                    
                ],
                [
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='statistics')
                ]])
        return buttons
    

    @staticmethod
    async def check_user_info(user_id):
        buttons = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(text='Заказы пользователя', callback_data=CallbackDataUser(action='get_user', id=user_id).pack())
                ],
                [
                    InlineKeyboardButton(text='⬅️ Назад', callback_data='admin_panel')
                ]])
        return buttons