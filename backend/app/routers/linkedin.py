"""LinkedIn Router — Recruitment & B2B Marketing Automation"""
from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.core.dependencies import DB, CurrentTenant

router = APIRouter(prefix="/linkedin", tags=["LinkedIn"])


# ── Request Schemas ─────────────────────────────────────────────────────────

class JobPostRequest(BaseModel):
    job_title: str = Field(..., min_length=3, example="Senior Selenium Automation Tester")
    location: str = Field(default="Hyderabad", example="Hyderabad")
    experience_years: str = Field(default="3-6 years", example="3-6 years")
    required_skills: list[str] = Field(..., min_length=1, example=["Selenium", "Java", "TestNG"])
    work_mode: str = Field(default="hybrid", example="hybrid")   # remote | hybrid | onsite
    salary_range: Optional[str] = Field(default=None, example="8-15 LPA")
    job_description: Optional[str] = None
    company_culture: Optional[str] = None
    save_as_lead: bool = False


class OutreachRequest(BaseModel):
    candidate_name: str = Field(..., example="Rahul Sharma")
    candidate_role: str = Field(..., example="QA Engineer at Infosys")
    candidate_skills: list[str] = Field(..., example=["Selenium", "Java", "API Testing"])
    job_title: str = Field(..., example="Senior Automation Tester")
    why_good_fit: Optional[str] = None
    message_type: str = Field(default="connection_request", example="connection_request")


class HiringAnnouncementRequest(BaseModel):
    roles_hiring: list[str] = Field(..., min_length=1, example=["Python Developer", "QA Lead"])
    location: str = Field(default="Hyderabad")
    company_size: Optional[str] = Field(default=None, example="50-200 employees")
    key_benefits: Optional[list[str]] = Field(default=None, example=["5 day week", "WFH 2 days", "Health insurance"])
    company_culture: Optional[str] = None
    urgent: bool = False


class CompanyPostRequest(BaseModel):
    topic: str = Field(..., min_length=5, example="How AI is transforming IT recruitment in 2026")
    post_type: str = Field(default="thought_leadership")  # thought_leadership | case_study | announcement | tips
    target_audience: str = Field(default="CTOs, HR managers, IT professionals")
    include_stats: bool = True


class ParseCandidateRequest(BaseModel):
    raw_message: str = Field(..., min_length=10)
    job_title: Optional[str] = None


class BulkJobPostRequest(BaseModel):
    job_titles: list[str] = Field(..., min_length=1, max_length=10)
    location: str = Field(default="Hyderabad")
    work_mode: str = Field(default="hybrid")


# ── Routes ──────────────────────────────────────────────────────────────────

