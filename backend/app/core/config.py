from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Health Platform API"
    supabase_url: str = ""
    supabase_anon_key: str = ""
    frontend_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


settings = Settings()
