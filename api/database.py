from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from config import get_config, BotConfig, DbConfig


# Аддресс Базы Данных берём из переменных окружения
db_config = get_config(DbConfig, "db")

# На продакшене echo обысно отключаю, что бы логи были чище
engine = create_async_engine(
        url=str(db_config.dsn), 
        echo=False)

SessionLocal = sessionmaker(autocommit=False, 
                            autoflush=False, 
                            bind=engine, 
                            class_=AsyncSession)


