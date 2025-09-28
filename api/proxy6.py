import aiohttp
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()


class ProxyS:
    def __init__(self):
        self.api_key = os.getenv("API_KEY")


    async def get_proxy_count(self, country_code, version: int):
        url = f"https://px6.link/api/{self.api_key}/getcount?country={country_code}&version={version}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    data = await resp.json()
                    if data.get("status") == "yes":
                        return data.get("count", 0)
                    else:
                        print(f"Ошибка при запросе для {country_code}: {data}")
                        return 0
        except Exception as e:
            print(f"Ошибка при запросе для {country_code}: {e}")
            return 0
        

    async def get_price(self, api_key: str, count: int, period: int, version: int = 6) -> dict:
        url = f"https://px6.link/api/{api_key}/getprice"
        params = {
            "count": count,
            "period": period,
            "version": version
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=10) as resp:
                data = await resp.json()

        if data.get("status") != "yes":
            raise Exception(f"API error: {data}")

        return data
    

    async def buy_proxy(self, api_key: str,
                          count: int,
                          period: int,
                          country: str,
                          version: int = 6,
                          type_: str = "http",
                          descr: str | None = None,
                          auto_prolong: bool = False,
                          nokey: bool = False) -> dict:
        url = f"https://px6.link/api/{api_key}/buy"
        params = {
            "count": count,
            "period": period,
            "country": country,
            "version": version,
            "type": type_
        }
        if descr:
            params["descr"] = descr
        if auto_prolong:
            params["auto_prolong"] = ""
        if nokey:
            params["nokey"] = ""

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=20) as resp:
                resp.raise_for_status()
                data = await resp.json()

        if data.get("status") != "yes":
            raise Exception(f"API error: {data}")
        return data
    

    async def prolong(self, api_key: str,
                          period: int,
                          ids: int):
        url = f"https://px6.link/api/{api_key}/prolong"
        params = {
            "period": period,
            "ids": ids
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=20) as resp:
                resp.raise_for_status()
                data = await resp.json()

        if data.get("status") != "yes":
            raise Exception(f"API error: {data}")
        return data