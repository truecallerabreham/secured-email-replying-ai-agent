from itsdangerous import BadSignature, URLSafeSerializer


class SessionTokenManager:
    def __init__(self, secret_key: str) -> None:
        self.serializer = URLSafeSerializer(secret_key, salt="secured-email-agent-session")

    def sign(self, session_id: str) -> str:
        return self.serializer.dumps({"sid": session_id})

    def unsign(self, token: str) -> str:
        try:
            payload = self.serializer.loads(token)
        except BadSignature as exc:
            raise ValueError("Invalid session token.") from exc

        session_id = payload.get("sid")
        if not session_id:
            raise ValueError("Missing session id.")
        return session_id
