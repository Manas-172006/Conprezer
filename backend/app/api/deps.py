from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.db.models import User
from app.db.session import get_db
from app.core.security import verify_jwt


def get_current_user(
    request: Request, db: Session = Depends(get_db)
) -> User:
    subject = verify_jwt(request.cookies.get("access_token", ""))
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sign in to continue",
        )
    user = db.get(User, int(subject))
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    return user
