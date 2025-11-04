from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, StateFilter
from aiogram import F

from sqlalchemy.future import select
from sqlalchemy import func

from src.keyboards import IBK
from src.keyboards.callbackdata import CallbackDataUser

from src.utils.state.state import Mailing, UsersState, Promo
from src.utils.filters import IsAdmin

from aiogram.types import BufferedInputFile

from sqlalchemy import distinct

import matplotlib.pyplot as plt

from db import get_db, async_session
from src.models.order import Order

from datetime import datetime, timedelta

from src.services import DbManager

import asyncio

import io



class Admin():
    def __init__(self, config):
        self.dp = config.dp
        self.db_manager = DbManager(async_session)
        self.bot = config.bot

    async def reg_handler(self):
        self.dp.callback_query(F.data == 'admin_panel')(self.admin_panel)
        self.dp.callback_query(F.data == 'mailing')(self.mailing)
        self.dp.message(StateFilter(Mailing.message), F.text)(self.malling_handler_message)
        self.dp.callback_query(F.data == 'statistics')(self.statistics)
        self.dp.callback_query(F.data == 'sale_statistic')(self.sale_statistic)
        self.dp.callback_query(F.data == 'user_statistic')(self.user_statistic)
        self.dp.callback_query(F.data == 'get_txt_users')(self.get_txt_user)
        self.dp.message(IsAdmin(), (Command('ban')))(self.cmd_ban)
        self.dp.message(IsAdmin(), (Command('unban')))(self.cmd_unban)
        self.dp.message(IsAdmin(), (Command('ub')))(self.cmd_update_balance)
        self.dp.callback_query(F.data == 'users')(self.check_users)
        self.dp.message(StateFilter(UsersState.id), F.text)(self.get_user_ip)
        self.dp.callback_query(CallbackDataUser.filter(F.action == 'get_user'))(self.get_user_orders)
        self.dp.callback_query(F.data == 'admins_comm')(self.admins_commands)
        self.dp.callback_query(F.data == 'add_promo')(self.add_promo)
        self.dp.message(StateFilter(Promo.code), F.text)(self.set_code)
        self.dp.message(StateFilter(Promo.discount), F.text)(self.set_discount)
        self.dp.message(StateFilter(Promo.period), F.text)(self.set_period)
        self.dp.message(StateFilter(Promo.usage_limit), F.text)(self.set_usage_limit)


    async def admin_panel(self, callback: CallbackQuery):
        await callback.answer(' ')
        await callback.message.delete()
        await callback.message.answer('Админ панель ⚙️', reply_markup=await IBK.admin_panel_keyboard())




    async def mailing(self, call: CallbackQuery, state: FSMContext):
        await call.answer(' ')
        await state.set_state(Mailing.message)
        await call.message.answer('Отправь сообщение для рассылки всем пользователям')


    async def malling_handler_message(self, m: Message, state: FSMContext):
        users = await self.db_manager.get_user(is_baned=False)

        for user in users:
            try:
                await self.bot.send_message(chat_id=user.telegram_id, text=m.text)
                await asyncio.sleep(0.3)  
            except Exception as e:
                print(f"Не удалось отправить {user.telegram_id}: {e}")
        await state.clear()
        await m.answer('Рассылка завершена ✅')

    

    async def statistics(self, call: CallbackQuery):
        await call.answer(' ')
        await call.message.answer('📊 Выбери тип статистики: ', reply_markup=await IBK.type_statistic())


    async def user_statistic(self, call: CallbackQuery):
        users = await self.db_manager.get_user(id='all')
        await call.answer('')
        async for sess in get_db():
            active_users_result = await sess.execute(
            select(distinct(Order.user_id))
            )
            active_users_ids = [r[0] for r in active_users_result.all()]
            break
        await call.message.answer(f'👤 Юзеры бота\nЮзеров за все время: {len(users)}\nАктивные юзеры {len(active_users_ids)}', 
                                  reply_markup=await IBK.get_user_statistic())
        

    async def get_txt_user(self, call: CallbackQuery):
        await call.answer()
        users = await self.db_manager.get_user(id='all')
        orders = await self.db_manager.get_order(status='succes')

        file_content = ""
        for user in users:
            user_orders_count = sum(1 for o in orders if o.user_id == user.telegram_id)
            nickname = (await self.bot.get_chat(user.telegram_id)).first_name
            date_reg = user.reg_time.strftime("%Y-%m-%d %H:%M:%S")
            file_content += f"id{user.telegram_id} | {nickname} | {date_reg} | {user_orders_count}\n"

        file = BufferedInputFile(file_content.encode("utf-8"), filename="users_list.txt")

        await call.message.answer_document(file, caption="📄 Список пользователей", reply_markup=await IBK.back_on_main_page())


    async def sale_statistic(self, call: CallbackQuery):
        await call.answer(' ')
        async for session in get_db():
            result = await session.execute(
                select(func.date(Order.created_at), func.sum(Order.requested))
                .group_by(func.date(Order.created_at))
                .order_by(func.date(Order.created_at))
            )
            stats = result.all()
            break

        if not stats:
            await call.message.answer("📊 Пока нет продаж.")
            return

        dates = [str(r[0]) for r in stats]
        proxies = [r[1] for r in stats]

        plt.figure(figsize=(7, 5))
        plt.plot(dates, proxies, marker="o", linestyle="-", color="blue")
        plt.title("Статистика продаж (по количеству прокси)")
        plt.xlabel("Дата")
        plt.ylabel("Количество прокси")
        plt.xticks(rotation=45)
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        plt.close()

        photo = BufferedInputFile(buffer.read(), filename="proxies_stats.png")
        await call.message.answer_photo(photo, caption="📊 Статистика продаж по купленным прокси", reply_markup=await IBK.admin_panel_keyboard())

    
    async def cmd_ban(self, message: Message, user):
        args = message.text.split()
        if len(args) < 2:
            await message.answer("❗ Формат:\n/ban `user_id`", parse_mode='Markdown')
            return

        try:
            user_id = int(args[1])
        except ValueError:
            await message.answer("❗ user_id должен быть числом.")
            return

        try:
            await self.db_manager.update_user(id=user_id, is_baned=True)
        except AttributeError:
            await message.answer('Такого пользователя не существует в бд ‼️')
            return


        await message.answer(f"✅ Пользователь `{user_id}` забанен.", parse_mode='Markdown')


    async def cmd_unban(self, message: Message, user):
        args = message.text.split()
        if len(args) < 2:
            await message.answer("❗ Формат:\n/unban `user_id`", parse_mode='Markdown')
            return

        try:
            user_id = int(args[1])
        except ValueError:
            await message.answer("❗ user_id должен быть числом.")
            return

        try:
            await self.db_manager.update_user(id=user_id, is_baned=False)  
        except AttributeError:
            await message.answer('Такого пользователя не существует в бд ‼️')
            return


        await message.answer(f"✅ Пользователь `{user_id}` разбанен.", parse_mode='Markdown')


    async def cmd_update_balance(self, message: Message, user):
        args = message.text.split()
        if len(args) != 3:
            await message.answer("❗ Формат:\n/ub `user_id`  `+/-число`", parse_mode='Markdown')
            return

        try:
            user_id = int(args[1])
            amount = int(args[2]) 
        except ValueError:
            await message.answer("❗ user_id и число должны быть числами.")
            return

        user = await self.db_manager.get_user(id=user_id)

        if not user:
            await message.answer(f"❌ Пользователь `{user_id}` не найден.", reply_markup='Markdown')
            return

        await self.db_manager.update_user(id=user.telegram_id, balance=amount)

        await message.answer(
                f"✅ Баланс пользователя `{user_id}` обновлён.\n"
                f"Новый баланс: `{user.balance}$`", parse_mode='Markdown'
            )


        
    async def check_users(self, call: CallbackQuery, state: FSMContext):
        await call.answer()
        await call.message.answer("Введи айди пользователя: ")
        await state.set_state(UsersState.id)


    async def get_user_ip(self, m: Message, state: FSMContext):
        if not m.text.isdigit():
            await m.answer('Неверный айди')
            return 
        
        user = await self.db_manager.get_user(id=int(m.text))
        if not user:
            await m.answer('Такого юзера не существует')
            return

        await m.answer(f'Пользователь:\nID: `{user.telegram_id}`\nBalance: `{user.balance} $`', parse_mode='Markdown', reply_markup=await IBK.check_user_info(user_id=int(m.text)))
        await state.clear()

    async def get_user_orders(self, call: CallbackQuery, callback_data: CallbackDataUser):
        await call.answer()
        user_id = callback_data.id
        orders = await self.db_manager.get_order(user_id=user_id)
        
        if not orders:
            await call.message.answer('У данного юзера еще нет заказов', reply_markup=await IBK.check_user_info(user_id=user_id))
            return
        
        for order in orders:
            await call.message.answer(f"ID заказа: `{order.track_number}`\n"
                f"Категория: `{order.category}`\n"
                f"Количество: `{order.requested}`\n"
                f"Статус: `{order.status}`\n"
                f"Время создания: `{order.created_at}`\n"
                f"Выполненые шаги: {order.steps}", parse_mode='Markdown')
            await asyncio.sleep(0.3)
        await call.message.answer(f'Все заказы пользователя `{user_id}` 👆', parse_mode='Markdown', reply_markup=await IBK.check_user_info(user_id=user_id))


    async def admins_commands(self, call: CallbackQuery):
        await call.answer()
        await call.message.answer('Все админ команды:\n\n/ban `user_id` - бан юзера по айди\n\n/unban `user_id` - разбан юзера по айди\n\n/ub `user_id`  `+\\-number` - отнимает или добавляет number от баланса юзера которого вы указали айди', parse_mode='Markdown')



    async def add_promo(self, call: CallbackQuery, state: FSMContext):
        await call.answer(' ')
        await call.message.answer('Введи промокод')
        await state.set_state(Promo.code)

    
    async def set_code(self, m: Message, state: FSMContext):
        await state.update_data(code=m.text)
        await m.answer('Введи процент добавления (число от 1 до 100)')
        await state.set_state(Promo.discount)

    async def set_discount(self, m: Message, state: FSMContext):
        if not m.text.isdigit() or not (1 <= int(m.text) <= 100):
            await m.answer('Процент должен быть числом от 1 до 100.')
            return
        await state.update_data(discount=int(m.text))
        await m.answer('Введи срок действия промокода в часах (число).')
        await state.set_state(Promo.period)

    async def set_period(self, m: Message, state: FSMContext):
        if not m.text.isdigit() or int(m.text) <= 0:
            await m.answer('Период должен быть положительным числом.')
            return
        await state.update_data(period=int(m.text))
        await m.answer('Введи лимит использования промокода (число).')
        await state.set_state(Promo.usage_limit)

    async def set_usage_limit(self, m: Message, state: FSMContext):
        if not m.text.isdigit() or int(m.text) <= 0:
            await m.answer('Лимит использования должен быть положительным числом.')
            return
        await state.update_data(usage_limit=int(m.text))

        data = await state.get_data()
        code = data['code']
        discount = data['discount']
        period = data['period']
        usage_limit = data['usage_limit']

        exspired_at = datetime.utcnow() + timedelta(hours=period)

        new_promo = await self.db_manager.create_promocode(code=code, discount=discount, exspired_at=exspired_at, usage_limit=usage_limit)

        await m.answer(f'Промокод создан:\nКод: `{new_promo.code}\n`Процент: `{new_promo.discount}%`\nДействует до: `{new_promo.exspired_at}`\nЛимит использования: `{new_promo.usage_limit}`', parse_mode='Markdown', reply_markup=await IBK.admin_panel_keyboard())
        await state.clear()
