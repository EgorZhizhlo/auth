from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncSession,
)

from config.settings import settings  # SECRET, URL и т.п.

# Асинхронный движок
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,                        # DEBUG-вывод SQL
    connect_args={
        "server_settings": {
            "timezone": "Europe/Moscow",
        }
    },
)

# Фабрика сессий
async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False,
)

# Зависимость FastAPI


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
