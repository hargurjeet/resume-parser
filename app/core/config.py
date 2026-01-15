from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    aws_region: str = "eu-west-2"
    bedrock_model_id: str = "anthropic.claude-3-7-sonnet-20250219-v1:0"

    class Config:
        env_file = ".env"

settings = Settings()
