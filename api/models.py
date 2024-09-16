from sqlalchemy import (Column, Integer, String, DateTime,
                        ForeignKey, Text, func)
from sqlalchemy.orm import (relationship, DeclarativeBase,
                            Mapped, mapped_column)
from datetime import datetime

from database import Base


'''
Класс User содержит id пользователя = telegram_id
Имя пользователя и пароль, тия пользователя - уникально
'''
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

    created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now()
            )


'''
Класс Note содержит Id записи, Название, Содержание, Тэги, Дату создания и обновленя
Id пользователя создавшего запись
'''
class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    tags = Column(String, index=True)
    created_at: Mapped[datetime] = mapped_column(
                 DateTime(timezone=True),
                 nullable=False,
                 server_default=func.now()
                 )
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="notes", lazy='joined')

User.notes = relationship("Note", back_populates="owner", lazy='joined')

