import os
from dataclasses import dataclass
from dotenv import load_dotenv
from google.genai import types

from app.config.response_configuration import ResponseConfiguration


env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

@dataclass
class AIConfig:
    api_key: str
    model_name: str = "learnlm-2.0-flash-experimental"
    response_mime_type: str = "text/plain"
    timeout: int = 30
    max_retries: int = 3

    def __generation_config__(self, advanced_response_schema=None) -> types.GenerateContentConfig:
        import json
        # Load the response schema 
        config_file = "app/config/response_config.json"
        with open(config_file, 'r') as f:
            config = json.load(f)
            response_schema = config['response_schema']
        # build the response configuration
        if not response_schema:
            raise ValueError("Response schema is required for content generation configuration.")
        
        response_configuration = ResponseConfiguration(response_schema=response_schema)
        
        if advanced_response_schema is None:
            return types.GenerateContentConfig(
                # system_instruction="You are a helpful AI assistant.",
                temperature=0.5, # balanced creativity
                top_p=0.95, # standard and safe value. It cuts off the least likely, often nonsensical, word choices.
                top_k=40, # limits the sampling pool to the 40 most likely words. Works well with the temperature.
                candidate_count=1, # i want only one candidate
                response_mime_type=response_configuration.get_response_mime_type(),
                response_schema=response_configuration.get_response_schema(),
            )
        else:
            return types.GenerateContentConfig(
                # system_instruction="You are a helpful AI assistant.",
                temperature=0.5, # balanced creativity
                top_p=0.95, # standard and safe value. It cuts off the least likely, often nonsensical, word choices.
                top_k=40, # limits the sampling pool to the 40 most likely words. Works well with the temperature.
                candidate_count=1, # i want only one candidate
                response_mime_type=response_configuration.get_response_mime_type(),
                response_schema=advanced_response_schema,
            )
    
    def __content_config__(self, prompt: str) -> list[types.Content]:
        return [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text=prompt),
                ],
            ),
        ]


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