"""Agent 11 — LinkedIn Recruitment & Marketing Agent
Specialised for IT recruitment agencies and B2B companies in India.
Generates job posts, hiring announcements, candidate outreach messages,
profile optimisation tips, and company page content.
Uses gpt-4o for high quality professional content.
"""
from __future__ import annotations

import json
from typing import Optional

from openai import AsyncOpenAI
from pydantic import BaseModel, Field

from app.config import settings


# ── Output Schemas ─────────────────────────────────────────────────────────

class LinkedInJobPost(BaseModel):
    title: str
    company_tagline: str
    about_role: str
    key_responsibilities: list[str]
    required_skills: list[str]
    preferred_skills: list[str]
    experience_years: str
    location: str
    work_mode: str               # remote | hybrid | onsite
    salary_range: Optional[str] = None
    perks: list[str]
    application_cta: str
    hashtags: list[str]
    full_post_text: str          # ready-to-paste LinkedIn post


class LinkedInOutreachMessage(BaseModel):
    subject_line: str
    greeting: str
    opening_hook: str
    value_proposition: str
    specific_mention: str        # personalised detail about candidate
    cta: str
    closing: str
    full_message: str
    note_on_tone: str


class LinkedInHiringPost(BaseModel):
    headline: str
    excitement_line: str
    team_culture_snippet: str
    what_we_offer: list[str]
    ideal_candidate_traits: list[str]
    roles_hiring: list[str]
    apply_cta: str
    hashtags: list[str]
    full_post_text: str


class LinkedInCompanyPost(BaseModel):
    post_type: str              # thought_leadership | case_study | announcement | tips
    headline: str
    body: str
    key_takeaways: list[str]
    cta: str
    hashtags: list[str]
    best_posting_time: str


class CandidateParseOutput(BaseModel):
    name: Optional[str] = None
    current_role: Optional[str] = None
    years_experience: Optional[int] = None
    skills: list[str]
    location: Optional[str] = None
    notice_period: Optional[str] = None
    expected_ctc: Optional[str] = None
    interest_level: str          # high | medium | low | not_interested
    key_points: list[str]
    suggested_reply: str
    next_action: str


# ── System Prompts ──────────────────────────────────────────────────────────

JOB_POST_PROMPT = """You are an expert LinkedIn recruiter and talent acquisition specialist
for the Indian IT industry. You write compelling job posts that:
- Sound human, not robotic
- Highlight real growth opportunities
- Use the right technical keywords for ATS
- Appeal to both active and passive candidates
- Are optimised for LinkedIn's algorithm (engagement, reach)
- Follow Indian market norms (mention work mode, notice period expectations, growth path)

Always return ONLY valid JSON matching the schema. Be specific and realistic."""

OUTREACH_PROMPT = """You are a senior IT recruiter crafting personalised LinkedIn outreach messages.
Your messages:
- Feel personal, not mass-blast
- Reference something specific about the candidate (skills, experience, achievements)
- Are concise (under 300 characters for connection request, 500 for InMail)
- Have a clear, low-pressure CTA
- Never start with "I hope this message finds you well"
- Sound like a real person, not a bot

Return ONLY valid JSON matching the schema."""

HIRING_ANNOUNCEMENT_PROMPT = """You are a LinkedIn content strategist helping companies
post hiring announcements that get REAL applications (not just likes).
Write content that:
- Creates FOMO (fear of missing out) 
- Shows company culture authentically
- Lists concrete benefits (growth, salary band if possible, flexibility)
- Uses inclusive language
- Has a clear call-to-action

Return ONLY valid JSON matching the schema."""

COMPANY_POST_PROMPT = """You are a B2B LinkedIn content expert for Indian IT companies.
You create thought leadership and brand content that:
- Builds trust with decision makers
- Shows industry expertise
- Drives engagement (comments, shares)
- Positions the company as a top employer
- Uses data, stories, or frameworks (not generic advice)

Return ONLY valid JSON matching the schema."""

CANDIDATE_PARSE_PROMPT = """You are an experienced IT recruiter parsing a candidate's LinkedIn 
message or profile snippet. Extract:
- Personal details (name, role, experience)
- Technical skills and stack
- Location and availability
- Notice period and salary expectations
- Their level of interest in the opportunity
- Suggested next steps

Return ONLY valid JSON matching the schema."""


