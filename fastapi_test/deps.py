from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import jwt
from jwt.exceptions import PyJWTError
from datetime import datetime, timedelta, timezone

from . import database, crud, schemas, config


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    token = jwt.encode(
        to_encode, config.settings.SECRET_KEY, algorithm=config.settings.ALGORITHM
    )
    database.logger.debug(f"Access-Token erstellt für: {data.get('sub')}")
    return token


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)
) -> schemas.User:
    database.logger.debug(
        "Versuche, aktuellen Benutzer anhand des Tokens zu identifizieren"
    )
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, config.settings.SECRET_KEY, algorithms=[config.settings.ALGORITHM]
        )
        username: str = payload.get("sub")
        if username is None:
            database.logger.warning("Token enthält keinen Benutzernamen (sub)")
            raise credentials_exception
    except PyJWTError as e:
        database.logger.error(f"Token-Validierung fehlgeschlagen: {e}")
        raise credentials_exception

    user = crud.get_user_by_username(db, username)
    if user is None:
        database.logger.warning(f"Benutzer nicht gefunden: {username}")
        raise credentials_exception

    database.logger.info(f"Benutzer erfolgreich authentifiziert: {username}")
    return user


def get_current_active_user(
    current_user: schemas.User = Depends(get_current_user),
) -> schemas.User:
    if current_user.disabled:
        database.logger.warning(f"Benutzer ist deaktiviert: {current_user.username}")
        raise HTTPException(status_code=400, detail="Inactive user")
    database.logger.debug(f"Aktiver Benutzer: {current_user.username}")
    return current_user
