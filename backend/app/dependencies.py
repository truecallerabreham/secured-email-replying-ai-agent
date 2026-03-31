from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.app.config import Settings
from backend.app.schemas import AppSession
from backend.app.services.gmail import GmailService
from backend.app.services.gemini import GeminiService
from backend.app.services.google_auth import GoogleAuthService
from backend.app.services.persistence import PersistenceService
from backend.app.services.session import InMemorySessionStore

bearer_scheme = HTTPBearer(auto_error=False)


def get_settings(request: Request) -> Settings:
    return request.app.state.settings


def get_session_store(request: Request) -> InMemorySessionStore:
    return request.app.state.session_store


def get_auth_service(settings: Settings = Depends(get_settings)) -> GoogleAuthService:
    return GoogleAuthService(settings)


def get_gmail_service(settings: Settings = Depends(get_settings)) -> GmailService:
    return GmailService(settings)


def get_gemini_service(settings: Settings = Depends(get_settings)) -> GeminiService:
    return GeminiService(settings)


def get_persistence_service(request: Request) -> PersistenceService:
    return request.app.state.persistence_service


def get_current_session(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    session_store: InMemorySessionStore = Depends(get_session_store),
) -> AppSession:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing session token.")

    session = session_store.get_session(credentials.credentials)
    if not session:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session expired or invalid.")
    return session
