from sqlalchemy import Integer, String, Boolean, BigInteger, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from db import Base

class Proxy(Base):
    __tablename__ = "proxies"

    id: Mapped[int] = mapped_column(primary_key=True)
    proxy_id: Mapped[int] = mapped_column(Integer, unique=True)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    ip: Mapped[str] = mapped_column(String(64))
    login: Mapped[int] = mapped_column(String)
    password: Mapped[int] = mapped_column(String)
    port: Mapped[int] = mapped_column(Integer)
    category: Mapped[str] = mapped_column(String)
    type: Mapped[int] = mapped_column(String)
    country: Mapped[str] = mapped_column(String)
    date: Mapped[DateTime] = mapped_column(DateTime)
    date_end: Mapped[DateTime] = mapped_column(DateTime)



