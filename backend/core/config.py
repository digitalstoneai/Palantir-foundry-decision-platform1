import os
from enum import Enum
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BACKEND_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BACKEND_DIR / os.getenv("DATABASE_URL", "./db/foundry.db").lstrip("./")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


class TaskComplexity(str, Enum):
    REASONING = "reasoning"
    FAST = "fast"


MODEL_MAP: dict[TaskComplexity, str] = {
    TaskComplexity.REASONING: os.getenv("AI_MODEL_REASONING", "claude-sonnet-4-6"),
    TaskComplexity.FAST: os.getenv("AI_MODEL_FAST", "claude-haiku-4-5-20251001"),
}


def resolve_model(complexity: TaskComplexity) -> str:
    return MODEL_MAP[complexity]
