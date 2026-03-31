from fastapi import APIRouter, Depends

from backend.app.dependencies import get_current_session, get_gmail_service
from backend.app.schemas import AppSession, EmailThread
from backend.app.services.gmail import GmailService

router = APIRouter()


@router.get("", response_model=list[EmailThread])
def list_threads(
    session: AppSession = Depends(get_current_session),
    gmail_service: GmailService = Depends(get_gmail_service),
) -> list[EmailThread]:
    return gmail_service.list_primary_threads(session)
