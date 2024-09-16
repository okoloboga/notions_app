from sqlalchemy import (Column, Integer, String, DateTime,
                        ForeignKey, Text, func)
from sqlalchemy.orm import (relationship, DeclarativeBase,
                            Mapped, mapped_column)
from datetime import datetime


# Начальный класс, от которого наследуются остальные
class Base(DeclarativeBase):
    pass


'''
Класс User содержит id пользователя = telegram_id
Имя пользователя и пароль, тия пользователя - уникально
Дата регистрации пользователя и метод репрезентации данных при обращении к классу
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

    def __repr__(self) -> str:
        return f'[{self.id}] {username}'


'''
Класс Note содержит Id записи, Название, Содержание, Тэги, Дату создания и обновленя
Id пользователя создавшего запись
Метод репрезентации, возвращающий id, название и автора
'''
class Note(Base):
    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    tags = Column(String, index=True)
    created_at = Mapped[datetime] = mapped_column(
                 DateTime(timezone=True),
                 nullable=False,
                 server_default=func.now()
                 )
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="notes")

    def __repr__(self) -> str:
        return f'[{self.id}] "{title}" by {owner}'


User.notes = relationship("Note", back_populates="owner")

