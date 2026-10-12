from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "secret_keys123"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = "sqlite:///./secure_api.db"
    APP_NAME: str = "Secure REST API"
    DEBUG: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
