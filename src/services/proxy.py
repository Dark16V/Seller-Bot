from sqlalchemy.future import select
from src.models.proxy import Proxy
from datetime import datetime


class ProxyManager():
    def __init__(self, session_maker):
        self.session = session_maker

    async def get_proxy(self, proxy_id: int = None, ip: int = None, user_id: int = None, category: str = None, type: str = None, country: str = None, on_sale: bool = None):
        async with self.session() as s:
            if ip:
                return (await s.execute(select(Proxy).where(Proxy.ip == ip))).scalar_one_or_none()
            if proxy_id:
                return (await s.execute(select(Proxy).where(Proxy.proxy_id == proxy_id))).scalar_one_or_none()
            proxy = select(Proxy)
            if user_id:
                proxy = proxy.where(Proxy.user_id == user_id)
            if category:
                proxy = proxy.where(Proxy.category == category)
            if type:
                proxy = proxy.where(Proxy.type == type)
            if country:
                proxy = proxy.where(Proxy.country == country)
            if on_sale == False or on_sale == True:
                proxy = proxy.where(Proxy.on_sale == on_sale)
           
            return (await s.execute(proxy)).scalars().all()

        

    async def delete_proxy(self, ip: int = None):
        async with self.session() as s:
            proxy = await s.execute(select(Proxy).where(Proxy.ip == ip)).scalar_one_or_none()
            if not proxy: return False
            await s.delete(proxy)
            await s.commit()
            return True
        

    async def create_proxy(self, user_id: int, ip: str, login: str, password: str, port: int, category: str, type: str, country: str, date, date_end, proxy_id: int = None):
        async with self.session() as s:
            if not (await s.execute(select(Proxy).where(Proxy.ip == ip))).scalar_one_or_none():
                proxy = Proxy(
                    proxy_id=proxy_id,
                    user_id=user_id,
                    ip=ip,
                    login=login,
                    password=password,
                    port=port,
                    category=category,
                    type=type,
                    country=country,
                    date=date,
                    date_end=date_end
                )
                s.add(proxy)
                await s.commit()


    async def update_p(self, proxy_id: int, date_end):
        async with self.session() as s:
            proxy = (await s.execute(select(Proxy).where(Proxy.proxy_id == proxy_id))).scalar_one_or_none()
            proxy.date_end = datetime.strptime(date_end, '%Y-%m-%d %H:%M:%S')
            await s.commit()

    

