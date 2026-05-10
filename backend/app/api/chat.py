"""Teacher feedback chat API."""

import re
import uuid

from fastapi import APIRouter, Query, Request
from pydantic import BaseModel

from app.services.chat_service import chat_service
from app.services.integration_service import integration_service
from app.services.llm import LLMService

router = APIRouter(prefix="/api/chat")


class ChatMessage(BaseModel):
    content: str
    session_id: str | None = None
    decision_id: str | None = None


class ChatResponse(BaseModel):
    session_id: str
    message_id: str
    role: str
    content: str
    updated_decision_id: str | None = None


def _get_llm(request: Request) -> LLMService:
    return request.app.state.llm_service


@router.post("")
def send_message(request: Request, body: ChatMessage) -> ChatResponse:
    llm = _get_llm(request)

    session_id = body.session_id or f"ses_{uuid.uuid4().hex[:8]}"
    try:
        chat_service.get_session(session_id)
    except KeyError:
        chat_service.create_session(session_id=session_id, title="Teacher Feedback")

    chat_service.add_message(
        message_id=f"msg_{uuid.uuid4().hex[:8]}",
        session_id=session_id,
        role="user",
        content=body.content,
    )

    updated_decision_id = _apply_feedback_to_decision(body.content, body.decision_id)
    try:
        reply_text = llm.generate_text(
            f"The teacher said: {body.content}\n\n"
            "You are a helpful teaching assistant. Respond helpfully in Chinese. "
            "If an integration decision was modified, acknowledge the change and explain it briefly."
        )
    except Exception:
        reply_text = "已记录教师反馈。"

    if updated_decision_id:
        reply_text = f"已更新整合决策 {updated_decision_id}。\n\n{reply_text}"

    assistant_msg = chat_service.add_message(
        message_id=f"msg_{uuid.uuid4().hex[:8]}",
        session_id=session_id,
        role="assistant",
        content=reply_text,
    )

    return ChatResponse(
        session_id=session_id,
        message_id=assistant_msg.message_id,
        role="assistant",
        content=reply_text,
        updated_decision_id=updated_decision_id,
    )


@router.get("/history")
def get_history(session_id: str | None = Query(default=None)) -> dict:
    if not session_id:
        return {"session": None, "messages": []}
    try:
        session = chat_service.get_session(session_id)
    except KeyError:
        return {"session": None, "messages": []}
    messages = chat_service.list_messages(session_id)
    return {
        "session": session.model_dump(mode="json"),
        "messages": [message.model_dump(mode="json") for message in messages],
    }


def _apply_feedback_to_decision(content: str, explicit_decision_id: str | None) -> str | None:
    decision_id = explicit_decision_id or _extract_decision_id(content)
    if not decision_id:
        decisions = [d for d in integration_service.list_decisions() if d.status == "active"]
        if len(decisions) == 1:
            decision_id = decisions[0].decision_id
    if not decision_id:
        return None

    try:
        decision = integration_service.get_decision(decision_id)
    except KeyError:
        return None

    normalized = content.lower()
    reason = f"{decision.reason}\n教师反馈：{content}"

    if any(token in normalized for token in ["保留", "keep", "不要删除", "不应该被删除"]):
        integration_service.update_decision(
            decision_id,
            action="keep",
            reason=reason,
            status="teacher_modified",
            confidence=max(decision.confidence, 0.99),
        )
        return decision_id

    if any(token in normalized for token in ["拆分", "分开", "不是同一个", "split", "separate"]):
        integration_service.update_decision(
            decision_id,
            action="keep",
            reason=reason,
            status="teacher_split",
            confidence=max(decision.confidence, 0.99),
        )
        return decision_id

    if any(token in normalized for token in ["合并", "merge", "认为相同"]):
        integration_service.update_decision(
            decision_id,
            action="merge",
            reason=reason,
            status="teacher_modified",
            confidence=max(decision.confidence, 0.99),
        )
        return decision_id

    if any(token in normalized for token in ["删除", "remove", "冗余"]):
        integration_service.update_decision(
            decision_id,
            action="remove",
            reason=reason,
            status="teacher_modified",
            confidence=max(decision.confidence, 0.99),
        )
        return decision_id

    return None


def _extract_decision_id(content: str) -> str | None:
    match = re.search(r"\bdec_[a-zA-Z0-9]+\b", content)
    if match:
        return match.group(0)
    return None
