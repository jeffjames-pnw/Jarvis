from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Jarvis"
    debug: bool = False

    # LLM — bump to sonnet for tool-calling reliability
    model_name: str = "claude-sonnet-4-6"

    # ChromaDB — embedded persistent client; set path via env var
    chroma_path: str = "./chroma_data"

    # GitHub
    github_token: str = ""

    # Microsoft (OneNote via Graph API)
    microsoft_client_id: str = ""
    microsoft_refresh_token: str = ""


settings = Settings()
