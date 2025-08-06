from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.session import get_db
from app.repositories import EmployeeRepository
from app.models import RefreshTokenModel
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.time_utils import utc_now
from app.schemas import TokenPair

router = APIRouter(prefix="/auth", tags=["auth"])


def _unauth(detail: str = "Не авторизован") -> HTTPException:
    return HTTPException(status.HTTP_401_UNAUTHORIZED, detail=detail)


# ---------- /login ----------
class LoginIn(BaseModel):
    username: str
    password: str


@router.post("/login", response_model=TokenPair)
async def login(data: LoginIn, db: AsyncSession = Depends(get_db)):
    repo = EmployeeRepository(db)
    user = await repo.get_by_username(data.username)
    if not user or not verify_password(data.password, user.password):
        raise _unauth("Неверные имя пользователя или пароль")
    if not user.is_active:
        raise _unauth("Пользователь деактивирован")

    access = create_access_token(user.username)
    refresh, jti, exp_ts = create_refresh_token(user.username)

    db.add(
        RefreshTokenModel(
            jti=jti,
            employee_id=user.id,
            expires_at=datetime.fromtimestamp(exp_ts, tz=timezone.utc),
        )
    )
    await db.commit()
    return TokenPair(access_token=access, refresh_token=refresh)


# ---------- /refresh ----------
@router.post("/refresh", response_model=TokenPair)
async def refresh(
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise _unauth("Отсутствует заголовок Authorization")
    raw_token = authorization.split()[1]

    payload = decode_token(raw_token)
    if payload.get("type") != "refresh":
        raise _unauth("Ожидался refresh-токен")

    token_row: RefreshTokenModel | None = await db.get(
        RefreshTokenModel, {"jti": payload["jti"]}
    )
    if not token_row or token_row.revoked or token_row.expires_at < utc_now():
        raise _unauth("Refresh-токен отозван или истёк")

    token_row.revoked = True  # отзываем старый

    access = create_access_token(payload["sub"])
    new_refresh, jti, exp_ts = create_refresh_token(payload["sub"])
    db.add(
        RefreshTokenModel(
            jti=jti,
            employee_id=token_row.employee_id,
            expires_at=datetime.fromtimestamp(exp_ts, tz=timezone.utc),
        )
    )
    await db.commit()
    return TokenPair(access_token=access, refresh_token=new_refresh)


# ---------- /logout ----------
@router.post("/logout", status_code=204)
async def logout(
    authorization: str | None = Header(None),
    db: AsyncSession = Depends(get_db),
):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise _unauth("Отсутствует заголовок Authorization")
    raw_token = authorization.split()[1]

    try:
        payload = decode_token(raw_token)
    except Exception:
        raise _unauth("Неверный токен")

    if payload["type"] == "refresh":  # пришли с refresh-токеном
        await db.execute(
            RefreshTokenModel.__table__.update()
            .where(RefreshTokenModel.jti == payload["jti"])
            .values(revoked=True)
        )
    else:  # отзываем все refresh-токены пользователя
        await db.execute(
            RefreshTokenModel.__table__.update()
            .where(RefreshTokenModel.employee_id == payload["sub"])
            .values(revoked=True)
        )
    await db.commit()
