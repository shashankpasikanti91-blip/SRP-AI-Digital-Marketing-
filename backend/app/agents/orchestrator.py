"""Agent Orchestrator
Coordinates multiple agents into intelligent marketing workflows.
Logs all agent calls for audit trail.
"""
from __future__ import annotations

import json
import traceback
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.analytics_agent import AnalyticsAgent
from app.agents.campaign_agent import CampaignAgent
from app.agents.content_agent import ContentAgent
from app.agents.conversation_agent import ConversationAgent
from app.agents.crm_pipeline_agent import CRMPipelineAgent
from app.agents.design_brief_agent import DesignBriefAgent
from app.agents.followup_agent import FollowupAgent
from app.agents.lead_capture_agent import LeadCaptureAgent
from app.agents.lead_qualification_agent import LeadQualificationAgent
from app.agents.strategy_agent import StrategyAgent


class AgentRunResult:
    def __init__(self, agent_name: str, output: Any, error: Optional[str] = None, duration_ms: int = 0):
        self.agent_name = agent_name
        self.output = output
        self.error = error
        self.duration_ms = duration_ms
        self.success = error is None


class AgentOrchestrator:
    """Orchestrates multiple AI agents into marketing workflows."""

    def __init__(self):
        self.strategy = StrategyAgent()
        self.content = ContentAgent()
        self.design_brief = DesignBriefAgent()
        self.campaign = CampaignAgent()
        self.lead_capture = LeadCaptureAgent()
        self.lead_qualification = LeadQualificationAgent()
        self.conversation = ConversationAgent()
        self.followup = FollowupAgent()
        self.crm_pipeline = CRMPipelineAgent()
        self.analytics = AnalyticsAgent()

    async def _run_agent(self, agent_name: str, coro) -> AgentRunResult:
        """Run an agent with timing and error handling."""
        start = datetime.now(timezone.utc)
        try:
            output = await coro
            duration = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
            return AgentRunResult(agent_name=agent_name, output=output, duration_ms=duration)
        except Exception as e:
            duration = int((datetime.now(timezone.utc) - start).total_seconds() * 1000)
            return AgentRunResult(
                agent_name=agent_name,
                output=None,
                error=f"{type(e).__name__}: {str(e)}",
                duration_ms=duration,
            )

    async def run_new_lead_workflow(
        self,
        raw_name: str,
        source: str,
        business_name: str,
        business_type: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        company: Optional[str] = None,
        raw_message: Optional[str] = None,
        target_customer_profile: Optional[str] = None,
    ) -> dict:
        """
        Full new lead workflow:
        1. Lead Capture Agent → normalise
        2. Lead Qualification Agent → score
        3. CRM Pipeline Agent → stage decision
        4. Conversation Agent → suggested first reply
        5. Follow-up Agent → build nurture sequence
        """
        # Step 1: Capture & normalise
        capture_result = await self._run_agent(
            "lead_capture",
            self.lead_capture.run(
                raw_name=raw_name,
                source=source,
                email=email,
                phone=phone,
                company=company,
                raw_message=raw_message,
            ),
        )

        normalised = capture_result.output
        if not normalised:
            return {"error": capture_result.error, "step": "lead_capture"}

        # Step 2: Qualify
        qualify_result = await self._run_agent(
            "lead_qualification",
            self.lead_qualification.run(
                name=normalised.name,
                source=source,
                email=normalised.email,
                phone=normalised.phone,
                company=normalised.company,
                message=raw_message,
                target_customer_profile=target_customer_profile,
            ),
        )

        qualification = qualify_result.output

        # Step 3: CRM stage decision
        crm_result = await self._run_agent(
            "crm_pipeline",
            self.crm_pipeline.run(
                lead_name=normalised.name,
                current_stage="new",
                lead_score=qualification.score if qualification else 0,
                lead_label=qualification.label if qualification else "cold",
                source=source,
                days_in_current_stage=0,
                last_message=raw_message,
            ),
        ) if qualification else AgentRunResult("crm_pipeline", None, "skipped")

        # Step 4: Conversation reply
        conv_result = await self._run_agent(
            "conversation",
            self.conversation.run(
                customer_message=raw_message or f"Hi, I'm interested in learning more.",
                channel="website_chat",
                business_name=business_name,
                business_type=business_type,
                customer_name=normalised.first_name,
            ),
        ) if raw_message else AgentRunResult("conversation", None, "no_message")

        # Step 5: Follow-up sequence
        followup_result = await self._run_agent(
            "followup",
            self.followup.run(
                lead_status=qualification.label if qualification else "cold",
                business_name=business_name,
                offer=business_type,
                num_steps=5,
                sequence_type="new_lead",
            ),
        )

        return {
            "capture": capture_result.output.model_dump() if capture_result.success else None,
            "qualification": qualify_result.output.model_dump() if qualify_result.success else None,
            "crm_decision": crm_result.output.model_dump() if crm_result.success else None,
            "suggested_reply": conv_result.output.model_dump() if conv_result.success else None,
            "followup_sequence": followup_result.output.model_dump() if followup_result.success else None,
            "errors": {
                k: v.error for k, v in [
                    ("capture", capture_result),
                    ("qualification", qualify_result),
                    ("crm", crm_result),
                    ("conversation", conv_result),
                    ("followup", followup_result),
                ] if v.error and v.error not in ("skipped", "no_message")
            },
        }

    async def run_campaign_launch_workflow(
        self,
        business_name: str,
        campaign_goal: str,
        topic: str,
        target_audience: str,
        budget: int,
        channels: list[str],
        industry: str = "General",
        offer: Optional[str] = None,
        duration_weeks: int = 4,
    ) -> dict:
        """
        Campaign launch workflow:
        1. Campaign Agent → plan
        2. Content Agent → content
        3. Design Brief Agent → creatives
        """
        import asyncio

        campaign_coro = self.campaign.run(
            business_name=business_name,
            campaign_goal=campaign_goal,
            budget=budget,
            channels=channels,
            target_audience=target_audience,
            industry=industry,
            offer=offer,
            duration_weeks=duration_weeks,
        )
        content_coro = self.content.run(
            topic=topic,
            business_name=business_name,
            target_audience=target_audience,
            platforms=channels,
            campaign_objective=campaign_goal,
            offer_details=offer,
        )
        campaign_r, content_r = await asyncio.gather(
            self._run_agent("campaign", campaign_coro),
            self._run_agent("content", content_coro),
        )

        design_r = await self._run_agent(
            "design_brief",
            self.design_brief.run(
                campaign_name=campaign_r.output.campaign_name if campaign_r.success else campaign_goal,
                format_type="image_ad",
                platform=channels[0] if channels else "facebook",
                headline=content_r.output.headline if content_r.success else topic,
                target_audience=target_audience,
                campaign_objective=campaign_goal,
            ),
        )

        return {
            "campaign_plan": campaign_r.output.model_dump() if campaign_r.success else None,
            "content": content_r.output.model_dump() if content_r.success else None,
            "design_brief": design_r.output.model_dump() if design_r.success else None,
            "errors": {
                k: v.error for k, v in [
                    ("campaign", campaign_r),
                    ("content", content_r),
                    ("design", design_r),
                ] if v.error
            },
        }
