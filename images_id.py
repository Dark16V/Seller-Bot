import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram import F

# Токен бота
API_TOKEN = "8375687840:AAGYL4HcxkVP2HYTlz3sMjh6g8YafJQslgM"

# Создаём бота и диспетчер
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# Обработчик команды /start
@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Привет! Отправь мне изображение, и я верну его ID.")


# Обработчик изображений
@dp.message(F.photo)
async def handle_photo(message: types.Message):
    photo_id = message.photo[-1].file_id
    await message.reply(f"ID изображения: {photo_id}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
