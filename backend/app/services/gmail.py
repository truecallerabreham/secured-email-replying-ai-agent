from __future__ import annotations

import base64
from email.mime.text import MIMEText

from fastapi import HTTPException, status
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from backend.app.config import Settings
from backend.app.schemas import AppSession, EmailMessage, EmailThread


class GmailService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def list_primary_threads(self, session: AppSession, limit: int = 10) -> list[EmailThread]:
        gmail = self._build_gmail_client(session)
        response = gmail.users().threads().list(userId="me", q="category:primary", maxResults=limit).execute()
        threads = response.get("threads", [])
        return [self._fetch_thread(gmail, thread["id"]) for thread in threads]

    def get_thread(self, session: AppSession, thread_id: str) -> EmailThread | None:
        gmail = self._build_gmail_client(session)
        return self._fetch_thread(gmail, thread_id)

    def send_reply(self, session: AppSession, thread: EmailThread, body: str) -> str:
        gmail = self._build_gmail_client(session)
        latest_message = thread.messages[-1]
        subject = latest_message.subject
        if not subject.lower().startswith("re:"):
            subject = f"Re: {subject}"

        mime_message = MIMEText(body)
        mime_message["to"] = latest_message.from_address
        mime_message["subject"] = subject
        if latest_message.in_reply_to:
            mime_message["In-Reply-To"] = latest_message.in_reply_to
        if latest_message.references:
            mime_message["References"] = latest_message.references

        raw_message = base64.urlsafe_b64encode(mime_message.as_bytes()).decode()
        payload = {"raw": raw_message, "threadId": thread.gmail_thread_id}
        sent = gmail.users().messages().send(userId="me", body=payload).execute()
        return sent["id"]

    def _build_gmail_client(self, session: AppSession):
        if not self.settings.google_client_id or not self.settings.google_client_secret:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Google client credentials are missing.",
            )

        credentials = Credentials(
            token=session.access_token,
            refresh_token=session.refresh_token,
            token_uri=self.settings.google_token_uri,
            client_id=self.settings.google_client_id,
            client_secret=self.settings.google_client_secret,
            scopes=self.settings.scope_list(),
        )
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(GoogleRequest())
        return build("gmail", "v1", credentials=credentials, cache_discovery=False)

    def _fetch_thread(self, gmail, thread_id: str) -> EmailThread:
        raw_thread = gmail.users().threads().get(userId="me", id=thread_id, format="full").execute()
        messages = [self._normalize_message(item) for item in raw_thread.get("messages", [])]
        if not messages:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thread has no messages.")

        latest = messages[-1]
        participants = list({message.from_address for message in messages})
        return EmailThread(
            id=thread_id,
            gmail_thread_id=raw_thread["id"],
            subject=latest.subject,
            participants=participants,
            snippet=raw_thread.get("snippet", ""),
            latest_from=latest.from_address,
            latest_received_at=latest.received_at,
            messages=messages,
        )

    def _normalize_message(self, raw_message: dict) -> EmailMessage:
        payload = raw_message.get("payload", {})
        headers = payload.get("headers", [])
        subject = self._header(headers, "Subject")
        message_id_header = self._header(headers, "Message-Id")
        body = self._extract_plain_text(payload)
        return EmailMessage(
            message_id=raw_message.get("id", ""),
            gmail_message_id=raw_message.get("id", ""),
            from_address=self._header(headers, "From"),
            to_address=self._header(headers, "To"),
            subject=subject,
            body=body or raw_message.get("snippet", ""),
            snippet=raw_message.get("snippet", ""),
            received_at=self._header(headers, "Date"),
            in_reply_to=message_id_header,
            references=self._header(headers, "References"),
        )

    def _extract_plain_text(self, payload: dict) -> str:
        if payload.get("mimeType") == "text/plain":
            return self._decode(payload.get("body", {}).get("data"))

        for part in payload.get("parts", []) or []:
            if part.get("mimeType") == "text/plain":
                return self._decode(part.get("body", {}).get("data"))
            nested = self._extract_plain_text(part)
            if nested:
                return nested
        return ""

    @staticmethod
    def _decode(data: str | None) -> str:
        if not data:
            return ""
        padded = data + "=" * (-len(data) % 4)
        return base64.urlsafe_b64decode(padded.encode("utf-8")).decode("utf-8", errors="ignore")

    @staticmethod
    def _header(headers: list[dict], name: str) -> str:
        for header in headers:
            if header.get("name", "").lower() == name.lower():
                return header.get("value", "")
        return ""
