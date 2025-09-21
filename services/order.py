from sqlalchemy.future import select
from models.order import Order


class OrderManager():
    def __init__(self, session_maker):
        self.session = session_maker

    async def get_order(self, user_id: int = None, status: str = None):
        async with self.session() as s:
            if status:
                return (await s.execute(select(Order).where(Order.status == status))).scalars().all()
            return (await s.execute(select(Order).where(Order.user_id == user_id))).scalars().all()
