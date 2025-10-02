from sqlalchemy.future import select
from models.promocode import PromoCode, UsedPromoCode
from datetime import datetime



class PromoCodeManager():
    def __init__(self, session_maker):
        self.session = session_maker

    async def get_promocode(self, code: str) -> PromoCode | None:
        async with self.session() as s:
            res = (await s.execute(select(PromoCode).where(PromoCode.code == code))).scalar_one_or_none()
            return res
        
    async def del_all(self, code: str) -> None:
        async with self.session() as s:
            promo = (await s.execute(select(PromoCode).where(PromoCode.code == code))).scalar_one_or_none()
            promos = (await s.execute(select(UsedPromoCode).where(UsedPromoCode.code_id == promo.id))).scalars().all()
            await s.delete(promo)
            for p in promos:
                if p:
                    await s.delete(p)
            await s.commit()

    async def use_promocode(self, user_id: int, promocode: PromoCode) -> UsedPromoCode:
        async with self.session() as s:
            used_code = UsedPromoCode(
                user_id=user_id,
                discount=promocode.discount,
                code_id=promocode.id,
                exspired_at=promocode.exspired_at
            )
            promo = (await s.execute(select(PromoCode).where(PromoCode.id == promocode.id))).scalar_one_or_none()
            promo.used_count += 1
            s.add(used_code)
            await s.commit()
            await s.refresh(used_code)
            return used_code
        
    async def create_promocode(self, code: str, discount: int, exspired_at: datetime = None, usage_limit: int = None) -> PromoCode:
        async with self.session() as s:
            new_code = PromoCode(
                code=code,
                discount=discount,
                exspired_at=exspired_at,
                usage_limit=usage_limit
            )
            s.add(new_code)
            await s.commit()
            await s.refresh(new_code)
            return new_code
        
    async def get_promo_users(self, user_id: int) -> tuple[UsedPromoCode | None, PromoCode | None]:
        async with self.session() as s:
            result = (await s.execute(select(UsedPromoCode).where(
                    (UsedPromoCode.user_id == user_id) & (UsedPromoCode.active == True)))).scalars().first()
            promo = (await s.execute(select(PromoCode).where(PromoCode.id == result.code_id))).scalar_one_or_none() if result else None
            if result and result.exspired_at < datetime.utcnow():
                await self.del_all(code=promo.code)
                await s.commit()
            return result, promo
        
    async def deactivate_promo_user(self, code_id: int) -> None:
        async with self.session() as s:
            promo = (await s.execute(select(UsedPromoCode).where(UsedPromoCode.code_id == code_id))).scalar_one_or_none()
            if promo:
                promo.active = False
                await s.commit()

    async def use_prmocode(self, user_id: int, code: str) -> UsedPromoCode | None:
        async with self.session() as s:
            promocode = (await s.execute(select(PromoCode).where(PromoCode.code == code))).scalar_one_or_none()
            if not promocode:
                return None
            promocode.used_count += 1
            used_code = UsedPromoCode(
                user_id=user_id,
                discount=promocode.discount,
                code_id=promocode.id,
                exspired_at=promocode.exspired_at
            )
            s.add(used_code)
            await s.commit()
            await s.refresh(used_code)
            return used_code
                
