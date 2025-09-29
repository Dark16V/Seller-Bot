from aiogram import Bot, Dispatcher, types
from aiogram.types import BufferedInputFile
from aiogram.filters import Command
from aiogram import F
import asyncio

TOKEN = "8375687840:AAGYL4HcxkVP2HYTlz3sMjh6g8YafJQslgM"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("photo"))
async def send_photo(message: types.Message):
    # Представим, что у тебя есть картинка в байтах
    with open("media/menu_test.mp4", "rb") as f:
        img_bytes = f.read()

    # Заворачиваем в BufferedInputFile
    media = BufferedInputFile(img_bytes, filename="test.mp4")

    # Отправляем как фото
    await message.answer_animation(media, caption="Media из байтов 📸")

@dp.message(Command("doc"))
async def send_doc(message: types.Message):
    # Пример с документом (PDF)
    with open("test.pdf", "rb") as f:
        pdf_bytes = f.read()

    document = BufferedInputFile(pdf_bytes, filename="file.pdf")

    await message.answer_document(document, caption="Документ из байтов 📑")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
