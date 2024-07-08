from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel

from pydantic_settings import BaseSettings, SettingsConfigDict

PATH = Path(__file__).parent

load_dotenv()


class PostgresSubModel(BaseModel):
    user: str = "admin"
    password: str = "admin"
    db: str = "mbc_bd"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f"{PATH}/../../.env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        frozen=True,
    )

    postgres: PostgresSubModel
    api_db_echo: bool = False
    api_v1_prefix: str = "/api"


settings = Settings()
