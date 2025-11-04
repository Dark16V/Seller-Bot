
from .admin import Admin
from .payments import Payment
from .user import user_modules


async def reg_handlers(config):
    admin = Admin(config=config)
    payment = Payment(config=config)
    for module in user_modules:
        client = module(config=config)
        await client.reg_handler()



    await admin.reg_handler()
    await payment.reg_handler()

