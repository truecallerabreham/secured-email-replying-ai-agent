from __future__ import annotations

from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import httpx
from fastapi import HTTPException, status

from backend.app.config import Settings
from backend.app.schemas import GoogleUser, OAuthTokenPayload
from backend.app.services.session import InMemorySessionStore


class GoogleAuthService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def build_login_url(self) -> str:
        if not self.settings.google_oauth_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "Google OAuth is not fully configured. "
                    f"Missing or placeholder values: {', '.join(self.settings.missing_local_setup())}"
                ),
            )

        query = urlencode(
            {
                "client_id": self.settings.google_client_id,
                "redirect_uri": self.settings.google_redirect_uri,
                "response_type": "code",
                "scope": " ".join(self.settings.scope_list()),
                "access_type": "offline",
                "include_granted_scopes": "true",
                "prompt": "consent",
            }
        )
        return f"{self.settings.google_auth_uri}?{query}"

    async def create_owner_session(self, code: str, session_store: InMemorySessionStore) -> str:
        if not self.settings.google_oauth_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    "Google OAuth is not fully configured. "
                    f"Missing or placeholder values: {', '.join(self.settings.missing_local_setup())}"
                ),
            )

        tokens = await self.exchange_code(code)
        user = await self.fetch_user(tokens.access_token)

        if user.email.lower() != self.settings.app_owner_email.lower():
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the owner can access this app.")

        expires_at = None
        if tokens.expires_in:
            expires_at = (datetime.now(UTC) + timedelta(seconds=tokens.expires_in - 60)).timestamp()

        return session_store.create_session(
            email=user.email,
            access_token=tokens.access_token,
            refresh_token=tokens.refresh_token,
            expires_at=expires_at,
        )

    async def exchange_code(self, code: str) -> OAuthTokenPayload:
        payload = {
            "code": code,
            "client_id": self.settings.google_client_id,
            "client_secret": self.settings.google_client_secret,
            "redirect_uri": self.settings.google_redirect_uri,
            "grant_type": "authorization_code",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(self.settings.google_token_uri, data=payload)

        if response.is_error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Google token exchange failed: {response.text}",
            )

        return OAuthTokenPayload.model_validate(response.json())

    async def fetch_user(self, access_token: str) -> GoogleUser:
        headers = {"Authorization": f"Bearer {access_token}"}
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.settings.google_userinfo_uri, headers=headers)

        if response.is_error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Google user lookup failed: {response.text}",
            )

        return GoogleUser.model_validate(response.json())
