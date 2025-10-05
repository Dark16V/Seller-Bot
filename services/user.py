from sqlalchemy import select, update, func, desc
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
            user = (
                await s.execute(select(User).where(User.telegram_id == id))
            ).scalar_one_or_none()

            if not user:
                return None

            if balance:
                user.balance += balance

                if user.referral_uid:
                    referral = (
                        await s.execute(
                            select(User).where(User.telegram_id == user.referral_uid)
                        )
                    ).scalar_one_or_none()

                    if referral:
                        referral.balance += (balance * 5) / 100

            if is_baned is not None:
                user.is_baned = is_baned

            if order_id:
                if not user.proxy_orders_id:
                    user.proxy_orders_id = order_id
                else:
                    user.proxy_orders_id += f'|{order_id}'

            await s.commit()
            await s.refresh(user)
            return user
    

    async def get_user_count_ref(self, uid: int):
        async with self.session() as s:
            return (await s.execute(select(func.count(User.telegram_id)).where(User.referral_uid == uid))).scalar_one() or 0