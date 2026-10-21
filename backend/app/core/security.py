from dataclasses import dataclass
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import settings

bearer = HTTPBearer(auto_error=True)


@dataclass(frozen=True)
class CurrentUser:
    id: str
    email: str | None
    role: str          # 'patient' | 'doctor' | 'freelancer' | 'hospital_admin'
    raw: dict[str, Any]


def _decode(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
        ) from e


def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
) -> CurrentUser:
    payload = _decode(creds.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Token missing sub")

    # Supabase stores app role in user_metadata (we set it at signup)
    meta = payload.get("user_metadata", {}) or {}
    role = meta.get("role", "patient")

    return CurrentUser(id=user_id, email=payload.get("email"), role=role, raw=payload)