@router.post("/job-post")
async def generate_job_post(payload: JobPostRequest, tenant: CurrentTenant, db: DB):
    """Generate a ready-to-post LinkedIn job post for a given role."""
    from app.agents.linkedin_agent import LinkedInAgent
    from app.models.business_profile import BusinessProfile
    from sqlalchemy import select

    bp_res = await db.execute(
        select(BusinessProfile).where(BusinessProfile.tenant_id == tenant.id)
    )
    bp = bp_res.scalar_one_or_none()
    company_name = bp.business_name if bp else tenant.name

    agent = LinkedInAgent()
    try:
        result = await agent.generate_job_post(
            job_title=payload.job_title,
            company_name=company_name,
            location=payload.location,
            experience_years=payload.experience_years,
            required_skills=payload.required_skills,
            work_mode=payload.work_mode,
            salary_range=payload.salary_range,
            job_description=payload.job_description,
            company_culture=payload.company_culture,
        )
        return {
            "success": True,
            "company": company_name,
            "job_post": result.model_dump(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Job post generation failed: {str(e)}")


@router.post("/outreach-message")
async def generate_outreach_message(payload: OutreachRequest, tenant: CurrentTenant, db: DB):
    """Generate a personalised LinkedIn outreach message for a candidate."""
    from app.agents.linkedin_agent import LinkedInAgent
    from app.models.business_profile import BusinessProfile
    from sqlalchemy import select

    bp_res = await db.execute(
        select(BusinessProfile).where(BusinessProfile.tenant_id == tenant.id)
    )
    bp = bp_res.scalar_one_or_none()
    company_name = bp.business_name if bp else tenant.name

    agent = LinkedInAgent()
    try:
        result = await agent.generate_outreach_message(
            candidate_name=payload.candidate_name,
            candidate_role=payload.candidate_role,
            candidate_skills=payload.candidate_skills,
            recruiter_name=tenant.name,
            company_name=company_name,
            job_title=payload.job_title,
            why_good_fit=payload.why_good_fit,
            message_type=payload.message_type,
        )
        return {"success": True, "outreach": result.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Outreach generation failed: {str(e)}")


@router.post("/hiring-announcement")
async def generate_hiring_announcement(payload: HiringAnnouncementRequest, tenant: CurrentTenant, db: DB):
    """Generate a LinkedIn hiring announcement post."""
    from app.agents.linkedin_agent import LinkedInAgent
    from app.models.business_profile import BusinessProfile
    from sqlalchemy import select

    bp_res = await db.execute(
        select(BusinessProfile).where(BusinessProfile.tenant_id == tenant.id)
    )
    bp = bp_res.scalar_one_or_none()
    company_name = bp.business_name if bp else tenant.name

    agent = LinkedInAgent()
    try:
        result = await agent.generate_hiring_announcement(
            company_name=company_name,
            roles_hiring=payload.roles_hiring,
            location=payload.location,
            company_size=payload.company_size,
            key_benefits=payload.key_benefits,
            company_culture=payload.company_culture,
            urgent=payload.urgent,
        )
        return {"success": True, "announcement": result.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hiring announcement failed: {str(e)}")


@router.post("/company-post")
async def generate_company_post(payload: CompanyPostRequest, tenant: CurrentTenant, db: DB):
    """Generate a LinkedIn company/brand post (thought leadership, tips, announcements)."""
    from app.agents.linkedin_agent import LinkedInAgent
    from app.models.business_profile import BusinessProfile
    from sqlalchemy import select

    bp_res = await db.execute(
        select(BusinessProfile).where(BusinessProfile.tenant_id == tenant.id)
    )
    bp = bp_res.scalar_one_or_none()
    company_name = bp.business_name if bp else tenant.name
    industry = bp.industry if bp else "IT / Technology"

    agent = LinkedInAgent()
    try:
        result = await agent.generate_company_post(
            company_name=company_name,
            topic=payload.topic,
            post_type=payload.post_type,
            industry=industry,
            target_audience=payload.target_audience,
            include_stats=payload.include_stats,
        )
        return {"success": True, "post": result.model_dump()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Company post generation failed: {str(e)}")


@router.post("/parse-candidate")
async def parse_candidate_message(payload: ParseCandidateRequest, tenant: CurrentTenant, db: DB):
    """Parse an incoming LinkedIn candidate message and extract lead data."""
    from app.agents.linkedin_agent import LinkedInAgent
    from app.models.lead import Lead
    from app.models.business_profile import BusinessProfile
    from sqlalchemy import select

    bp_res = await db.execute(
        select(BusinessProfile).where(BusinessProfile.tenant_id == tenant.id)
    )
    bp = bp_res.scalar_one_or_none()
    company_name = bp.business_name if bp else tenant.name

    agent = LinkedInAgent()
    try:
        result = await agent.parse_candidate_message(
            raw_message=payload.raw_message,
            job_title=payload.job_title,
            company_name=company_name,
        )
        parsed = result.model_dump()

        # Auto-create lead if name found and interest is high/medium
        lead_id = None
        if result.name and result.interest_level in ("high", "medium"):
            lead = Lead(
                tenant_id=tenant.id,
                name=result.name,
                source="linkedin",
                notes=f"LinkedIn candidate. Skills: {', '.join(result.skills[:5])}. "
                      f"Notice: {result.notice_period or 'Unknown'}. "
                      f"CTC: {result.expected_ctc or 'Unknown'}.",
                ai_label={"high": "hot", "medium": "warm"}.get(result.interest_level, "cold"),
            )
            db.add(lead)
            await db.flush()
            lead_id = str(lead.id)

        return {
            "success": True,
            "parsed": parsed,
            "lead_created": lead_id is not None,
            "lead_id": lead_id,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Candidate parsing failed: {str(e)}")


@router.post("/bulk-job-posts")
async def bulk_job_posts(payload: BulkJobPostRequest, tenant: CurrentTenant, db: DB):
    """Generate LinkedIn job posts for multiple roles at once (max 10)."""
    from app.agents.linkedin_agent import LinkedInAgent
    from app.models.business_profile import BusinessProfile
    from sqlalchemy import select

    bp_res = await db.execute(
        select(BusinessProfile).where(BusinessProfile.tenant_id == tenant.id)
    )
    bp = bp_res.scalar_one_or_none()
    company_name = bp.business_name if bp else tenant.name

    agent = LinkedInAgent()
    try:
        results = await agent.bulk_generate_posts(
            job_titles=payload.job_titles,
            company_name=company_name,
            location=payload.location,
            work_mode=payload.work_mode,
        )
        return {
            "success": True,
            "total": len(results),
            "generated": sum(1 for r in results if r.get("success")),
            "posts": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bulk job posts failed: {str(e)}")


@router.get("/templates")
async def get_linkedin_templates(tenant: CurrentTenant):
    """Get pre-built LinkedIn message templates for common hiring scenarios."""
    return {
        "connection_request_templates": [
            {
                "scenario": "Tech role in Hyderabad",
                "template": "Hi {name}, I came across your profile and was impressed by your {skill} experience. "
                           "We have an exciting {role} opportunity at {company} in Hyderabad. Would love to connect!",
            },
            {
                "scenario": "Passive candidate",
                "template": "Hi {name}, your background in {skill} caught my attention. "
                           "Not sure if you're open to new opportunities, but we're building something exciting at {company}. "
                           "Happy to share details if you're curious!",
            },
            {
                "scenario": "Referral",
                "template": "Hi {name}, {referrer_name} from {referrer_company} suggested I reach out. "
                           "We're hiring a {role} and your profile looks like a great fit. Would you be open to a quick chat?",
            },
        ],
        "follow_up_templates": [
            {
                "day": 3,
                "template": "Hi {name}, just following up on my earlier message about the {role} at {company}. "
                           "We're moving quickly on this. Let me know if you'd like to know more!",
            },
            {
                "day": 7,
                "template": "Hi {name}, I know you're probably busy. Just wanted to share that the {role} role "
                           "at {company} has a {benefit}. Happy to schedule a quick 15-min call if interested.",
            },
        ],
        "job_post_frameworks": [
            "Problem → Solution → Opportunity (PSO)",
            "Role → Impact → Growth Path",
            "Company Story → Team Culture → Apply",
        ],
    }
