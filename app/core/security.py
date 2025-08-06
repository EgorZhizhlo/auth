from datetime import timedelta
import uuid
from typing import Tuple, Dict

from jose import jwt, JWTError
from passlib.context import CryptContext

from config.settings import settings
from core.time_utils import utc_now

# ── крипто-настройки ────────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


# ── JWT ─────────────────────────────────────────────────────────
def _create_jwt_token(
    *, subject: str, token_type: str, expires_delta: timedelta
) -> Tuple[str, str, int]:
    """
    Генерирует JWT и возвращает (token, jti, exp_timestamp).
    `token_type` — 'access' или 'refresh'.
    """
    expire = utc_now() + expires_delta
    jti = str(uuid.uuid4())
    payload: Dict[str, str | int] = {
        "sub": subject,
        "type": token_type,
        "jti": jti,
        "exp": expire,
    }
    token = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return token, jti, int(expire.timestamp())


def create_access_token(username: str) -> str:
    token, _, _ = _create_jwt_token(
        subject=username,
        token_type="access",
        expires_delta=timedelta(minutes=settings.ACCESS_EXPIRE_MIN),
    )
    return token


def create_refresh_token(username: str) -> Tuple[str, str, int]:
    """
    Возвращает tuple: (token, jti, exp_ts) — удобно, если нужно
    сохранить `jti` и время истечения в БД.
    """
    return _create_jwt_token(
        subject=username,
        token_type="refresh",
        expires_delta=timedelta(days=settings.REFRESH_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict:
    """
    Декодирует JWT, выбрасывает JWTError при невалидности / истечении.
    """
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError as exc:
        # вызывающая сторона решит, как ответить (401/403 и т. д.)
        raise exc
