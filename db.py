from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from aiogram.types import BufferedInputFile
import os
import subprocess

import datetime
from dotenv import load_dotenv
import asyncio

load_dotenv()

DATABASE_URL = f"postgresql+asyncpg://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"

engine = create_async_engine(DATABASE_URL) 

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db():
    async with async_session() as session:
        yield session

class Base(DeclarativeBase):
    pass 


async def backup_database(bot):
    time = datetime.datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"backup_{time}.dump"

    os.environ["PGPASSWORD"] = os.getenv("DB_PASSWORD")

    # PG_DUMP_PATH = r"D:\\PostgreSQL\\17\\bin\\pg_dump.exe"

    cmd = [
        "pg_dump",
        "-h", os.getenv("DB_HOST"),
        "-p", os.getenv("DB_PORT"),
        "-U", os.getenv("DB_USER"),
        "-F", "c", os.getenv("DB_NAME"),
    ]

    try:
        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        output, error = process.communicate()

        if process.returncode != 0:
            print(f"❌ error backup: {error.decode()}")
            return

        input_file = BufferedInputFile(output, filename=filename)

        await bot.send_document(
            chat_id=os.getenv("BACKUP_CID"),
            document=input_file,
            caption="Бэкап базы данных за " + time
        )

        print(f"✅ Backup sent: {filename}")

    except Exception as e:
        print(f"Error: {e}")


async def backup_task(bot):
    while True:
        wait_time = 7 * 24 * 60 * 60
        await backup_database(bot)
        await asyncio.sleep(wait_time)