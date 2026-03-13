"""Leads Router"""

import csv
import io
import uuid
from typing import List, Optional

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import func, select

from app.core.dependencies import DB, CurrentTenant
from app.models.lead import Lead, LeadStatus
from app.schemas.lead import LeadCreate, LeadListResponse, LeadResponse, LeadUpdate
from app.services.lead_service import LeadService

router = APIRouter(prefix="/leads", tags=["Lead Capture"])


@router.post("/", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(payload: LeadCreate, tenant: CurrentTenant, db: DB):
    """Capture a new lead from a form or integration."""
    lead = await LeadService.create(db, tenant.id, payload)
    return lead


@router.get("/", response_model=LeadListResponse)
async def list_leads(
    tenant: CurrentTenant,
    db: DB,
    status: Optional[LeadStatus] = None,
    source: Optional[str] = Query(None),
    campaign: Optional[str] = Query(None),
    ai_label: Optional[str] = Query(None, description="hot | warm | cold"),
    search: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List all leads with optional filters."""
    items, total = await LeadService.list(
        db, tenant.id,
        status=status, source=source, campaign=campaign,
        ai_label=ai_label, search=search, page=page, page_size=page_size,
    )
    return LeadListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/export/csv")
async def export_leads_csv(
    tenant: CurrentTenant,
    db: DB,
    status: Optional[LeadStatus] = None,
    source: Optional[str] = Query(None),
    campaign: Optional[str] = Query(None),
):
    """Export all leads as a CSV file."""
    items, _ = await LeadService.list(
        db, tenant.id,
        status=status, source=source, campaign=campaign,
        page=1, page_size=10000,
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "name", "email", "phone", "company", "source", "campaign",
                     "medium", "status", "ai_score", "ai_label", "notes", "created_at"])
    for lead in items:
        writer.writerow([
            str(lead.id), lead.name, lead.email or "", lead.phone or "",
            lead.company or "", lead.source or "", lead.campaign or "",
            lead.medium or "", (lead.status.value if hasattr(lead.status, 'value') else str(lead.status)), lead.ai_score or "",
            lead.ai_label or "", (lead.notes or "").replace("\n", " "),
            lead.created_at.isoformat(),
        ])
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="leads.csv"'},
    )


@router.post("/import/csv", status_code=status.HTTP_200_OK)
async def import_leads_csv(
    tenant: CurrentTenant,
    db: DB,
    file: UploadFile = File(..., description="CSV file with columns: name, email, phone, company, source, campaign"),
):
    """Bulk-import leads from a CSV file."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are accepted")

    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")))

    created = 0
    skipped = 0
    errors: list[str] = []

    for i, row in enumerate(reader, start=2):  # row 1 = header
        name = (row.get("name") or "").strip()
        if not name:
            skipped += 1
            continue
        try:
            payload = LeadCreate(
                name=name,
                email=row.get("email") or None,
                phone=row.get("phone") or None,
                company=row.get("company") or None,
                source=row.get("source") or "csv_import",
                campaign=row.get("campaign") or None,
                medium=row.get("medium") or None,
                notes=row.get("notes") or None,
            )
            await LeadService.create(db, tenant.id, payload)
            created += 1
        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")
            skipped += 1

    return {"created": created, "skipped": skipped, "errors": errors[:20]}


class BulkUpdateRequest(BaseModel):
    ids: List[uuid.UUID]
    status: Optional[LeadStatus] = None


@router.post("/bulk-update", status_code=status.HTTP_200_OK)
async def bulk_update_leads(payload: BulkUpdateRequest, tenant: CurrentTenant, db: DB):
    """Bulk-update lead statuses."""
    if not payload.ids:
        raise HTTPException(status_code=400, detail="No IDs provided")
    updated = 0
    for lead_id in payload.ids:
        lead = await LeadService.get(db, tenant.id, lead_id)
        if lead and payload.status:
            lead.status = payload.status
            updated += 1
    return {"updated": updated}


@router.get("/stats/summary")
async def lead_stats(tenant: CurrentTenant, db: DB):
    """Quick summary stats for leads."""
    from sqlalchemy import case
    result = await db.execute(
        select(
            func.count(Lead.id).label("total"),
            func.count(Lead.id).filter(Lead.status == LeadStatus.NEW).label("new"),
            func.count(Lead.id).filter(Lead.status == LeadStatus.CONTACTED).label("contacted"),
            func.count(Lead.id).filter(Lead.status == LeadStatus.QUALIFIED).label("qualified"),
            func.count(Lead.id).filter(Lead.status == LeadStatus.CONVERTED).label("converted"),
            func.count(Lead.id).filter(Lead.ai_label == "hot").label("hot"),
            func.count(Lead.id).filter(Lead.ai_label == "warm").label("warm"),
            func.count(Lead.id).filter(Lead.ai_label == "cold").label("cold"),
        ).where(Lead.tenant_id == tenant.id)
    )
    row = result.one()
    return {
        "total": row.total, "new": row.new, "contacted": row.contacted,
        "qualified": row.qualified, "converted": row.converted,
        "hot": row.hot, "warm": row.warm, "cold": row.cold,
        "conversion_rate": round((row.converted / row.total * 100) if row.total else 0, 2),
    }


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    lead = await LeadService.get(db, tenant.id, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(lead_id: uuid.UUID, payload: LeadUpdate, tenant: CurrentTenant, db: DB):
    lead = await LeadService.update(db, tenant.id, lead_id, payload)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.delete("/{lead_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_lead(lead_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    deleted = await LeadService.delete(db, tenant.id, lead_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Lead not found")


@router.post("/{lead_id}/score", response_model=LeadResponse)
async def score_lead(lead_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    """Trigger AI lead scoring for a specific lead."""
    from app.services.ai_service import AIService
    lead = await LeadService.get(db, tenant.id, lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    scored = await AIService.classify_lead(db, tenant.id, lead)
    return scored


@router.post("/{lead_id}/convert", response_model=LeadResponse)
async def convert_lead(lead_id: uuid.UUID, tenant: CurrentTenant, db: DB):
    """Mark a lead as converted and optionally create a CRM deal."""
    from app.schemas.lead import LeadUpdate
    lead = await LeadService.update(
        db, tenant.id, lead_id, LeadUpdate(status=LeadStatus.CONVERTED)
    )
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead
