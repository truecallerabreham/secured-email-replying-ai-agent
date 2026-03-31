from __future__ import annotations

import time
import uuid

from backend.app.schemas import AppSession
from backend.app.security import SessionTokenManager


class InMemorySessionStore:
    def __init__(self, secret_key: str) -> None:
        self.tokens = SessionTokenManager(secret_key)
        self.sessions: dict[str, AppSession] = {}

    def create_session(
        self,
        *,
        email: str,
        access_token: str,
        refresh_token: str | None,
        expires_at: float | None,
    ) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = AppSession(
            session_id=session_id,
            email=email,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=expires_at,
            created_at=time.time(),
        )
        return self.tokens.sign(session_id)

    def get_session(self, signed_token: str) -> AppSession | None:
        try:
            session_id = self.tokens.unsign(signed_token)
        except ValueError:
            return None

        session = self.sessions.get(session_id)
        if not session:
            return None

        if session.expires_at and session.expires_at <= time.time():
            self.sessions.pop(session_id, None)
            return None
        return session

    def update_session_tokens(
        self,
        session_id: str,
        *,
        access_token: str,
        expires_at: float | None,
        refresh_token: str | None = None,
    ) -> None:
        session = self.sessions.get(session_id)
        if not session:
            return

        session.access_token = access_token
        session.expires_at = expires_at
        if refresh_token:
            session.refresh_token = refresh_token

    def delete_session(self, session_id: str) -> bool:
        return self.sessions.pop(session_id, None) is not None
