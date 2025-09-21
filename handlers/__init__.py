
from .admin import Admin
from .payments import Payment
from .user import user_modules
from config import bot


async def reg_handlers(dp):
    admin = Admin(dp, bot=bot)
    payment = Payment(dp=dp, bot=bot)
    for module in user_modules:
        client = module(dp=dp, bot=bot)
        await client.reg_handler()



    await admin.reg_handler()
    await payment.reg_handler()

