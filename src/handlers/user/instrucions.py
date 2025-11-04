from aiogram.types import CallbackQuery, InputMediaAnimation
from aiogram import F

from src.keyboards import IBK
from src.keyboards.callbackdata import *

from src.utils.utils import get_media


class InstructionsClient():
    def __init__(self, config):
        self.dp = config.dp
        self.bot = config.bot


    async def reg_handler(self):
        self.dp.callback_query(F.data == 'instr')(self.instr)
        self.dp.callback_query(F.data == 'ios')(self.instr_ios)
        self.dp.callback_query(F.data == 'con_ios')(self.con_ios)
        self.dp.callback_query(F.data == 'android')(self.instr_android)
        self.dp.callback_query(F.data == 'con_andr')(self.con_andr)
        self.dp.callback_query(F.data == 'winda')(self.instr_win)



    async def instr(self, call: CallbackQuery):
        await call.answer()
        animation = await get_media('catalog')
        await call.message.edit_media(media=InputMediaAnimation(media=animation, 
                                            caption=f"Выберите платформу: "),
                                            reply_markup=await IBK.select_type_instr())

    
    async def instr_ios(self, call: CallbackQuery):
        await call.answer('')
        await call.message.answer('🍏 ИНСТРУКЦИЯ ПОД IOS\n\n☑️ Скачиваем приложение <a href="https://apps.apple.com/ru/app/v2raytun/id6476628951">v2RayTun</a> в App Store. '
                                '(нажмите на название что бы перейти к приложению)',
                                  disable_web_page_preview=True)
        image_id = 'AgACAgIAAxkBAAIDG2jLne6JwE0CnhjVzDcYyVxvbGrgAALrAjIbRINYShbjX0DqTlwlAQADAgADeQADNgQ'
        await call.message.answer_photo(photo=image_id, caption='После этого вернитесь в данный бот, для следующих шагов.\n\nПродолжить?', reply_markup=await IBK.con_ios())
        await call.message.delete()


    async def con_ios(self, call: CallbackQuery):
        await call.answer()
        image_id = 'AgACAgIAAxkBAAIDHWjLn1AjcHGTXM8ysZ8Uy1jagPIzAALyAjIbRINYSqudi_a_iFoqAQADAgADeQADNgQ'
        await call.message.answer('☑️ Откройте v2RayTun и нажмите плюс ➕ (вверху справа), затем выберите: Добавить из буфера или Ввести вручную.')
        await call.message.answer_photo(photo=image_id, caption='Вставьте скопированый вами ключ который вы преобрели в нашем боте.\n\n' \
        '✅ Готово! Теперь можно запустить ВПН-сервис, нажав на большую кнопку вверху ⏻\n\n' \
        'Если позникли вопросы, обращайтесь в "Тех Поддержка".', reply_markup=await IBK.back_on_vpn())
        await call.message.delete()


    async def instr_android(self, call: CallbackQuery):
        await call.answer('')
        await call.message.answer('🤖 ИНСТРУКЦИЯ ПОД ANDROID\n\n' \
        '☑️ Первым делом необходимо скачать приложение <a href="https://play.google.com/store/apps/details?id=com.v2raytun.android">v2rayTun</a> из Google Play. '
        '(нажмите на название что бы перейти к приложению)',
        disable_web_page_preview=True)
        image_id = 'AgACAgIAAxkBAAIDH2jLojR3_tAbGFl9h4uf6tn3CDAFAAIHAzIbRINYSqADgnAEWa5VAQADAgADeAADNgQ'
        await call.message.answer_photo(photo=image_id, caption='После этого вернитесь в данный бот, для следующих шагов.\n\nПродолжить?', reply_markup=await IBK.con_andr())
        await call.message.delete()


    async def con_andr(self, call: CallbackQuery):
        await call.answer()
        image_id1 = 'AgACAgIAAxkBAAIDIWjLozfsNePpemu3ndu01wjjWbd8AAIVAzIbRINYSkV7b4CD-mDzAQADAgADeAADNgQ'
        await call.message.answer_photo(photo=image_id1, caption='☑️ Откройте v2RayTun и нажмите плюс ➕ (вверху справа).')
        image_id2 = 'AgACAgIAAxkBAAIDI2jLozwIdXDuUYgrFIGkdxh4KyUqAAIWAzIbRINYSqNLX2fW4c0ZAQADAgADeAADNgQ'
        await call.message.answer_photo(photo=image_id2, caption='Затем выберите: Импорт из буфера обмена или Ручной ввод.\n' 
        'Вставьте скопированый вами ключ который вы преобрели в нашем боте.\n\n'
        '✅ Готово! Теперь можно запустить ВПН-сервис, нажав на большую кнопку вверху ⏻\n\n' \
        'Если позникли вопросы, обращайтесь в "Тех Поддержка".', reply_markup=await IBK.back_on_vpn())
        await call.message.delete()

    
    async def instr_win(self, call: CallbackQuery):
        await call.answer()
        await call.message.answer('❖ ИНСТРУКЦИЯ ПОД WINDOWS\n\n'
                                  'Для подключения к моим серверам можно использовать разные программы. Например: NekoRay, Hiddify, V2rayN, Clash и другие.\n\n' \
                                  'Вот инструкции для двух из них: \n\n' \
                                  '<a href="https://teletype.in/@axo/karing_windows">☑️ Подключение через Karing</a>\n\n' \
                                  '<a href="https://teletype.in/@axo/hiddify-windows">☑️ Подключение через Hiddify</a>', disable_web_page_preview=True, reply_markup=await IBK.back_on_vpn())
        await call.message.delete()