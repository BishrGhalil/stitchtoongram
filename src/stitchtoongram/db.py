from datetime import datetime
from datetime import timedelta
from typing import Optional

from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import create_engine
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker

from .const import DB_NAME


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(name="id", primary_key=True)
    telegram_id: Mapped[int] = mapped_column(
        name="telegram_id", type_=BigInteger, unique=True
    )
    username: Mapped[str] = mapped_column(
        name="username", type_=String(255), nullable=True
    )
    full_name: Mapped[Optional[str]] = mapped_column(
        name="full_name", type_=String(255)
    )
    points: Mapped[int] = mapped_column(name="points", type_=Integer, default=0)
    is_admin: Mapped[bool] = mapped_column(
        name="is_admin", type_=Boolean, default=False
    )
    is_blocked: Mapped[bool] = mapped_column(
        name="is_blocked", type_=Boolean, default=False
    )
    is_requesting: Mapped[bool] = mapped_column(
        name="is_requesting", type_=Boolean, default=False
    )
    is_registered: Mapped[bool] = mapped_column(
        name="is_registered", type_=Boolean, default=False
    )
    opened_reports: Mapped[int] = mapped_column(
        name="opened_reports", type_=Integer, default=0
    )
    points_earned_at: Mapped["DateTime"] = mapped_column(
        name="points_earned_at", type_=DateTime, server_default=func.now()
    )
    created_at: Mapped["DateTime"] = mapped_column(
        name="created_at", type_=DateTime, server_default=func.now()
    )
    chat: Mapped["Chat"] = relationship("Chat", back_populates="user")

    def next_earning(self) -> timedelta:
        month_later = self.points_earned_at + timedelta(days=30)
        diff = month_later - datetime.now()

        return diff if diff.days >= 0 else timedelta(days=0)

    def add_points(self, points):
        self.points += points
        self.points_earned_at = datetime.now()

    def can_earn(self) -> bool:
        if self.next_earning() <= timedelta(days=0):
            return True
        return False

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, telegram_id={self.telegram_id!r}, username={self.username!r}, full_name={self.full_name!r}, points={self.points!r}, is_admin={self.is_admin!r}, is_blocked={self.is_blocked!r}, is_requesting={self.is_requesting!r}, points_earned_at={self.points_earned_at!r}, created_at={self.created_at!r})"


class Option(Base):
    __tablename__ = "options"
    name: Mapped[str] = mapped_column(
        name="name", type_=String(255), unique=True, primary_key=True
    )
    value: Mapped[str] = mapped_column(name="value", type_=String(255))
    data_type: Mapped[str] = mapped_column(name="data_type", type_=String(255))

    def __repr__(self) -> str:
        return f"Options(id={self.id!r}, name={self.name!r}, value={self.value!r}, data_type={self.data_type!r})"


class Chat(Base):
    __tablename__ = "chats"
    id: Mapped[int] = mapped_column(name="id", primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    chat_id: Mapped[int] = mapped_column(
        name="telegram_id", type_=BigInteger, unique=True, index=True
    )
    user: Mapped["User"] = relationship("User", back_populates="chat")

    def __repr__(self) -> str:
        return (
            f"Chat(id={self.id!r}, chat_id={self.chat_id!r}, user_id={self.user_id!r})"
        )


engine = create_engine(f"sqlite+pysqlite:///{DB_NAME}", echo=False)
Base.metadata.create_all(engine)
session = sessionmaker(bind=engine)()
