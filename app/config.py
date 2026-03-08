from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./test.db"
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 300

    model_config = {"env_file": ".env"}


settings = Settings()
