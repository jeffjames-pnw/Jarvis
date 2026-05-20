from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Jarvis"
    debug: bool = False

    # LLM
    model_name: str = "claude-haiku-4-5-20251001"

    # ChromaDB — embedded persistent client; set path via env var
    chroma_path: str = "./chroma_data"


settings = Settings()
