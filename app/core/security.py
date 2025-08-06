from datetime import timedelta
import uuid
from typing import Tuple, Dict

from jose import jwt, JWTError
from werkzeug.security import generate_password_hash, check_password_hash

from app.config.settings import settings
from app.core.time_utils import utc_now

# ── пароли ─────────────────────────────────────────────────────


def get_password_hash(password: str) -> str:
    """Создать хеш пароля (pbkdf2:sha256, соль внутри строки)."""
    return generate_password_hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Проверить пароль против сохранённого хеша."""
    return check_password_hash(hashed, plain)


# ── JWT ────────────────────────────────────────────────────────
def _create_jwt_token(
    *, subject: str, token_type: str, expires_delta: timedelta
) -> Tuple[str, str, int]:
    """
    Сгенерировать JWT и вернуть (token, jti, exp_timestamp).
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
    return _create_jwt_token(
        subject=username,
        token_type="access",
        expires_delta=timedelta(minutes=settings.ACCESS_EXPIRE_MIN),
    )[0]


def create_refresh_token(username: str) -> Tuple[str, str, int]:
    """Вернуть (token, jti, exp_ts) — удобно сохранять в БД."""
    return _create_jwt_token(
        subject=username,
        token_type="refresh",
        expires_delta=timedelta(days=settings.REFRESH_EXPIRE_DAYS),
    )


def decode_token(token: str) -> dict:
    """Декодировать JWT; при ошибке бросить JWTError."""
    try:
        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except JWTError as exc:
        raise exc
