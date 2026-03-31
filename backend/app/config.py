from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file="backend/.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Secured Email Replying Agent API"
    app_env: str = "development"
    frontend_url: str = "http://localhost:3000"
    allowed_origins: str = "http://localhost:3000"
    app_owner_email: str = "owner@example.com"
    session_secret: str = "change-me"

    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/auth/callback"
    google_auth_uri: str = "https://accounts.google.com/o/oauth2/v2/auth"
    google_token_uri: str = "https://oauth2.googleapis.com/token"
    google_userinfo_uri: str = "https://openidconnect.googleapis.com/v1/userinfo"
    gmail_scopes: str = (
        "openid email profile "
        "https://www.googleapis.com/auth/gmail.modify "
        "https://www.googleapis.com/auth/gmail.send"
    )

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"
    gemini_api_base: str = "https://generativelanguage.googleapis.com/v1beta"

    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_db_schema: str = "public"

    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    def scope_list(self) -> list[str]:
        return [scope.strip() for scope in self.gmail_scopes.split() if scope.strip()]

    @staticmethod
    def _is_real_value(value: str, *, placeholders: tuple[str, ...] = ()) -> bool:
        normalized = value.strip()
        if not normalized:
            return False
        if normalized in placeholders:
            return False
        return not normalized.startswith("replace-with-")

    def owner_email_configured(self) -> bool:
        return self._is_real_value(self.app_owner_email, placeholders=("owner@example.com",))

    def session_secret_configured(self) -> bool:
        return self._is_real_value(self.session_secret, placeholders=("change-me",))

    def google_oauth_configured(self) -> bool:
        return all(
            [
                self._is_real_value(self.google_client_id),
                self._is_real_value(self.google_client_secret),
                self._is_real_value(self.google_redirect_uri),
                self.owner_email_configured(),
                self.session_secret_configured(),
            ]
        )

    def gemini_configured(self) -> bool:
        return self._is_real_value(self.gemini_api_key)

    def supabase_configured(self) -> bool:
        return all(
            [
                self._is_real_value(self.supabase_url, placeholders=("https://your-project.supabase.co",)),
                self._is_real_value(self.supabase_service_role_key),
            ]
        )

    def missing_local_setup(self) -> list[str]:
        missing: list[str] = []
        if not self.owner_email_configured():
            missing.append("APP_OWNER_EMAIL")
        if not self.session_secret_configured():
            missing.append("SESSION_SECRET")
        if not self._is_real_value(self.google_client_id):
            missing.append("GOOGLE_CLIENT_ID")
        if not self._is_real_value(self.google_client_secret):
            missing.append("GOOGLE_CLIENT_SECRET")
        if not self.gemini_configured():
            missing.append("GEMINI_API_KEY")
        return missing


@lru_cache
def get_settings() -> Settings:
    return Settings()
