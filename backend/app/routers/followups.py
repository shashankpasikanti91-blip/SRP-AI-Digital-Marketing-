"""Followups Router — AI-generated follow-up sequences"""
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from app.core.dependencies import DB, CurrentTenant
from app.models.followup import FollowupSequence, FollowupStep, SequenceStatus

router = APIRouter(prefix="/followups", tags=["Follow-ups"])


class GenerateSequenceRequest(BaseModel):
    lead_name: str
    product_or_service: str
    pain_point: Optional[str] = None
    channel: str = "email"
    goal: str = "convert"
    persona: Optional[str] = None
    tone: str = "professional"
    num_steps: int = Field(6, ge=2, le=10)


class SequenceCreate(BaseModel):
    name: str = Field(..., max_length=200)
    trigger: str = "new_lead"
    sequence_type: str = "new_lead"
    target_segment: Optional[str] = None


class SequenceUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[SequenceStatus] = None
    target_segment: Optional[str] = None


class StepUpdate(BaseModel):
    subject: Optional[str] = None
    body: Optional[str] = None
    delay_days: Optional[int] = None
    cta: Optional[str] = None


@router.get("/")
async def list_sequences(
    tenant: CurrentTenant,
    db: DB,
    seq_status: Optional[SequenceStatus] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    query = select(FollowupSequence).where(FollowupSequence.tenant_id == tenant.id)
    if seq_status:
        query = query.where(FollowupSequence.status == seq_status)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    query = query.order_by(FollowupSequence.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = list((await db.execute(query)).scalars().all())
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_followup_sequence(payload: GenerateSequenceRequest, tenant: CurrentTenant, db: DB):
    """Use Follow-up Agent to build a complete nurture sequence and save all steps."""
    from app.agents.followup_agent import FollowupAgent
    agent = FollowupAgent()
    try:
        output = await agent.run(
            lead_name=payload.lead_name,
            product_or_service=payload.product_or_service,
            pain_point=payload.pain_point,
            channel=payload.channel,
            goal=payload.goal,
            persona=payload.persona,
            tone=payload.tone,
            num_steps=payload.num_steps,
        )

        # Save sequence
        sequence = FollowupSequence(
            tenant_id=tenant.id,
            name=output.sequence_name,
            trigger="new_lead",
            sequence_type="ai_generated",
            target_segment=payload.lead_name,
            ai_generated_json=output.model_dump(),
        )
        db.add(sequence)
        await db.flush()

        # Save steps
        for step_data in output.steps:
            step = FollowupStep(
                sequence_id=sequence.id,
                tenant_id=tenant.id,
                step_number=step_data.step_number,
                delay_days=step_data.day,
                channel=payload.channel,
                subject=step_data.subject,
                body=step_data.body,
                cta=step_data.cta,
                goal=step_data.tone_hint,
            )
            db.add(step)

        await db.flush()
        await db.refresh(sequence)
        return {
            "sequence_id": str(sequence.id),
            "sequence_name": output.sequence_name,
            "total_steps": len(output.steps),
            "strategy_note": output.strategy_note,
            "steps": [s.model_dump() for s in output.steps],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Followup generation failed: {str(e)}")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_sequence(payload: SequenceCreate, tenant: CurrentTenant, db: DB):
    seq = FollowupSequence(tenant_id=tenant.id, **payload.model_dump())
    db.add(seq)
    await db.flush()
    await db.refresh(seq)
    return seq


@router.get("/{seq_id}")
async def get_sequence(seq_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    result = await db.execute(
        select(FollowupSequence).where(FollowupSequence.id == seq_id, FollowupSequence.tenant_id == tenant.id)
    )
    seq = result.scalar_one_or_none()
    if not seq:
        raise HTTPException(status_code=404, detail="Sequence not found")
    return seq


@router.get("/{seq_id}/steps")
async def list_steps(seq_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    result = await db.execute(
        select(FollowupSequence).where(FollowupSequence.id == seq_id, FollowupSequence.tenant_id == tenant.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sequence not found")
    steps_res = await db.execute(
        select(FollowupStep).where(FollowupStep.sequence_id == seq_id).order_by(FollowupStep.step_number)
    )
    return {"steps": list(steps_res.scalars().all())}


@router.patch("/{seq_id}")
async def update_sequence(seq_id: uuid.UUID, payload: SequenceUpdate, tenant: CurrentTenant, db: DB):
    result = await db.execute(
        select(FollowupSequence).where(FollowupSequence.id == seq_id, FollowupSequence.tenant_id == tenant.id)
    )
    seq = result.scalar_one_or_none()
    if not seq:
        raise HTTPException(status_code=404, detail="Sequence not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(seq, field, value)
    await db.flush()
    await db.refresh(seq)
    return seq


@router.post("/{seq_id}/activate")
async def activate_sequence(seq_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    result = await db.execute(
        select(FollowupSequence).where(FollowupSequence.id == seq_id, FollowupSequence.tenant_id == tenant.id)
    )
    seq = result.scalar_one_or_none()
    if not seq:
        raise HTTPException(status_code=404, detail="Sequence not found")
    seq.status = SequenceStatus.ACTIVE
    await db.flush()
    return {"id": str(seq.id), "status": seq.status, "message": "Sequence activated"}


@router.post("/{seq_id}/pause")
async def pause_sequence(seq_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    result = await db.execute(
        select(FollowupSequence).where(FollowupSequence.id == seq_id, FollowupSequence.tenant_id == tenant.id)
    )
    seq = result.scalar_one_or_none()
    if not seq:
        raise HTTPException(status_code=404, detail="Sequence not found")
    seq.status = SequenceStatus.PAUSED
    await db.flush()
    return {"id": str(seq.id), "status": seq.status}


@router.patch("/{seq_id}/steps/{step_id}")
async def update_step(seq_id: uuid.UUID, step_id: uuid.UUID, payload: StepUpdate, tenant: CurrentTenant, db: DB):
    result = await db.execute(
        select(FollowupSequence).where(FollowupSequence.id == seq_id, FollowupSequence.tenant_id == tenant.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sequence not found")
    step_res = await db.execute(
        select(FollowupStep).where(FollowupStep.id == step_id, FollowupStep.sequence_id == seq_id)
    )
    step = step_res.scalar_one_or_none()
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(step, field, value)
    await db.flush()
    await db.refresh(step)
    return step

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from app.core.dependencies import DB, CurrentTenant
from app.models.followup import FollowupSequence, FollowupStep, SequenceStatus

router = APIRouter(prefix="/followups", tags=["Follow-ups"])


class GenerateSequenceRequest(BaseModel):
    lead_name: str
    product_or_service: str
    pain_point: Optional[str] = None
    channel: str = "email"
    goal: str = "convert"
    persona: Optional[str] = None
    tone: str = "professional"
    num_steps: int = Field(6, ge=2, le=10)
    lead_id: Optional[uuid.UUID] = None


class SequenceCreate(BaseModel):
    name: str = Field(..., max_length=200)
    channel: str = "email"
    lead_id: Optional[uuid.UUID] = None
    goal: Optional[str] = None


class SequenceUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[SequenceStatus] = None
    goal: Optional[str] = None


class StepUpdate(BaseModel):
    subject: Optional[str] = None
    body: Optional[str] = None
    send_delay_days: Optional[int] = None


@router.get("/")
async def list_sequences(
    tenant: CurrentTenant,
    db: DB,
    seq_status: Optional[SequenceStatus] = Query(None, alias="status"),
    lead_id: Optional[uuid.UUID] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    query = select(FollowupSequence).where(FollowupSequence.tenant_id == tenant.id)
    if seq_status:
        query = query.where(FollowupSequence.status == seq_status)
    if lead_id:
        query = query.where(FollowupSequence.lead_id == lead_id)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    query = query.order_by(FollowupSequence.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    items = list((await db.execute(query)).scalars().all())
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_followup_sequence(payload: GenerateSequenceRequest, tenant: CurrentTenant, db: DB):
    """Use Follow-up Agent to build a complete nurture sequence and save all steps."""
    from app.agents.followup_agent import FollowupAgent
    agent = FollowupAgent()
    try:
        output = await agent.run(
            lead_name=payload.lead_name,
            product_or_service=payload.product_or_service,
            pain_point=payload.pain_point,
            channel=payload.channel,
            goal=payload.goal,
            persona=payload.persona,
            tone=payload.tone,
            num_steps=payload.num_steps,
        )

        # Save sequence
        sequence = FollowupSequence(
            tenant_id=tenant.id,
            lead_id=payload.lead_id,
            name=output.sequence_name,
            channel=payload.channel,
            goal=payload.goal,
            total_steps=len(output.steps),
            ai_generated=True,
        )
        db.add(sequence)
        await db.flush()

        # Save steps
        for step_data in output.steps:
            step = FollowupStep(
                sequence_id=sequence.id,
                step_number=step_data.step_number,
                send_delay_days=step_data.day,
                subject=step_data.subject,
                body=step_data.body,
                cta=step_data.cta,
                tone=step_data.tone_hint,
            )
            db.add(step)

        await db.flush()
        await db.refresh(sequence)
        return {
            "sequence_id": str(sequence.id),
            "sequence_name": output.sequence_name,
            "total_steps": len(output.steps),
            "strategy_note": output.strategy_note,
            "steps": [s.model_dump() for s in output.steps],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Followup generation failed: {str(e)}")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_sequence(payload: SequenceCreate, tenant: CurrentTenant, db: DB):
    seq = FollowupSequence(tenant_id=tenant.id, **payload.model_dump())
    db.add(seq)
    await db.flush()
    await db.refresh(seq)
    return seq


@router.get("/{seq_id}")
async def get_sequence(seq_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    result = await db.execute(
        select(FollowupSequence).where(FollowupSequence.id == seq_id, FollowupSequence.tenant_id == tenant.id)
    )
    seq = result.scalar_one_or_none()
    if not seq:
        raise HTTPException(status_code=404, detail="Sequence not found")
    return seq


@router.get("/{seq_id}/steps")
async def list_steps(seq_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    # Verify ownership
    result = await db.execute(
        select(FollowupSequence).where(FollowupSequence.id == seq_id, FollowupSequence.tenant_id == tenant.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sequence not found")
    steps_res = await db.execute(
        select(FollowupStep).where(FollowupStep.sequence_id == seq_id).order_by(FollowupStep.step_number)
    )
    return {"steps": list(steps_res.scalars().all())}


@router.patch("/{seq_id}")
async def update_sequence(seq_id: uuid.UUID, payload: SequenceUpdate, tenant: CurrentTenant, db: DB):
    result = await db.execute(
        select(FollowupSequence).where(FollowupSequence.id == seq_id, FollowupSequence.tenant_id == tenant.id)
    )
    seq = result.scalar_one_or_none()
    if not seq:
        raise HTTPException(status_code=404, detail="Sequence not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(seq, field, value)
    await db.flush()
    await db.refresh(seq)
    return seq


@router.post("/{seq_id}/activate")
async def activate_sequence(seq_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    """Set sequence status to active, scheduling follow-up delivery."""
    result = await db.execute(
        select(FollowupSequence).where(FollowupSequence.id == seq_id, FollowupSequence.tenant_id == tenant.id)
    )
    seq = result.scalar_one_or_none()
    if not seq:
        raise HTTPException(status_code=404, detail="Sequence not found")
    seq.status = SequenceStatus.ACTIVE
    await db.flush()
    return {"id": str(seq.id), "status": seq.status, "message": "Sequence activated"}


@router.post("/{seq_id}/pause")
async def pause_sequence(seq_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    result = await db.execute(
        select(FollowupSequence).where(FollowupSequence.id == seq_id, FollowupSequence.tenant_id == tenant.id)
    )
    seq = result.scalar_one_or_none()
    if not seq:
        raise HTTPException(status_code=404, detail="Sequence not found")
    seq.status = SequenceStatus.PAUSED
    await db.flush()
    return {"id": str(seq.id), "status": seq.status}


@router.patch("/{seq_id}/steps/{step_id}")
async def update_step(seq_id: uuid.UUID, step_id: uuid.UUID, payload: StepUpdate, tenant: CurrentTenant, db: DB):
    # Verify ownership
    result = await db.execute(
        select(FollowupSequence).where(FollowupSequence.id == seq_id, FollowupSequence.tenant_id == tenant.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Sequence not found")
    step_res = await db.execute(
        select(FollowupStep).where(FollowupStep.id == step_id, FollowupStep.sequence_id == seq_id)
    )
    step = step_res.scalar_one_or_none()
    if not step:
        raise HTTPException(status_code=404, detail="Step not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(step, field, value)
    await db.flush()
    await db.refresh(step)
    return step
