from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str

    jwt_secret: str = "change-me-dev-secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 480

    llm_enabled: bool = False
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.6-flash"

    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
