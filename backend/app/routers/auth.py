"""Auth Router — register, login, profile management"""

import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select

from app.core.dependencies import DB, CurrentTenant
from app.core.security import create_access_token, hash_password, verify_password
from app.models.tenant import Tenant

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── Request / Response Schemas ─────────────────────────────────────────────

class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    slug: str = Field(..., min_length=2, max_length=80, pattern=r"^[a-z0-9\-]+$")
    email: EmailStr
    password: str = Field(..., min_length=8)
    company_name: Optional[str] = None
    timezone: str = "UTC"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    tenant_id: str
    tenant_name: str
    tenant_slug: str
    plan: str
    api_key: str


class TenantProfile(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    email: str
    plan: str
    api_key: str
    is_active: bool
    company_name: Optional[str] = None
    website: Optional[str] = None
    phone: Optional[str] = None
    timezone: str
    logo_url: Optional[str] = None
    created_at: str


class UpdateProfileRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=120)
    company_name: Optional[str] = Field(None, max_length=120)
    website: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=30)
    timezone: Optional[str] = Field(None, max_length=60)
    logo_url: Optional[str] = Field(None, max_length=512)


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)


# ── Routes ────────────────────────────────────────────────────────────────

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: DB):
    """Register a new tenant account."""
    existing = await db.execute(
        select(Tenant).where((Tenant.email == payload.email) | (Tenant.slug == payload.slug))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email or slug already registered")

    tenant = Tenant(
        name=payload.name,
        slug=payload.slug,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        api_key=uuid.uuid4().hex,
        company_name=payload.company_name,
        timezone=payload.timezone,
    )
    db.add(tenant)
    await db.flush()
    await db.refresh(tenant)

    token = create_access_token({"sub": str(tenant.id)})
    return TokenResponse(
        access_token=token,
        tenant_id=str(tenant.id),
        tenant_name=tenant.name,
        tenant_slug=tenant.slug,
        plan=tenant.plan,
        api_key=tenant.api_key,
    )


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: DB):
    """Authenticate and receive a JWT token."""
    result = await db.execute(
        select(Tenant).where(Tenant.email == payload.email, Tenant.is_active == True)
    )
    tenant = result.scalar_one_or_none()
    if not tenant or not verify_password(payload.password, tenant.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(tenant.id)})
    return TokenResponse(
        access_token=token,
        tenant_id=str(tenant.id),
        tenant_name=tenant.name,
        tenant_slug=tenant.slug,
        plan=tenant.plan,
        api_key=tenant.api_key,
    )


@router.get("/me", response_model=TenantProfile)
async def get_me(tenant: CurrentTenant):
    """Get the authenticated tenant's profile."""
    return TenantProfile(
        id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        email=tenant.email,
        plan=tenant.plan,
        api_key=tenant.api_key,
        is_active=tenant.is_active,
        company_name=tenant.company_name,
        website=tenant.website,
        phone=tenant.phone,
        timezone=tenant.timezone,
        logo_url=tenant.logo_url,
        created_at=tenant.created_at.isoformat(),
    )


@router.patch("/me", response_model=TenantProfile)
async def update_profile(payload: UpdateProfileRequest, tenant: CurrentTenant, db: DB):
    """Update the authenticated tenant's profile."""
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(tenant, field, value)
    await db.flush()
    await db.refresh(tenant)
    return TenantProfile(
        id=tenant.id,
        name=tenant.name,
        slug=tenant.slug,
        email=tenant.email,
        plan=tenant.plan,
        api_key=tenant.api_key,
        is_active=tenant.is_active,
        company_name=tenant.company_name,
        website=tenant.website,
        phone=tenant.phone,
        timezone=tenant.timezone,
        logo_url=tenant.logo_url,
        created_at=tenant.created_at.isoformat(),
    )


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(payload: ChangePasswordRequest, tenant: CurrentTenant, db: DB):
    """Change the authenticated tenant's password."""
    if not verify_password(payload.current_password, tenant.hashed_password):
        raise HTTPException(status_code=400, detail="Current password is incorrect")
    tenant.hashed_password = hash_password(payload.new_password)
    await db.flush()


@router.post("/regenerate-api-key", response_model=dict)
async def regenerate_api_key(tenant: CurrentTenant, db: DB):
    """Regenerate the tenant API key."""
    new_key = uuid.uuid4().hex
    tenant.api_key = new_key
    await db.flush()
    return {"api_key": new_key}
