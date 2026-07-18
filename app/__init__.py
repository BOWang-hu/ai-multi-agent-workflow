"""
多 Agent 工作流系统 - 配置模块
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_base_url: str = field(default_factory=lambda: os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    openai_model_name: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"))

    app_host: str = field(default_factory=lambda: os.getenv("APP_HOST", "0.0.0.0"))
    app_port: int = int(os.getenv("APP_PORT", "8000"))

    max_iterations: int = int(os.getenv("MAX_ITERATIONS", "10"))

    @property
    def is_api_key_set(self) -> bool:
        return bool(self.openai_api_key) and self.openai_api_key != "sk-your-api-key-here"


settings = Settings()
