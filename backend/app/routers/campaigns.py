"""Campaigns Router — create, manage, and AI-plan campaigns"""
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from app.core.dependencies import DB, CurrentTenant
from app.models.campaign import Campaign, CampaignStatus

router = APIRouter(prefix="/campaigns", tags=["Campaigns"])


class CampaignCreate(BaseModel):
    name: str = Field(..., max_length=200)
    objective: str = Field(..., max_length=200)
    target_audience: Optional[str] = None
    industry: Optional[str] = None
    channels: Optional[list[str]] = None
    budget_total: int = 0
    currency: str = "USD"
    duration_weeks: int = 4
    start_date: Optional[str] = None


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    objective: Optional[str] = None
    status: Optional[CampaignStatus] = None
    target_audience: Optional[str] = None
    channels: Optional[list[str]] = None
    budget_total: Optional[int] = None
    duration_weeks: Optional[int] = None


class AICampaignRequest(BaseModel):
    campaign_goal: str
    budget: int = 1000
    currency: str = "USD"
    duration_weeks: int = 4
    channels: Optional[list[str]] = None
    target_audience: str = "General audience"
    offer: Optional[str] = None
    topic: Optional[str] = None


@router.get("/")
async def list_campaigns(
    tenant: CurrentTenant,
    db: DB,
    status_filter: Optional[CampaignStatus] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    query = select(Campaign).where(Campaign.tenant_id == tenant.id)
    if status_filter:
        query = query.where(Campaign.status == status_filter)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    query = query.order_by(Campaign.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = list((await db.execute(query)).scalars().all())
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_campaign(payload: CampaignCreate, tenant: CurrentTenant, db: DB):
    campaign = Campaign(tenant_id=tenant.id, **payload.model_dump())
    db.add(campaign)
    await db.flush()
    await db.refresh(campaign)
    return campaign


@router.get("/{campaign_id}")
async def get_campaign(campaign_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.tenant_id == tenant.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return item


@router.patch("/{campaign_id}")
async def update_campaign(campaign_id: uuid.UUID, payload: CampaignUpdate, tenant: CurrentTenant, db: DB):
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.tenant_id == tenant.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Campaign not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(item, field, value)
    await db.flush()
    await db.refresh(item)
    return item


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(campaign_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.tenant_id == tenant.id)
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Campaign not found")
    await db.delete(item)


@router.post("/{campaign_id}/ai-plan")
async def generate_ai_campaign_plan(campaign_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    """Use Campaign Agent to generate a detailed AI plan for an existing campaign."""
    result = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id, Campaign.tenant_id == tenant.id)
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Get business profile for context
    from sqlalchemy import select as sel
    from app.models.business_profile import BusinessProfile
    bp_res = await db.execute(sel(BusinessProfile).where(BusinessProfile.tenant_id == tenant.id))
    bp = bp_res.scalar_one_or_none()

    from app.agents.campaign_agent import CampaignAgent
    agent = CampaignAgent()
    try:
        plan = await agent.run(
            business_name=bp.business_name if bp else tenant.name,
            campaign_goal=campaign.objective,
            budget=campaign.budget_total // 100 if campaign.budget_total else 1000,
            currency=campaign.currency,
            duration_weeks=campaign.duration_weeks,
            channels=campaign.channels or ["facebook", "email"],
            target_audience=campaign.target_audience or "General audience",
            industry=campaign.industry or (bp.industry if bp else "General"),
            offer=bp.main_offer if bp else None,
        )
        campaign.ai_plan_json = plan.model_dump()
        await db.flush()
        return {"plan": plan.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Campaign plan generation failed: {str(e)}")


@router.post("/ai-launch")
async def ai_launch_campaign(payload: AICampaignRequest, tenant: CurrentTenant, db: DB):
    """Full AI campaign launch workflow: plan + content + design brief in one call."""
    from app.models.business_profile import BusinessProfile
    bp_res = await db.execute(
        select(BusinessProfile).where(BusinessProfile.tenant_id == tenant.id)
    )
    bp = bp_res.scalar_one_or_none()

    from app.agents.orchestrator import AgentOrchestrator
    orch = AgentOrchestrator()
    try:
        result = await orch.run_campaign_launch_workflow(
            business_name=bp.business_name if bp else tenant.name,
            campaign_goal=payload.campaign_goal,
            topic=payload.topic or payload.campaign_goal,
            target_audience=payload.target_audience,
            budget=payload.budget,
            channels=payload.channels or ["facebook", "instagram", "email"],
            industry=bp.industry if bp else "General",
            offer=payload.offer or (bp.main_offer if bp else None),
            duration_weeks=payload.duration_weeks,
        )

        # Auto-save the campaign
        if result.get("campaign_plan"):
            plan = result["campaign_plan"]
            campaign = Campaign(
                tenant_id=tenant.id,
                name=plan.get("campaign_name", payload.campaign_goal),
                objective=plan.get("campaign_objective", payload.campaign_goal),
                channels=payload.channels,
                budget_total=payload.budget * 100,
                currency=payload.currency,
                duration_weeks=payload.duration_weeks,
                target_audience=payload.target_audience,
                ai_plan_json=result,
            )
            db.add(campaign)
            await db.flush()
            result["campaign_id"] = str(campaign.id)

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Campaign launch failed: {str(e)}")
