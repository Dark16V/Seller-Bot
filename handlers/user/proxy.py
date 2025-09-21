from aiogram.types import Message, CallbackQuery, FSInputFile, BufferedInputFile, InputMediaAnimation
from aiogram.filters import StateFilter
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram import F

from keyboards import IBK
from keyboards.callbackdata import *

from db import get_db, async_session
from models.order import Order
from models.user import User

from utils.state.state import NumProx, Prolong
from utils.loguru import logger
from config import proxy_info
import aiohttp

from datetime import datetime

import os
import uuid
import asyncio

from services import DbManager

from dotenv import load_dotenv
from config import ipv6, ipv4

load_dotenv()

class ProxyClient():
    def __init__(self, dp, bot):
        self.dp = dp
        self.bot = bot
        self.api_key = os.getenv('API_KEY')
        self.menu_id = 'CgACAgIAAxkBAAMFaMKDp4R4ZNpd4G3rbPbvVfMAAbA0AAJvfwACf0UYSpntdLDLaMBZNgQ'
        self.catalogue_id = 'CgACAgIAAxkBAAMLaMKEG9RnqxCELyg5SiWaFZXyWl0AAm5_AAJ_RRhKiu5ZRQOxWgw2BA'
        self.profile_id = 'CgACAgIAAxkBAAMOaMKETaEfPD7btpw6-xltJHM6MQMAAnB_AAJ_RRhKvaDK5arl6C82BA'
        self.db_manager = DbManager(async_session)
        self.x_price = 1.3


    async def reg_handler(self):
        self.dp.callback_query(F.data == 'buy_proxy')(self.buy_proxy_callback)
        self.dp.callback_query(F.data.startswith('cat_'))(self.category_callback)
        self.dp.callback_query((F.data == 'http') | (F.data == 'socks'))(self.type_callback)
        self.dp.callback_query(CallbackDataProxyCountry.filter(F.action == 'country'))(self.select_country)
        self.dp.callback_query(F.data == 'accept')(self.accept_handler)
        self.dp.callback_query(CallbackDataProxy.filter(F.action == 'amount_proxy'))(self.select_amount_proxy)
        self.dp.callback_query(F.data == 'my_amount_proxy')(self.write_amount_proxy)
        self.dp.message(StateFilter(NumProx.number), F.text)(self.handle_number)
        self.dp.callback_query(CallbackDataSelectPeriod.filter(F.action == 'period'))(self.select_period)
        self.dp.callback_query(F.data == 'confirm_order')(self.handler_confirm_order)
        self.dp.callback_query(F.data == 'my_proxies')(self.my_proxies)
        self.dp.callback_query(ProxiesPage.filter())(self.proxies_page_handler)
        self.dp.callback_query(ProlongProxy.filter())(self.prolong)
        self.dp.callback_query(CallbackDataSelectPeriod.filter(F.action == 'period_prolong'))(self.prolong_period)
        self.dp.callback_query(F.data == 'pay_prolong')(self.pay_prolong)
        self.dp.callback_query(F.data == 'get_my_proxies')(self.get_my_proxies)


    async def send_media(self, file_name: str, file_id: str):
        animation = file_id
        try:
            await self.bot.get_file(animation)
            return animation
        except TelegramBadRequest:
            animation = FSInputFile(os.path.join("media", file_name))
            return animation 

    async def buy_proxy_callback(self, callback: CallbackQuery):
        await callback.answer()

        animation = await self.send_media('catalogue.gif', self.catalogue_id)
        await callback.message.edit_media(media=InputMediaAnimation(media=animation, 
                                            caption="📂 <b>Выбери категорию 👇</b>"), 
                                            reply_markup=await IBK.get_categories_keyboard())
        

    async def category_callback(self, call: CallbackQuery, state: FSMContext):
        await call.answer(' ')
        await state.clear()
        category = call.data.split("_", 1)[1]  

        await state.update_data(category=category)

        animation = await self.send_media('catalogue.gif', self.catalogue_id)
        await call.message.edit_media(media=InputMediaAnimation(media=animation, 
                                            caption='🌟 <b>Выбери тип:</b>'),
                                            reply_markup=await IBK.select_type())

        await state.set_state(NumProx.type)


    async def type_callback(self, call: CallbackQuery, state: FSMContext):
        await call.answer()
        await state.update_data(type=call.data)
        data = await state.get_data()
        category = data.get('category')
        if category == 'ipv4':
            buttons = await IBK.select_country_proxy(ipv4)
        else:
            buttons = await IBK.select_country_proxy(ipv6)
        animation = await self.send_media('catalogue.gif', self.catalogue_id)
        await call.message.edit_media(media=InputMediaAnimation(media=animation, 
                                            caption='🌍 <b>Выбери страну:</b>'),
                                            reply_markup=buttons)

        await state.set_state(NumProx.country)

    async def select_country(self, call: CallbackQuery, state: FSMContext, callback_data: CallbackDataProxyCountry):

        data = await state.get_data()
        category = data.get('category')
        type = data.get('type')
        proxy_inf = proxy_info.get(f'{category} - {type}')
    
        await call.answer()
        await state.update_data(country=callback_data.country)

        animation = await self.send_media('catalogue.gif', self.catalogue_id)
        await call.message.edit_media(media=InputMediaAnimation(media=animation, caption=proxy_inf), reply_markup=await IBK.accept())

        await state.set_state(NumProx.await_accept)


    async def accept_handler(self, call: CallbackQuery, state: FSMContext):
        await call.answer()
        
        animation = await self.send_media('catalogue.gif', self.catalogue_id)
        await call.message.edit_media(media=InputMediaAnimation(media=animation, caption='🎲 <b>Выбери количество:</b>'), reply_markup=await IBK.amount_proxy())
        await state.set_state(NumProx.number)

    async def write_amount_proxy(self, call: CallbackQuery, state: FSMContext):
        await call.answer(' ')
        await call.message.answer('✍️ <b>Напиши, сколько хочешь купить:</b>')
        await state.set_state(NumProx.number)


    async def handle_number(self, m: Message, state: FSMContext):
        if not m.text.isdigit():
            await m.answer("⚠️ <b>Нужно ввести именно число!</b>")
            return
        await state.update_data(requested_count=int(m.text))
        
        await m.answer('Выбирете период: ', reply_markup=await IBK.select_period())



    async def select_amount_proxy(self, call: CallbackQuery, callback_data: CallbackDataProxy, state: FSMContext, user):
        await call.answer()
        requested_count = callback_data.amount
        await state.update_data(requested_count=requested_count)

        animation = await self.send_media('catalogue.gif', self.catalogue_id)
        await call.message.edit_media(media=InputMediaAnimation(media=animation, caption='🗓 <b>Выбери период:</b>'), reply_markup=await IBK.select_period())


    async def get_proxy_count(self, country_code, version: int):
        url = f"https://px6.link/api/{self.api_key}/getcount?country={country_code}&version={version}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    data = await resp.json()
                    if data.get("status") == "yes":
                        return data.get("count", 0)
                    else:
                        print(f"Ошибка при запросе для {country_code}: {data}")
                        return 0
        except Exception as e:
            print(f"Ошибка при запросе для {country_code}: {e}")
            return 0


    async def select_period(self, call: CallbackQuery, callback_data: CallbackDataSelectPeriod, state: FSMContext, user):
        data = await state.get_data()
        country = data.get('country')
        category = data.get("category")
        requested_count = data.get('requested_count')
        count = await self.get_proxy_count(country_code=country, version=(4 if category == 'ipv4' else 6))
        if requested_count > count:
            await call.answer(f'Для странны, которую вы выбрали доступно {count} прокси, вы выбрали {requested_count}‼️', show_alert=True)
            await state.clear()
            return

        await call.answer()
        period = callback_data.period
        await state.update_data(period=period)
        data = await state.get_data()
        
        
        

        await self.create_order_proces(category=category, country=country, type=type, requested_count=requested_count, user=user, state=state, m=call, period=period)


    async def get_price(self, api_key: str, count: int, period: int, version: int = 6) -> dict:
        url = f"https://px6.link/api/{api_key}/getprice"
        params = {
            "count": count,
            "period": period,
            "version": version
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as resp:
                data = await resp.json()

        if data.get("status") != "yes":
            raise Exception(f"API error: {data}")

        return data
         


    async def create_order_proces(self, category: str, country: str, type: str, requested_count: int, user: User, state: FSMContext, m: Message | CallbackQuery, period: int):
        if isinstance(m, CallbackQuery):
            m = m.message

        version = 6 if category == 'ipv6' else 4
        result = await self.get_price(self.api_key, count=requested_count, period=period, version=version)
        await state.update_data(balance=float(result['balance']))
        try:
            await state.update_data(price=result['price'])

            if category == 'ipv6':
                country_name = next((k for k, v in ipv6.items() if v == country), None)
            else:
                country_name = next((k for k, v in ipv4.items() if v == country), None)
            animation = await self.send_media('catalogue.gif', self.catalogue_id)
            await m.edit_media(media=InputMediaAnimation(media=animation, caption="➖➖➖➖➖📝 <b>Ваш заказ:</b>➖➖➖➖➖\n\n"
                        f"📂 <b>Категория:</b> <code>{'IPv6' if category == 'ipv6' else 'IPv4'}</code>\n"
                        f"🏳️ <b>Страна:</b> <code>{country_name}</code>\n"
                        f"⚡️ <b>Количество:</b> <code>{requested_count}</code>\n"
                        f"⏳ <b>Срок:</b>  <code>{period} дней </code>\n"
                        f"💲 <b>Общая сумма:</b> <code>{(result['price'] * self.x_price):.2f}$</code>"), reply_markup=await IBK.confirm_order())

        except Exception as e:
            print(e)


    async def handler_confirm_order(self, call: CallbackQuery, state: FSMContext):
        data = await state.get_data()

        requested_count = data.get("requested_count")
        price = data.get("price")
        category = data.get("category")
        country = data.get("country")
        type = data.get('type')
        period = int(data.get('period'))
        admin_balance = data.get('balance')
        track_number = str(uuid.uuid4())[:8]
        steps = ""

        async for session in get_db():
            user = await self.db_manager.get_user(id=call.from_user.id)

            if user.balance < (price * self.x_price):
                await call.answer()
                await call.message.delete()
                await call.message.answer('Недостаточно средств ❌\n'
                                f'💲 *Цена заказа:* `{(price * self.x_price):.2f} $`\n'
                                f'💰 *Ваш баланс:* `{user.balance:.2f}` $', parse_mode="Markdown", reply_markup=await IBK.need_inc_balance())
                return

            logger.info(f"[{track_number}] Начало обработки заказа (user={call.from_user.id}, category={category})")

            

            if admin_balance < price:
                await call.answer('🔄 Повторите позже | Произошла ошибка оформления заказа | Обратитесь в поддержку', show_alert=True)
                await self.bot.send_message(chat_id=7431078179, text=f'Юзер {call.from_user.id} не смог осуществить платеж на {price * self.x_price}$ из за недостатка средств на вашем аккаунте proxy6.net. Пополните свой баланс в proxy6.net минимум на {price}')
                return

            await call.answer()
            await call.message.delete()
            order = Order(
                track_number=track_number,
                user_id=call.from_user.id,
                category=f"{category} - {type}",
                requested=requested_count,
                status="in_progress",
            )

            try:
                
                await self.db_manager.update_user(id=user.telegram_id, balance=((price * self.x_price) * -1))

                steps += f"|Списано {price * self.x_price}"

                order.status = "processing"
                order.steps = steps
                session.add(order)
                await session.commit()
                logger.info(f"[{track_number}] У юзера (user={call.from_user.id}) списано {price * self.x_price}$")

                result = await self.buy_proxy_async(
                    self.api_key,
                    count=requested_count,
                    period=period,     
                    country=country,
                    type_= type
                )

                await call.message.answer(f"✅ Заказ оформлен!\n"
                    f"🆔 Трек-номер: `{track_number}`\n"
                    f"📦 Номер заказа: `{result['order_id']}`\n\n"
                    "🔗 Список прокси:", parse_mode='Markdown')
                logger.info(f"[{track_number}] прокси отправлены (user={call.from_user.id})")
                
                for proxy_id, proxy_info in result["list"].items():
                    if category == 'ipv6':
                        country_name = next((k for k, v in ipv6.items() if v == country), None)
                    else:
                        country_name = next((k for k, v in ipv4.items() if v == country), None)
                    date_start = (datetime.strptime(proxy_info['date'], "%Y-%m-%d %H:%M:%S")).strftime("%Y-%m-%d %H:%M")
                    date_end = (datetime.strptime(proxy_info['date_end'], "%Y-%m-%d %H:%M:%S")).strftime("%Y-%m-%d %H:%M")
                    await call.message.answer(f'IP: {proxy_info['host']}\n'
                                            f'Login: {proxy_info['user']}\n'
                                            f'Password: {proxy_info['pass']}\n'
                                            f'Категория: {category} - {type}\n'
                                            f'Страна: {country_name}\n'
                                            f'Срок: {date_start} - {date_end}\n')
                    
                    await self.db_manager.create_proxy(proxy_id=int(proxy_id), user_id=call.from_user.id, ip=proxy_info['host'], login=proxy_info['user'], 
                                                       password=proxy_info['pass'], port=int(proxy_info['port']), category=category, type=type, country=country,
                                                       date=datetime.strptime(proxy_info['date'], "%Y-%m-%d %H:%M:%S"), 
                                                       date_end=datetime.strptime(proxy_info['date_end'], "%Y-%m-%d %H:%M:%S"))
                    await asyncio.sleep(0.3)
                    
                await call.message.answer('Спасибо за покупку!\nЧто бы посмотреть все свои купленые прокси, загляните в раздел "Мои прокси".', 
                                          parse_mode="Markdown", reply_markup=await IBK.back_on_main_page())
                logger.info(f"[{track_number}] прокси отправлены и сохранены в бд(user={call.from_user.id})")

                order.status = "succes"
                order.steps += "|Заказ успешно выполнен"
                session.add(order)
                await session.commit()
                logger.info(f"[{track_number}] заказ успешно оформлен (user={call.from_user.id})")

            except Exception as e:
                await session.rollback()
                logger.error(f"[{track_number}] Ошибка: {e}")
                order.status = "error"
                order.steps = steps + f"|Ошибка: {str(e)}"
                session.add(order)
                await session.commit()
                await call.message.answer(
                    f"❌ Ошибка при создании заказа.\n🆔 Трек-номер: `{track_number}`",
                    parse_mode="Markdown"
                )
            finally:
                await state.clear()

    async def buy_proxy_async(self, api_key: str,
                          count: int,
                          period: int,
                          country: str,
                          version: int = 6,
                          type_: str = "http",
                          descr: str | None = None,
                          auto_prolong: bool = False,
                          nokey: bool = False) -> dict:
        url = f"https://px6.link/api/{api_key}/buy"
        params = {
            "count": count,
            "period": period,
            "country": country,
            "version": version,
            "type": type_
        }
        if descr:
            params["descr"] = descr
        if auto_prolong:
            params["auto_prolong"] = ""
        if nokey:
            params["nokey"] = ""

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=20) as resp:
                resp.raise_for_status()
                data = await resp.json()

        if data.get("status") != "yes":
            raise Exception(f"API error: {data}")
        return data
    

    async def my_proxies(self, call: CallbackQuery):
        proxies = await self.db_manager.get_proxy(user_id=call.from_user.id)
        if not proxies:
            await call.answer('Вы еще не купили ни одного прокси ‼️', show_alert=True)
            return
        await call.answer()

        page = 1
        start = (page - 1) * 1
        end = start + 1
        page_proxies = proxies[start:end]

        animation = await self.send_media('profile.gif', self.profile_id)
        text = await self.format_proxies(page_proxies, len_page=len(proxies))
        for p in page_proxies:
            pid = p.proxy_id
            break

        await call.message.edit_media(
            media=InputMediaAnimation(
                media=animation,
                caption=text
            ),
            reply_markup=build_proxies_keyboard(page=page, total=len(proxies), proxy_id=pid)
        )

        

    async def format_proxies(self, proxies, page: int = 1, len_page: int = 1):
        text = f"🧑‍💻 <b>Ваши прокси:</b> {page}/{len_page}\n\n"
        for p in proxies:
            if p.category == 'ipv6':
                country_name = next((k for k, v in ipv6.items() if v == p.country), None)
            else:
                country_name = next((k for k, v in ipv4.items() if v == p.country), None)
            text += (
                "📡 <b>Информация о прокси</b>\n\n"
                f"🌐 <b>IP:</b> <code>{p.ip}</code>\n"
                f"👤 <b>Логин:</b> <code>{p.login}</code>\n"
                f"🔑 <b>Пароль:</b> <code>{p.password}</code>\n"
                f"☄️ <b>Порт:</b> <code>{p.port}</code>\n"
                f"🗂 <b>Категория:</b> {'IPv4' if p.category == 'ipv4' else 'IPv6'} | {'HTTPS' if p.type == 'http' else 'SOCKS5'}\n"
                f"📅 <b>Срок действия:</b> {p.date} ➝ {p.date_end}\n"
                f"🏳️ <b>Страна:</b> {country_name}\n"
            )

        return text
    

    async def get_my_proxies(self, call: CallbackQuery):
        proxies = await self.db_manager.get_proxy(user_id=call.from_user.id)

        await call.answer()
        file_content = ""
        for proxy in proxies:
            file_content += f"{proxy.ip}:{proxy.port}@{proxy.login}:{proxy.password}:{proxy.category}:{'https' if proxy.type == 'http' else 'socks5'}\n"

        file = BufferedInputFile(file_content.encode("utf-8"), filename="my_proxies.txt")

        await call.message.delete()
        await call.message.answer_document(file, caption="📂 Ваш список прокси", reply_markup=await IBK.back_on_profile())


    async def proxies_page_handler(self, callback: CallbackQuery, callback_data: ProxiesPage):
        page = callback_data.page
        proxies = await self.db_manager.get_proxy(user_id=callback.from_user.id)
        animation = await self.send_media('profile.gif', self.profile_id)

        start = (page - 1) * 1
        end = start + 1
        page_proxies = proxies[start:end]
        page_proxy = page_proxies[0] if page_proxies else None

        text = await self.format_proxies(page_proxies, page=page, len_page=len(proxies))
        await callback.message.edit_media(media=InputMediaAnimation(media=animation, caption=text), reply_markup=build_proxies_keyboard(page, len(proxies), proxy_id=page_proxy.proxy_id if page_proxy else None))
        await callback.answer()


    async def prolong(self, call: CallbackQuery, callback_data: ProlongProxy, state: FSMContext):
        await call.answer()
        proxy_id = callback_data.proxy_id
        await state.update_data(proxy_id=proxy_id)
        proxy = await self.db_manager.get_proxy(proxy_id=proxy_id)
        animation = await self.send_media('catalogue.gif', self.catalogue_id)
        await call.message.edit_media(media=InputMediaAnimation(media=animation, 
                                                                caption=f'🌐 <b>Продление прокси:</b> {proxy.ip}\n🕐 <b>Срок окончания прокси:</b> <code>{proxy.date_end}</code>\n\n<b>📆 Выберите период для продления:</b> '), 
                                                                reply_markup=await IBK.period_prolong())
        await state.set_state(Prolong.period)

    async def prolong_period(self, call: CallbackQuery, callback_data: CallbackDataSelectPeriod, state: FSMContext):
        await call.answer()
        data = await state.get_data()
        proxy_id = data.get('proxy_id')
        period = callback_data.period
        await state.update_data(period=period)
        proxy = await self.db_manager.get_proxy(proxy_id=proxy_id)
        res = await self.get_price(api_key=self.api_key, count=1, period=period, version=(6 if proxy.category == 'ipv6' else 4))

        if float(res['price']) > float(res['balance']):
            await call.answer('🔄 Повторите позже | Произошла ошибка оформления заказа | Обратитесь в поддержку', show_alert=True)
            await self.bot.send_message(chat_id=7431078179, text=f'Юзер {call.from_user.id} не смог осуществить платеж на {res['price'] * self.x_price}$ из за недостатка средств на вашем аккаунте proxy6.net. Пополните свой баланс минимум на {res['price']}')
            return
        
        await state.update_data(price=res['price'])
        if proxy.category == 'ipv6':
            country_name = next((k for k, v in ipv6.items() if v == proxy.country), None)
        else:
            country_name = next((k for k, v in ipv4.items() if v == proxy.country), None)
        animation = await self.send_media('catalogue.gif', self.catalogue_id)
        await call.message.edit_media(media=InputMediaAnimation(media=animation, 
                                    caption=f"------------------------💲 <b>Цена {(res['price'] * self.x_price):.2f}$</b>------------------------\n\n"
                                    f"<b>Прокси для продления:</b>\n"
                                    f"🌐 <b>IP:</b> <code>{proxy.ip}</code>\n"
                                    f"👤 <b>Логин:</b> <code>{proxy.login}</code>\n"
                                    f"🔑 <b>Пароль:</b> <code>{proxy.password}</code>\n"
                                    f"☄️ <b>Порт:</b> <code>{proxy.port}</code>\n"
                                    f"🗂 <b>Категория:</b> {'IPv4' if proxy.category == 'ipv4' else 'IPv6'} | {'HTTPS' if proxy.type == 'http' else 'SOCKS5'}\n"
                                    f"📅 <b>Срок (до продления):</b> {proxy.date_end}\n"
                                    f"🗓️ <b>Срок (после продления):</b> {proxy.date_end} + {period} дней\n"
                                    f"🏳️ <b>Страна:</b> {country_name}\n"), 
                                    reply_markup=await IBK.accept_prolong())

        
    async def pay_prolong(self, call: CallbackQuery, state: FSMContext):
        data = await state.get_data()
        proxy_id = data.get('proxy_id')
        price = data.get('price')
        period = data.get('period')
        try:
            user = await self.db_manager.get_user(id=call.from_user.id)
            track_number = str(uuid.uuid4())[:8]
            logger.info(f"[{track_number}] Начало продления (user={call.from_user.id}, proxy_id={proxy_id}, period={period})")
            if price > user.balance:
                logger.warning(f"[{track_number}] Недостаточно средств (нужно={price * self.x_price}, баланс={user.balance * self.x_price})")
                await call.message.answer('Недостаточно средств ❌\n'
                                    f'💲 *Цена заказа:* `{(price * self.x_price):.2f}` $\n'
                                    f'💰 *Ваш баланс:* `{user.balance}` $', parse_mode="Markdown", reply_markup=await IBK.need_inc_balance())
                await state.clear()
                return
            
            await call.answer()
            result = await self.prolong_api(api_key=self.api_key, period=period, ids=proxy_id)
            logger.info(f"[{track_number}] Продление успешно (proxy_id={proxy_id})")

            await self.db_manager.update_user(id=call.from_user.id, balance=((price * self.x_price) * -1))
            logger.info(f"[{track_number}] Списано {price * self.x_price} с баланса user={call.from_user.id}")
            animation = await self.send_media('catalogue.gif', self.catalogue_id)
            await call.message.edit_media(media=InputMediaAnimation(media=animation, 
                                    caption=f'Прокси продлен на {period} дней ✅\n⏳ Новый срок прокси: {result['list'][str(proxy_id)]['date_end']}'), 
                                    reply_markup=await IBK.back_on_main_page())

            await self.db_manager.update_p(proxy_id=proxy_id, date_end=result['list'][str(proxy_id)]['date_end'])

            logger.info(f"[{track_number}] Продление завершено успешно")

        except Exception as e:
            logger.error(f"[{track_number}] Ошибка при продлении: {e}", exc_info=True)
            await call.message.answer(
                f"❌ Ошибка при продлении прокси.\n🆔 Трек-номер: `{track_number}`",
                parse_mode="Markdown"
            )

        finally:
            await state.clear()


    async def prolong_api(self, api_key: str,
                          period: int,
                          ids: int):
        url = f"https://px6.link/api/{api_key}/prolong"
        params = {
            "period": period,
            "ids": ids
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=20) as resp:
                resp.raise_for_status()
                data = await resp.json()

        if data.get("status") != "yes":
            raise Exception(f"API error: {data}")
        return data