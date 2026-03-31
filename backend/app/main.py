from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.routes import auth, replies, threads
from backend.app.config import get_settings
from backend.app.schemas import HealthResponse
from backend.app.services.persistence import PersistenceService
from backend.app.services.session import InMemorySessionStore

settings = get_settings()

app = FastAPI(title=settings.app_name)
app.state.settings = settings
app.state.session_store = InMemorySessionStore(settings.session_secret)
app.state.persistence_service = PersistenceService(settings)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(threads.router, prefix="/api/threads", tags=["threads"])
app.include_router(replies.router, prefix="/api/replies", tags=["replies"])


@app.get("/api/health", response_model=HealthResponse)
def healthcheck() -> HealthResponse:
    return HealthResponse(
        status="ok",
        owner_email=settings.app_owner_email,
        gmail_configured=settings.google_oauth_configured(),
        gemini_configured=settings.gemini_configured(),
        supabase_configured=settings.supabase_configured(),
        missing_settings=settings.missing_local_setup(),
    )
