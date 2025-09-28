import aiohttp
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()


class PS:
    def __init__(self):
        self.base_url = "https://proxysoxy.com/api"
        self.token = os.getenv("TOKEN_PS")
        self.headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }

    async def buy_product(self, count: int, item_id: int, promo_code: str = "", payment_system: str = "balance") -> dict:
        """Создание заказа"""
        url = f"{self.base_url}/order/create"
        data = {
            "paymentSystem": payment_system,
            "count": count,
            "itemId": item_id,
            "promoCode": promo_code
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=self.headers, json=data) as resp:
                result = await resp.json()
                return {"status": resp.status, "data": result}
            
    
    async def get_price(self, country: str, proxy_type: str) -> dict:
        """Получает цену продукта"""
        url = f"{self.base_url}/categories/all"

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()

        categories = data.get("categories", [])

        for cat in categories:
            country_names = [cat["name"].get("en", "").lower(), cat["name"].get("en", "").lower()]
            if country.lower() in country_names:
                for item in cat["items"]:
                    if item["name"].lower() == proxy_type.lower():
                        return {"price": cat["price"], "product_id": item["id"]}

        return {"error": "Страна или тип прокси не найдены"}
    

    import aiohttp

    import aiohttp

    async def download_proxy(self, order_id: int) -> list[dict]:
        format_type = 'login:password@ip:port'
        """Достаем прокси по айди заказа и возвращаем их в виде списка словарей"""
        url = f"{self.base_url}/order/{order_id}/download/{format_type}"

        async with aiohttp.ClientSession() as session:
            # Получаем ссылку на файл с прокси
            async with session.get(url, headers=self.headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
            
            # Скачиваем прокси по ссылке
            async with session.get(data['url']) as resp:
                resp.raise_for_status()
                text = await resp.text()

        proxies = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                creds, ip_port = line.split('@')
                login, password = creds.split(':')
                ip, port = ip_port.split(':')
                proxies.append({
                    "login": login,
                    "password": password,
                    "ip": ip,
                    "port": port
                })
            except ValueError:
                # Если строка не соответствует формату login:password@ip:port — пропускаем
                continue

        return proxies



from datetime import datetime, timedelta

            

async def main():
    ps = PS()

    date_start = datetime.now()
    print(date_start)
    # допустим, после покупки вернулся order_id = 123
    result = await ps.download_proxy(1526)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())




