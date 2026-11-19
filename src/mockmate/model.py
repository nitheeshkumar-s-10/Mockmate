from langchain.chat_models import init_chat_model
from .config import load_settings


def build_model():
    settings = load_settings()
    kwargs = {
        "model": settings.model_name,
        "model_provider": settings.model_provider,
        "api_key": settings.model_api_key,
        "temperature": settings.temperature,
        "timeout": 90,
        "max_retries": 2,
    }
    if settings.model_base_url:
        kwargs["base_url"] = settings.model_base_url
    return init_chat_model(**kwargs)
