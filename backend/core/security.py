from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from backend.database import get_db
from jose import jwt, JWTError
from backend.core.config import settings
# esquema de autenticación Bearer
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )

        usuario_id = int(payload["sub"])
        comercio_id = payload.get("comercio_id")

        if comercio_id is None:
            raise HTTPException(status_code=401, detail="Token sin comercio_id")

    except (JWTError, KeyError, ValueError):
        raise HTTPException(status_code=401, detail="Token inválido")

    return {
        "usuario_id": usuario_id,
        "comercio_id": comercio_id,
    }