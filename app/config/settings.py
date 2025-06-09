import os
from dataclasses import dataclass
from dotenv import load_dotenv

env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

@dataclass
class AIConfig:
    api_key: str
    model_name: str = "learnlm-2.0-flash-experimental"
    response_mime_type: str = "text/plain"
    timeout: int = 30
    max_retries: int = 3

@dataclass
class AppConfig:
    ai_config: AIConfig
    debug: bool = False
    log_level: str = "INFO"
    max_workers: int = 4
    request_timeout: int = 300

def load_config() -> AppConfig:
    ai_config = AIConfig(
        api_key=os.getenv("GENAI_API_KEY", "your_api_key_here"),
        model_name=os.getenv("GENAI_MODEL", "learnlm-2.0-flash-experimental")
    )
    
    return AppConfig(
        ai_config=ai_config,
        debug=os.getenv("DEBUG", "False").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        max_workers=int(os.getenv("MAX_WORKERS", "4")),
        request_timeout=int(os.getenv("REQUEST_TIMEOUT", "300"))
    )