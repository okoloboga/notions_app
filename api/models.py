from sqlalchemy import (Column, Integer, String, DateTime,
                        ForeignKey, Text, func)
from sqlalchemy.orm import (relationship, DeclarativeBase,
                            Mapped, mapped_column)
from datetime import datetime

from database import Base



class User(Base):
    """
    User model.

    Contains the following fields:
        - `id`: Unique identifier for the user.
        - `username`: Username chosen by the user.
        - `password`: Password for the user.
        - `created_at`: Timestamp of when the user was created.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)

    created_at: Mapped[datetime] = mapped_column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now()
            )


class Note(Base):
    """
    Note model.

    Contains the following fields:
        - `id`: Unique identifier for the note.
        - `title`: Title of the note.
        - `content`: Content of the note.
        - `tags`: Tags for the note.
        - `created_at`: Timestamp of when the note was created.
        - `updated_at`: Timestamp of when the note was last updated.
        - `owner_id`: Foreign key to the owner of the note.
        - `owner`: Relationship to the owner of the note.
    """
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

