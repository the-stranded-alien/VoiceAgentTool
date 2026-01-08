from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    #Supabase
    supabase_url: str
    supabase_publishable_key: str
    supabase_secret_key: str

    #Database
    database_url: str
    database_name: str
    database_password: str

    #Retell API
    retell_api_key: str = ""
    retell_webhook_secret_key: str = ""

    #LLM - Anthropic
    anthropic_api_key: str = ""
    llm_model: str = "claude-sonnet-4-20250514"
    llm_max_tokens: int = 4096
    llm_temperature: float = 0.1
    
    #LLM - OpenAI
    # openai_api_key: str = ""

    #Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()    