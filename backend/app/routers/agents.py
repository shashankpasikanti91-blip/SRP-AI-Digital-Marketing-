"""Agents Router — orchestrated AI workflows"""
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select

from app.core.dependencies import DB, CurrentTenant

router = APIRouter(prefix="/agents", tags=["AI Agents"])


class NewLeadWorkflowRequest(BaseModel):
    lead_id: Optional[uuid.UUID] = None
    raw_lead_data: Optional[dict] = None
    lead_name: Optional[str] = None
    lead_email: Optional[str] = None
    lead_phone: Optional[str] = None
    lead_source: Optional[str] = None
    message: Optional[str] = None


class CampaignLaunchRequest(BaseModel):
    campaign_goal: str = Field(..., min_length=5)
    topic: Optional[str] = None
    target_audience: str = "General audience"
    budget: int = 1000
    duration_weeks: int = 4
    channels: Optional[list[str]] = None
    offer_details: Optional[str] = None
    save_campaign: bool = True


class QualifyLeadRequest(BaseModel):
    lead_id: uuid.UUID


class PipelineDecisionRequest(BaseModel):
    lead_id: uuid.UUID
    current_stage: Optional[str] = None


@router.post("/new-lead-workflow")
async def run_new_lead_workflow(payload: NewLeadWorkflowRequest, tenant: CurrentTenant, db: DB):
    """
    Full new-lead processing: capture → normalise → qualify → CRM pipeline decision → follow-up sequence.
    Accepts either a lead_id (existing DB lead) or a raw_lead_data dict.
    """
    from app.agents.orchestrator import AgentOrchestrator
    from app.models.lead import Lead

    orch = AgentOrchestrator()

    # Build raw data from request or fetch from DB
    raw_data = payload.raw_lead_data or {}
    if payload.lead_id:
        result = await db.execute(
            select(Lead).where(Lead.id == payload.lead_id, Lead.tenant_id == tenant.id)
        )
        lead = result.scalar_one_or_none()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")
        raw_data = {
            "name": lead.name or "",
            "email": lead.email or "",
            "phone": lead.phone or "",
            "source": lead.source or "",
            "message": payload.message or "",
            "company": lead.company or "",
        }
    else:
        # Fill from explicit fields
        raw_data.setdefault("name", payload.lead_name or "")
        raw_data.setdefault("email", payload.lead_email or "")
        raw_data.setdefault("phone", payload.lead_phone or "")
        raw_data.setdefault("source", payload.lead_source or "webhook")
        raw_data.setdefault("message", payload.message or "")

    try:
        # Get business context
        from app.models.business_profile import BusinessProfile
        bp_res = await db.execute(
            select(BusinessProfile).where(BusinessProfile.tenant_id == tenant.id)
        )
        bp = bp_res.scalar_one_or_none()

        result = await orch.run_new_lead_workflow(
            raw_lead_data=raw_data,
            business_name=bp.business_name if bp else tenant.name,
            product_or_service=bp.main_offer if bp else "our services",
        )

        # Update lead in DB if provided
        if payload.lead_id and result.get("qualification"):
            qual = result["qualification"]
            lead_res = await db.execute(
                select(Lead).where(Lead.id == payload.lead_id, Lead.tenant_id == tenant.id)
            )
            lead = lead_res.scalar_one_or_none()
            if lead:
                lead.ai_score = qual.get("score")
                lead.ai_label = qual.get("label")

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"New lead workflow failed: {str(e)}")


@router.post("/campaign-launch")
async def run_campaign_launch(payload: CampaignLaunchRequest, tenant: CurrentTenant, db: DB):
    """
    Full campaign launch: campaign plan + multi-platform content + design brief — all in parallel.
    """
    from app.agents.orchestrator import AgentOrchestrator
    from app.models.business_profile import BusinessProfile
    from app.models.campaign import Campaign

    orch = AgentOrchestrator()

    bp_res = await db.execute(
        select(BusinessProfile).where(BusinessProfile.tenant_id == tenant.id)
    )
    bp = bp_res.scalar_one_or_none()

    try:
        result = await orch.run_campaign_launch_workflow(
            business_name=bp.business_name if bp else tenant.name,
            campaign_goal=payload.campaign_goal,
            topic=payload.topic or payload.campaign_goal,
            target_audience=payload.target_audience,
            budget=payload.budget,
            channels=payload.channels or ["facebook", "instagram", "email"],
            industry=bp.industry if bp else "General",
            offer=payload.offer_details or (bp.main_offer if bp else None),
            duration_weeks=payload.duration_weeks,
        )

        if payload.save_campaign and result.get("campaign_plan"):
            plan = result["campaign_plan"]
            campaign = Campaign(
                tenant_id=tenant.id,
                name=plan.get("campaign_name", payload.campaign_goal),
                objective=plan.get("campaign_objective", payload.campaign_goal),
                channels=payload.channels,
                budget_total=payload.budget * 100,
                currency="USD",
                duration_weeks=payload.duration_weeks,
                target_audience=payload.target_audience,
                ai_plan_json=result,
            )
            db.add(campaign)
            await db.flush()
            result["campaign_id"] = str(campaign.id)
            result["campaign_saved"] = True

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Campaign launch workflow failed: {str(e)}")


@router.post("/qualify-lead")
async def qualify_lead(payload: QualifyLeadRequest, tenant: CurrentTenant, db: DB):
    """Run only the lead qualification agent on an existing lead."""
    from app.agents.lead_qualification_agent import LeadQualificationAgent
    from app.models.lead import Lead

    result = await db.execute(
        select(Lead).where(Lead.id == payload.lead_id, Lead.tenant_id == tenant.id)
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    agent = LeadQualificationAgent()
    try:
        qual = await agent.run(
            name=lead.name or "",
            email=lead.email or "",
            company=lead.company or "",
            message=lead.notes or "",
            source=lead.source or "",
            phone=lead.phone or "",
        )
        lead.ai_score = qual.score
        lead.ai_label = qual.label
        await db.flush()
        return qual.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lead qualification failed: {str(e)}")


@router.post("/pipeline-decision")
async def run_pipeline_decision(payload: PipelineDecisionRequest, tenant: CurrentTenant, db: DB):
    """Get CRM pipeline stage recommendation for a lead."""
    from app.agents.crm_pipeline_agent import CRMPipelineAgent
    from app.models.lead import Lead

    result = await db.execute(
        select(Lead).where(Lead.id == payload.lead_id, Lead.tenant_id == tenant.id)
    )
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    agent = CRMPipelineAgent()
    try:
        decision = await agent.run(
            lead_name=lead.name or "",
            current_stage=payload.current_stage or "new",
            ai_label=lead.ai_label or "unknown",
            lead_score=lead.ai_score or 0,
            company=lead.company or "",
            source=lead.source or "",
        )
        return decision.model_dump()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline decision failed: {str(e)}")
