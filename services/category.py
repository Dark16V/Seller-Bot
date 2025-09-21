from sqlalchemy.future import select
from models.category import Category

class CatManager():
    def __init__(self, session_maker):
        self.session = session_maker


    async def create_cat(self, name: str):
        async with self.session() as s:
            if not (await s.execute(select(Category).where(Category.name == name))).scalar_one_or_none():
                    s.add(Category(name=name))
                    await s.commit()

    async def get_cat(self, name: str = None):
         async with self.session() as s:
            if name:
                return (await s.execute(select(Category).where(Category.name == name))).scalar_one_or_none()
            return (await s.execute(select(Category))).scalars().all()