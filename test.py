from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
import asyncio


BOT_TOKEN = "8452174279:AAF9Yh3nsn0Y71Rg2Rvj3FeqISP34YTmxrU"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# При добавлении в группу — приветствие с ID
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(f"👋 Привет! ID этого чата: `{message.chat.id}`", parse_mode="Markdown")

# Команда /id — выводит ID текущего чата
@dp.message(Command("id"))
async def get_id(message: types.Message):
    await message.answer(f"🆔 ID этого чата: `{message.chat.id}`", parse_mode="Markdown")

async def main():
    print("🤖 Бот запущен. Добавь его в группу и напиши /id")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
