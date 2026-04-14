# -*- coding: utf-8 -*-
# 编码修复: config.py - 已替换Unicode符号避免Windows编码问题
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
