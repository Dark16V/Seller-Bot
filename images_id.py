import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram import F

# Токен бота
API_TOKEN = "8452174279:AAF9Yh3nsn0Y71Rg2Rvj3FeqISP34YTmxrU"

# Создаём бота и диспетчер
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Привет! Отправь мне гифку/анимацию, и я верну её ID.")


# Обработчик анимаций (GIF)
@dp.message(F.animation)
async def handle_animation(message: types.Message):
    animation_id = message.animation.file_id
    await message.reply(f"ID анимации: {animation_id}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
