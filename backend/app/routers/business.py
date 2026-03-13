"""Business Profile Router — onboarding + strategy generation"""
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.core.dependencies import DB, CurrentTenant
from app.models.business_profile import BusinessProfile

router = APIRouter(prefix="/business", tags=["Business Profile"])


class BusinessProfileCreate(BaseModel):
    business_name: str = Field(..., min_length=1, max_length=200)
    business_type: str = Field(..., max_length=120)
    industry: str = Field(..., max_length=120)
    location: Optional[str] = None
    website: Optional[str] = None
    target_audience: Optional[str] = None
    main_offer: Optional[str] = None
    unique_selling_proposition: Optional[str] = None
    brand_voice: Optional[str] = None
    brand_colors: Optional[list[str]] = None
    competitors: Optional[str] = None
    current_challenges: Optional[str] = None
    monthly_budget: Optional[str] = None
    primary_goal: Optional[str] = None
    channels: Optional[list[str]] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    business_hours: Optional[str] = None


class BusinessProfileUpdate(BusinessProfileCreate):
    business_name: Optional[str] = None
    business_type: Optional[str] = None
    industry: Optional[str] = None


class StrategyRequest(BaseModel):
    goals: Optional[str] = None
    time_horizon: str = "3 months"
    focus_area: Optional[str] = None


@router.get("/")
async def get_business_profile(tenant: CurrentTenant, db: DB):
    """Get the current tenant's business profile."""
    result = await db.execute(
        select(BusinessProfile).where(BusinessProfile.tenant_id == tenant.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Business profile not found. Complete onboarding first.")
    return profile


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_business_profile(payload: BusinessProfileCreate, tenant: CurrentTenant, db: DB):
    """Create or replace the business profile (initial onboarding)."""
    # Check if one already exists
    existing = await db.execute(
        select(BusinessProfile).where(BusinessProfile.tenant_id == tenant.id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Business profile already exists. Use PATCH to update.")

    profile = BusinessProfile(tenant_id=tenant.id, **payload.model_dump())
    db.add(profile)
    await db.flush()
    await db.refresh(profile)
    return profile


@router.patch("/")
async def update_business_profile(payload: BusinessProfileUpdate, tenant: CurrentTenant, db: DB):
    """Update the business profile."""
    result = await db.execute(
        select(BusinessProfile).where(BusinessProfile.tenant_id == tenant.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Business profile not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, field, value)
    await db.flush()
    await db.refresh(profile)
    return profile


@router.post("/generate-strategy")
async def generate_strategy(payload: StrategyRequest, tenant: CurrentTenant, db: DB):
    """Run Strategy Agent to generate a full marketing strategy for this business."""
    result = await db.execute(
        select(BusinessProfile).where(BusinessProfile.tenant_id == tenant.id)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="Complete your business profile first")

    from app.agents.strategy_agent import StrategyAgent
    agent = StrategyAgent()
    try:
        strategy = await agent.run(
            business_name=profile.business_name,
            business_type=profile.business_type,
            industry=profile.industry,
            location=profile.location or "Not specified",
            target_audience=profile.target_audience or "General audience",
            main_offer=profile.main_offer or "Not specified",
            budget_monthly=profile.monthly_budget,
            current_channels=profile.channels,
            goals=payload.goals or profile.primary_goal,
            competitors=profile.competitors,
            challenges=profile.current_challenges,
        )
        # Store strategy
        profile.strategy_json = strategy.model_dump()
        profile.onboarding_completed = True
        await db.flush()
        return {"strategy": strategy.model_dump(), "saved": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI strategy generation failed: {str(e)}")


@router.get("/strategy")
async def get_strategy(tenant: CurrentTenant, db: DB):
    """Get the last generated marketing strategy."""
    result = await db.execute(
        select(BusinessProfile).where(BusinessProfile.tenant_id == tenant.id)
    )
    profile = result.scalar_one_or_none()
    if not profile or not profile.strategy_json:
        raise HTTPException(status_code=404, detail="No strategy generated yet. Run /generate-strategy first.")
    return profile.strategy_json
