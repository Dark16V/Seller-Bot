from aiogram.filters import BaseFilter
from dotenv import load_dotenv
import os
import ast

load_dotenv

ADMINS = ast.literal_eval(os.getenv("ADMINS", "[]"))

class IsAdmin(BaseFilter):
    async def __call__(self, message):
        return message.from_user.id in ADMINS