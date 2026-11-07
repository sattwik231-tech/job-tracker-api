from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.database import get_db
from app.models.user import User

bearer_scheme = HTTPBearer()

def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        db: Session = Depends(get_db),
) -> User:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate":"Bearer"},
    )

    try:
        payload = decode_access_token(credentials.credentials)
        subject = payload.get("sub")

        if subject is None:
            raise unauthorized

        user_id = int(subject)

    except(InvalidTokenError, ValueError, TypeError):
        raise unauthorized

    user = db.query(User).filter(User.id == user_id).first()

    if user is None:
        raise unauthorized

    return user