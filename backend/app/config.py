import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from langchain_core.embeddings import Embeddings

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")          # found regardless of which directory you run from

# .strip() everywhere: a key pasted into a dashboard with a trailing newline makes an illegal
# HTTP header, which the openai SDK reports as the very unhelpful "Connection error."
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
OPENROUTER_URL = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1").strip()
LLM_MODEL = os.getenv("LLM_MODEL", "nvidia/nemotron-3-super-120b-a12b:free").strip()
# Free models run on a shared upstream pool and return 429 without warning. OpenRouter routes
# to the next model in this list when that happens. All must support tool calling.
FALLBACK_MODELS = [m.strip() for m in os.getenv(
    "FALLBACK_MODELS",
    "nvidia/nemotron-3-nano-30b-a3b:free,nvidia/nemotron-nano-9b-v2:free").split(",") if m.strip()]
CHROMA_DIR = os.getenv("CHROMA_DIR", str(BASE_DIR / ".chroma"))
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR / 'orders.db'}")
ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "demo-token")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
DEFAULT_BUSINESS = os.getenv("DEFAULT_BUSINESS", "tinyd_lights")


# --- LLM adapter: swap providers by editing this function. ---
def get_llm(temperature: float = 0.3):
    """OpenRouter speaks the OpenAI API, so ChatOpenAI + a base_url is the whole integration.
    Pick any tool-calling model in LLM_MODEL (openai/gpt-4o-mini, anthropic/claude-*, ...)."""
    from langchain_openai import ChatOpenAI

    if not OPENROUTER_API_KEY:
        raise RuntimeError(
            "OPENROUTER_API_KEY is not set. Locally: put it in backend/.env (see .env.example). "
            "On Railway: add it as an environment variable. Get one at "
            "https://openrouter.ai/keys"
        )
    return ChatOpenAI(
        model=LLM_MODEL,
        api_key=OPENROUTER_API_KEY,
        base_url=OPENROUTER_URL,
        temperature=temperature,
        # A 3-line WhatsApp reply plus the order slots. Left unset, langchain asks for the
        # model's whole window and OpenRouter rejects it against a small credit balance.
        max_tokens=int(os.getenv("MAX_TOKENS", "1024")),
        extra_body={"models": [LLM_MODEL, *FALLBACK_MODELS]},
    )


class _LocalEmbeddings(Embeddings):
    """all-MiniLM-L6-v2 via the ONNX runtime that ships with chromadb.

    OpenRouter has no embeddings endpoint, and a 40-chunk catalog doesn't need a hosted
    model. Downloads ~80MB once, then runs offline and free.
    """

    def __init__(self) -> None:
        from chromadb.utils.embedding_functions import DefaultEmbeddingFunction

        self._fn = DefaultEmbeddingFunction()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[float(x) for x in vector] for vector in self._fn(texts)]

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]


@lru_cache
def get_embeddings() -> Embeddings:
    return _LocalEmbeddings()
