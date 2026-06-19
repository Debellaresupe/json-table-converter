from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "JSON Table Converter"
    max_json_bytes: int = Field(default=10 * 1024 * 1024)
    max_depth: int = 80
    preview_limit: int = 100
    max_rows: int = 100_000
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]


settings = Settings()
