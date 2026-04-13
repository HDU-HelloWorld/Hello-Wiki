import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str
    app_env: str


def load_settings() -> Settings:
    return Settings(
        app_name=os.getenv("HELLO_WIKI_APP_NAME", "Hello Wiki Backend"),
        app_env=os.getenv("HELLO_WIKI_APP_ENV", "dev"),
    )


settings = load_settings()
