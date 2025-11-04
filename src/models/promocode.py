from sqlalchemy import BigInteger, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Base
from datetime import datetime


class PromoCode(Base):
    __tablename__ = "promocodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    discount: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    exspired_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    usage_limit: Mapped[int] = mapped_column(Integer, nullable=True)
    used_count: Mapped[int] = mapped_column(Integer, default=0)



class UsedPromoCode(Base):
    __tablename__ = "used_promocodes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    discount: Mapped[int] = mapped_column(Integer, nullable=False)

    code_id: Mapped[int] = mapped_column(Integer,ForeignKey("promocodes.id", ondelete="CASCADE"),nullable=False)

    exspired_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)

