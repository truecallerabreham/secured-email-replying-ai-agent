from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse

from backend.app.dependencies import get_auth_service, get_current_session, get_session_store, get_settings
from backend.app.config import Settings
from backend.app.schemas import AppSession, AuthStatus
from backend.app.services.google_auth import GoogleAuthService
from backend.app.services.session import InMemorySessionStore

router = APIRouter()


@router.get("/login")
def login(auth_service: GoogleAuthService = Depends(get_auth_service)) -> RedirectResponse:
    return RedirectResponse(auth_service.build_login_url())


@router.get("/callback")
async def auth_callback(
    code: str,
    auth_service: GoogleAuthService = Depends(get_auth_service),
    session_store: InMemorySessionStore = Depends(get_session_store),
) -> RedirectResponse:
    session_token = await auth_service.create_owner_session(code, session_store)
    redirect_target = f"{auth_service.settings.frontend_url}/auth/callback?token={session_token}"
    return RedirectResponse(redirect_target)


@router.get("/me", response_model=AuthStatus)
def me(
    session: AppSession = Depends(get_current_session),
    settings: Settings = Depends(get_settings),
) -> AuthStatus:
    return AuthStatus(
        authenticated=True,
        email=session.email,
        owner_email=settings.app_owner_email,
    )


@router.post("/logout", response_model=AuthStatus)
def logout(
    session: AppSession = Depends(get_current_session),
    session_store: InMemorySessionStore = Depends(get_session_store),
) -> AuthStatus:
    if not session_store.delete_session(session.session_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found.")
    return AuthStatus(authenticated=False)