class LinkedInAgent:
    """Agent 11: LinkedIn Recruitment & B2B Marketing Agent for Indian IT market."""

    def __init__(self):
        from app.services.model_router import get_model_router, FeatureBucket
        router = get_model_router()
        self._client, self._model = router.resolve(FeatureBucket.text_marketing)

    # ── Job Post Generation ─────────────────────────────────────────────

    async def generate_job_post(
        self,
        job_title: str,
        company_name: str,
        location: str,
        experience_years: str,
        required_skills: list[str],
        work_mode: str = "hybrid",
        salary_range: Optional[str] = None,
        job_description: Optional[str] = None,
        industry: Optional[str] = "IT",
        company_culture: Optional[str] = None,
    ) -> LinkedInJobPost:
        prompt = f"""Generate a LinkedIn job post for:

Job Title: {job_title}
Company: {company_name}
Location: {location}
Experience: {experience_years}
Required Skills: {', '.join(required_skills)}
Work Mode: {work_mode}
Salary Range: {salary_range or 'Competitive (not disclosed)'}
Industry: {industry}
Job Description Context: {job_description or 'Standard role for this title'}
Company Culture: {company_culture or 'Collaborative, learning-focused, growth-oriented'}

Create a complete, engaging LinkedIn job post optimised for Indian IT market.
Make it compelling enough that a passive candidate would consider applying."""

        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": JOB_POST_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=1500,
        )
        return LinkedInJobPost(**json.loads(resp.choices[0].message.content))

    # ── Candidate Outreach ──────────────────────────────────────────────

    async def generate_outreach_message(
        self,
        candidate_name: str,
        candidate_role: str,
        candidate_skills: list[str],
        recruiter_name: str,
        company_name: str,
        job_title: str,
        why_good_fit: Optional[str] = None,
        message_type: str = "connection_request",   # connection_request | inmail | follow_up
    ) -> LinkedInOutreachMessage:
        prompt = f"""Write a personalised LinkedIn {message_type} message:

Candidate: {candidate_name}
Their Current Role: {candidate_role}
Their Skills: {', '.join(candidate_skills)}
Recruiter: {recruiter_name} from {company_name}
Role We're Hiring For: {job_title}
Why They're a Good Fit: {why_good_fit or 'Strong technical match with required skills'}
Message Type: {message_type}

Make it feel personal, relevant, and non-pushy. Indian IT market context."""

        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": OUTREACH_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.75,
            max_tokens=800,
        )
        return LinkedInOutreachMessage(**json.loads(resp.choices[0].message.content))

    # ── Hiring Announcement ─────────────────────────────────────────────

    async def generate_hiring_announcement(
        self,
        company_name: str,
        roles_hiring: list[str],
        location: str,
        company_size: Optional[str] = None,
        key_benefits: Optional[list[str]] = None,
        company_culture: Optional[str] = None,
        urgent: bool = False,
    ) -> LinkedInHiringPost:
        prompt = f"""Create a LinkedIn hiring announcement:

Company: {company_name}
Roles Hiring: {', '.join(roles_hiring)}
Location: {location}
Company Size: {company_size or 'Growing startup/mid-size'}
Key Benefits: {', '.join(key_benefits) if key_benefits else 'Competitive pay, growth, flexible work'}
Culture: {company_culture or 'Collaborative, learning-first environment'}
Urgency: {'URGENT - immediate requirement' if urgent else 'Planned hiring'}

Target: Experienced Indian IT professionals on LinkedIn."""

        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": HIRING_ANNOUNCEMENT_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=1000,
        )
        return LinkedInHiringPost(**json.loads(resp.choices[0].message.content))

    # ── Company / Brand Post ────────────────────────────────────────────

    async def generate_company_post(
        self,
        company_name: str,
        topic: str,
        post_type: str = "thought_leadership",   # thought_leadership | case_study | announcement | tips
        industry: str = "IT / Technology",
        target_audience: str = "CTOs, HR managers, IT professionals",
        include_stats: bool = True,
    ) -> LinkedInCompanyPost:
        prompt = f"""Create a LinkedIn company post:

Company: {company_name}
Post Type: {post_type}
Topic: {topic}
Industry: {industry}
Target Audience: {target_audience}
Include Stats/Data: {include_stats}

Focus on Indian B2B tech market. Make it shareable and comment-worthy."""

        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": COMPANY_POST_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=1000,
        )
        return LinkedInCompanyPost(**json.loads(resp.choices[0].message.content))

    # ── Parse Incoming Candidate Message ───────────────────────────────

    async def parse_candidate_message(
        self,
        raw_message: str,
        job_title: Optional[str] = None,
        company_name: Optional[str] = None,
    ) -> CandidateParseOutput:
        prompt = f"""Parse this LinkedIn message from a candidate and extract all relevant details.

Job We're Hiring For: {job_title or 'Not specified'}
Our Company: {company_name or 'Not specified'}

Candidate Message:
---
{raw_message}
---

Extract information, assess interest level, and suggest next recruiter action."""

        resp = await self._client.chat.completions.create(
            model=self._model,
            messages=[
                {"role": "system", "content": CANDIDATE_PARSE_PROMPT},
                {"role": "user", "content": prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.3,
            max_tokens=800,
        )
        return CandidateParseOutput(**json.loads(resp.choices[0].message.content))

    # ── Batch: Generate 5 Job Posts ─────────────────────────────────────

    async def bulk_generate_posts(
        self,
        job_titles: list[str],
        company_name: str,
        location: str = "Hyderabad",
        work_mode: str = "hybrid",
    ) -> list[dict]:
        """Generate multiple job posts for different roles at once."""
        results = []
        for title in job_titles:
            try:
                post = await self.generate_job_post(
                    job_title=title,
                    company_name=company_name,
                    location=location,
                    experience_years="3-8 years",
                    required_skills=[title.split()[0], "Communication", "Problem Solving"],
                    work_mode=work_mode,
                )
                results.append({"title": title, "post": post.model_dump(), "success": True})
            except Exception as e:
                results.append({"title": title, "error": str(e), "success": False})
        return results
