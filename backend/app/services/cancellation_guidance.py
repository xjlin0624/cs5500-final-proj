import json
from functools import lru_cache
from pathlib import Path


_GUIDANCE_PATH = Path(__file__).resolve().parents[1] / "data" / "cancellation_guidance.json"


@lru_cache(maxsize=1)
def load_cancellation_guidance() -> dict[str, dict]:
    data = json.loads(_GUIDANCE_PATH.read_text(encoding="utf-8"))
    return {entry["retailer"].lower(): entry for entry in data}


def get_cancellation_guidance(retailer: str) -> dict | None:
    return load_cancellation_guidance().get(retailer.lower())
