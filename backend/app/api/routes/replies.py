from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.dependencies import (
    get_current_session,
    get_gemini_service,
    get_gmail_service,
    get_persistence_service,
)
from backend.app.schemas import AppSession, DraftReplyResponse, SendReplyRequest, SendReplyResponse
from backend.app.services.gemini import GeminiService
from backend.app.services.gmail import GmailService
from backend.app.services.persistence import PersistenceService

router = APIRouter()


@router.post("/threads/{thread_id}/draft", response_model=DraftReplyResponse)
async def generate_draft(
    thread_id: str,
    session: AppSession = Depends(get_current_session),
    gmail_service: GmailService = Depends(get_gmail_service),
    gemini_service: GeminiService = Depends(get_gemini_service),
    persistence_service: PersistenceService = Depends(get_persistence_service),
) -> DraftReplyResponse:
    thread = gmail_service.get_thread(session, thread_id)
    if not thread:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found.")

    draft_text = await gemini_service.generate_draft(thread)
    record = persistence_service.save_draft(thread=thread, draft_text=draft_text, model_name=gemini_service.model_name)

    return DraftReplyResponse(
        draft_id=record.id if record else None,
        thread_id=thread.id,
        model_name=gemini_service.model_name,
        draft_text=draft_text,
        storage_backend=persistence_service.backend_name,
        retrieval_sources=[],
    )


@router.post("/threads/{thread_id}/send", response_model=SendReplyResponse)
def send_reply(
    thread_id: str,
    request: SendReplyRequest,
    session: AppSession = Depends(get_current_session),
    gmail_service: GmailService = Depends(get_gmail_service),
    persistence_service: PersistenceService = Depends(get_persistence_service),
) -> SendReplyResponse:
    thread = gmail_service.get_thread(session, thread_id)
    if not thread:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread not found.")

    gmail_message_id = gmail_service.send_reply(session, thread, request.final_text)
    record = persistence_service.save_sent_reply(
        thread=thread,
        draft_id=request.draft_id,
        final_text=request.final_text,
        gmail_message_id=gmail_message_id,
    )

    return SendReplyResponse(
        sent_reply_id=record.id if record else None,
        gmail_message_id=gmail_message_id,
        thread_id=thread.id,
        storage_backend=persistence_service.backend_name,
        sent_at=datetime.now(UTC).isoformat(),
    )
