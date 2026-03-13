"""Chatbot Router — platform support chatbot with streaming"""
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.core.dependencies import CurrentTenant
from app.agents.chatbot_agent import ChatbotAgent

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])

_chatbot = ChatbotAgent()


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=1000)
    conversation_history: Optional[list[dict]] = None


class ChatResponse(BaseModel):
    reply: str
    is_safe: bool = True


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, tenant: CurrentTenant):
    """Send a message to the SRP AI Marketing Manager support chatbot."""
    try:
        reply = await _chatbot.chat(
            message=payload.message,
            conversation_history=payload.conversation_history,
        )
        return {"reply": reply, "is_safe": True}
    except ValueError as e:
        # Safety guardrail triggered
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chatbot unavailable: {str(e)}")


@router.post("/chat/stream")
async def chat_stream(payload: ChatRequest, tenant: CurrentTenant):
    """Stream a response from the SRP AI support chatbot (Server-Sent Events)."""

    async def event_generator() -> AsyncGenerator[str, None]:
        try:
            async for chunk in _chatbot.chat_stream(
                message=payload.message,
                conversation_history=payload.conversation_history,
            ):
                # SSE format
                yield f"data: {chunk}\n\n"
        except ValueError as e:
            yield f"data: [ERROR] {str(e)}\n\n"
        except Exception as e:
            yield f"data: [ERROR] Chatbot unavailable: {str(e)}\n\n"
        finally:
            yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/welcome")
async def welcome_message():
    """Return the chatbot welcome message (no auth required)."""
    return {
        "message": (
            "Hi! I'm the SRP AI Marketing Manager assistant. I can help you understand "
            "this platform — features, how to use it, pricing plans, and marketing tips. "
            "What would you like to know?"
        ),
        "suggestions": [
            "What can this platform do?",
            "How do the AI agents work?",
            "How do I generate my first campaign?",
            "What's the difference between plans?",
        ],
    }
