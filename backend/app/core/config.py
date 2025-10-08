import os
from pydantic import BaseSettings


class Settings(BaseSettings):
    ENV: str = os.getenv("ENV", "development")
    API_PREFIX: str = "/api/v1"
    QWEN_IMAGE_MODEL: str = os.getenv("QWEN_IMAGE_MODEL", "Qwen/Qwen2-VL-2B-Instruct")
    AI_DEVICE: str = os.getenv("AI_DEVICE", "")
    SAM_MODEL_PATH: str = os.getenv("SAM_MODEL_PATH", "/app/models/sam/sam_vit_b_01ec64.pth")

    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    POSTGRES_DSN: str = os.getenv("POSTGRES_DSN", "postgresql://postgres:postgres@db:5432/retouch")


settings = Settings()
