from sqlalchemy import BigInteger, Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column
from db import Base
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    balance: Mapped[float] = mapped_column(default=0.0)
    is_baned: Mapped[bool] = mapped_column(Boolean, default=False)
    reg_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
   


