from sqlalchemy.future import select
from models.user import User


class UserManager():
    def __init__(self, session_maker):
        self.session = session_maker

    async def get_user(self, id: int | str = None, is_baned: bool = None):
        async with self.session() as s:
            if id == 'all':
                return (await s.execute(select(User))).scalars().all()
            if id:
                return (await s.execute(select(User).where(User.telegram_id == id))).scalar_one_or_none()
            if is_baned == False or is_baned == True:
                return (await s.execute(select(User).where(User.is_baned == is_baned))).scalars().all()
            

    async def update_user(self, id: int, balance: int = None, is_baned: bool = None, order_id: str = None):
        async with self.session() as s:
            if balance:
                user = (await s.execute(select(User).where(User.telegram_id == id))).scalar_one_or_none()
                user.balance += balance

            if is_baned == True or is_baned == False:
                user = (await s.execute(select(User).where(User.telegram_id == id))).scalar_one_or_none()
                user.is_baned = is_baned

            if order_id:
                user = (await s.execute(select(User).where(User.telegram_id == id))).scalar_one_or_none()
                user.proxy_orders_id += f'|{order_id}'
            await s.commit()