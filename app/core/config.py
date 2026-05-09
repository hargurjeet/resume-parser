from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    fireworks_api_key: str = ""
    fireworks_model_id: str = "accounts/fireworks/models/llama-v3p3-70b-instruct"
    fireworks_base_url: str = "https://api.fireworks.ai/inference/v1"

settings = Settings()
