"""FastAPI Dependencies — Auth & Tenant resolution"""

import uuid
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.database import get_db
from app.models.tenant import Tenant

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_tenant(
    db: Annotated[AsyncSession, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Security(bearer_scheme)] = None,
    x_api_key: Annotated[str | None, Header(alias="X-API-Key")] = None,
) -> Tenant:
    """
    Resolve the current Tenant from either:
      - Bearer JWT token (Authorization: Bearer <token>)
      - API key header    (X-API-Key: <key>)
    """
    tenant: Tenant | None = None

    # ── API Key auth ──────────────────────────────────────────────────────
    if x_api_key:
        result = await db.execute(select(Tenant).where(Tenant.api_key == x_api_key, Tenant.is_active == True))
        tenant = result.scalar_one_or_none()

    # ── JWT auth ──────────────────────────────────────────────────────────
    elif credentials:
        try:
            payload = decode_access_token(credentials.credentials)
            tenant_id: str = payload.get("sub")
            if not tenant_id:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
            result = await db.execute(
                select(Tenant).where(Tenant.id == uuid.UUID(tenant_id), Tenant.is_active == True)
            )
            tenant = result.scalar_one_or_none()
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token is invalid or expired")

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return tenant


CurrentTenant = Annotated[Tenant, Depends(get_current_tenant)]
DB = Annotated[AsyncSession, Depends(get_db)]
