from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
WORKSPACE_DIR = ROOT_DIR / "workspace"
SESSIONS_DIR = WORKSPACE_DIR / "sessions"
WEAK_TOPICS_FILE = WORKSPACE_DIR / "weak-topics.md"
CHECKPOINT_DB = WORKSPACE_DIR / "mockmate_checkpoints.sqlite"


@dataclass(frozen=True)
class Settings:
    model_provider: str
    model_name: str
    model_api_key: str
    model_base_url: str | None
    temperature: float


def load_settings() -> Settings:
    load_dotenv(ROOT_DIR / ".env")
    provider = os.getenv("MODEL_PROVIDER", "").strip()
    name = os.getenv("MODEL_NAME", "").strip()
    key = os.getenv("MODEL_API_KEY", "").strip()
    base_url = os.getenv("MODEL_BASE_URL", "").strip() or None
    if not provider or not name or not key:
        raise RuntimeError(
            "Model configuration is incomplete. Copy .env.example to .env and set "
            "MODEL_PROVIDER, MODEL_NAME, and MODEL_API_KEY."
        )
    try:
        temperature = float(os.getenv("MODEL_TEMPERATURE", "0.2"))
    except ValueError as exc:
        raise RuntimeError("MODEL_TEMPERATURE must be a number.") from exc
    return Settings(provider, name, key, base_url, temperature)


def ensure_workspace() -> None:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
