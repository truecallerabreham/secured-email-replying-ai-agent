from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    status: str
    owner_email: str
    gmail_configured: bool
    gemini_configured: bool
    supabase_configured: bool
    missing_settings: list[str] = Field(default_factory=list)


class AuthStatus(BaseModel):
    authenticated: bool
    email: str | None = None
    owner_email: str | None = None


class EmailMessage(BaseModel):
    message_id: str
    gmail_message_id: str
    from_address: str
    to_address: str | None = None
    subject: str
    body: str
    snippet: str
    received_at: str | None = None
    in_reply_to: str | None = None
    references: str | None = None


class EmailThread(BaseModel):
    id: str
    gmail_thread_id: str
    subject: str
    participants: list[str]
    snippet: str
    latest_from: str
    latest_received_at: str | None = None
    messages: list[EmailMessage] = Field(default_factory=list)


class DraftReplyResponse(BaseModel):
    draft_id: str | None = None
    thread_id: str
    model_name: str
    draft_text: str
    storage_backend: str
    retrieval_sources: list[str] = Field(default_factory=list)


class SendReplyRequest(BaseModel):
    draft_id: str | None = None
    final_text: str = Field(min_length=1)


class SendReplyResponse(BaseModel):
    sent_reply_id: str | None = None
    gmail_message_id: str
    thread_id: str
    storage_backend: str
    sent_at: str


class PersistenceRecord(BaseModel):
    id: str
    storage_backend: str


class AppSession(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    session_id: str
    email: str
    access_token: str
    refresh_token: str | None = None
    expires_at: float | None = None
    created_at: float


class OAuthTokenPayload(BaseModel):
    access_token: str
    refresh_token: str | None = None
    expires_in: int | None = None
    id_token: str | None = None
    token_type: str | None = None


class GoogleUser(BaseModel):
    email: str
    verified_email: bool = False
    name: str | None = None
    picture: str | None = None


class SupabaseInsertResult(BaseModel):
    id: str
    payload: dict[str, Any] = Field(default_factory=dict)
