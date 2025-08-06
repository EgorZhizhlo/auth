from fastapi import FastAPI
from app.config.settings import settings
from app.infrastructure.db.session import engine
from app.infrastructure.db.base import Base

# важно: чтобы таблицы «увиделись», импортируем модели
from app.models import *  # noqa

# — FastAPI-приложение —
app = FastAPI(
    title="Token microservice",
    debug=settings.DEBUG,
)

# — стартап / шатдаун —


@app.on_event("startup")
async def startup() -> None:
    """В DEV-режиме создаём таблицы на лету."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def shutdown() -> None:
    await engine.dispose()

# — только auth-роутер —
from app.api.routers.v1 import auth  # noqa
app.include_router(auth.router, prefix="/api/v1")
