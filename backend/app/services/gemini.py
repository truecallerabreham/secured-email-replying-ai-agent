from __future__ import annotations

import httpx
from fastapi import HTTPException, status

from backend.app.config import Settings
from backend.app.schemas import EmailThread


class GeminiService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.model_name = settings.gemini_model

    async def generate_draft(self, thread: EmailThread) -> str:
        if not self.settings.gemini_configured():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Gemini API key is missing or still using a placeholder value.",
            )

        endpoint = f"{self.settings.gemini_api_base}/models/{self.model_name}:generateContent"
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": self._build_prompt(thread),
                        }
                    ]
                }
            ]
        }
        params = {"key": self.settings.gemini_api_key}
        async with httpx.AsyncClient(timeout=45.0) as client:
            response = await client.post(endpoint, params=params, json=payload)

        if response.is_error:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Gemini request failed: {response.text}",
            )

        data = response.json()
        candidates = data.get("candidates", [])
        try:
            return candidates[0]["content"]["parts"][0]["text"].strip()
        except (IndexError, KeyError, TypeError) as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Gemini returned an unexpected response format.",
            ) from exc

    def _build_prompt(self, thread: EmailThread) -> str:
        transcript = []
        for message in thread.messages:
            transcript.append(
                "\n".join(
                    [
                        f"From: {message.from_address}",
                        f"Subject: {message.subject}",
                        f"Date: {message.received_at or 'Unknown'}",
                        f"Body: {message.body}",
                    ]
                )
            )

        joined_transcript = "\n\n---\n\n".join(transcript)
        return (
            "You are drafting an email reply for the owner of a secure email assistant.\n"
            "Write a professional, concise response.\n"
            "Do not promise unavailable facts.\n"
            "If the sender is asking for details not present in the conversation, ask a clarifying follow-up.\n"
            "Return only the email body without markdown fences.\n\n"
            f"Email thread:\n{joined_transcript}"
        )
