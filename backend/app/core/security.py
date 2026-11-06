from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.core.config import settings


def sign_jwt(subject: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    return jwt.encode(
        {"sub": subject, "exp": expires},
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def verify_jwt(token: str) -> str | None:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        subject = payload.get("sub")
        return subject if isinstance(subject, str) else None
    except JWTError:
        return None
