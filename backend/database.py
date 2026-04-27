import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# Берем URL из окружения (Docker)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://admin:password@db:5432/job_db")

# Создаем движок
engine = create_async_engine(DATABASE_URL, echo=True)

# Фабрика сессий
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# Создаем Base ЗДЕСЬ. Все модели будут наследоваться от него.
Base = declarative_base()

# Зависимость для получения сессии в роутах
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session