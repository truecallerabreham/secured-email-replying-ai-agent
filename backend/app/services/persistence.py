from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from supabase import Client, create_client

from backend.app.config import Settings
from backend.app.schemas import EmailThread, PersistenceRecord


class PersistenceService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._local_drafts: dict[str, dict[str, Any]] = {}
        self._local_sent_replies: dict[str, dict[str, Any]] = {}
        self.client: Client | None = None
        self.backend_name = "memory"

        if settings.supabase_url and settings.supabase_service_role_key:
            self.client = create_client(settings.supabase_url, settings.supabase_service_role_key)
            self.backend_name = "supabase"

    def save_draft(self, *, thread: EmailThread, draft_text: str, model_name: str) -> PersistenceRecord:
        payload = {
            "gmail_thread_id": thread.gmail_thread_id,
            "thread_snapshot": thread.model_dump(mode="json"),
            "draft_text": draft_text,
            "model_name": model_name,
            "retrieval_context": [],
            "created_at": datetime.now(UTC).isoformat(),
        }
        return self._insert("draft_replies", self._local_drafts, payload)

    def save_sent_reply(
        self,
        *,
        thread: EmailThread,
        draft_id: str | None,
        final_text: str,
        gmail_message_id: str,
    ) -> PersistenceRecord:
        payload = {
            "draft_reply_id": draft_id,
            "gmail_thread_id": thread.gmail_thread_id,
            "thread_snapshot": thread.model_dump(mode="json"),
            "final_text": final_text,
            "gmail_sent_message_id": gmail_message_id,
            "sent_at": datetime.now(UTC).isoformat(),
        }
        return self._insert("sent_replies", self._local_sent_replies, payload)

    def _insert(
        self,
        table_name: str,
        local_store: dict[str, dict[str, Any]],
        payload: dict[str, Any],
    ) -> PersistenceRecord:
        if self.client:
            inserted = self.client.table(table_name).insert(payload).execute()
            inserted_id = inserted.data[0]["id"]
            return PersistenceRecord(id=str(inserted_id), storage_backend=self.backend_name)

        local_id = str(uuid.uuid4())
        local_store[local_id] = {"id": local_id, **payload}
        return PersistenceRecord(id=local_id, storage_backend=self.backend_name)
