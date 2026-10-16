import hashlib
import json
from pathlib import Path

from app.config import OLLAMA_MODEL, PROJECT_ROOT
from app.schemas import JobAnalysis


CACHE_DIR = PROJECT_ROOT / "data" / "analysis_cache"

# Increase this when you change the extraction prompt or schema.
ANALYSIS_VERSION = "1"


def get_cache_path(job_description: str) -> Path:
    identity = {
        "description": job_description,
        "model": OLLAMA_MODEL,
        "analysis_version": ANALYSIS_VERSION,
        "schema": JobAnalysis.model_json_schema(),
    }

    serialized = json.dumps(
        identity,
        sort_keys=True,
        ensure_ascii=False,
    )

    fingerprint = hashlib.sha256(
        serialized.encode("utf-8")
    ).hexdigest()

    return CACHE_DIR / f"{fingerprint}.json"


def load_analysis(job_description: str) -> JobAnalysis | None:
    cache_path = get_cache_path(job_description)

    if not cache_path.is_file():
        return None

    return JobAnalysis.model_validate_json(
        cache_path.read_text(encoding="utf-8")
    )


def save_analysis(
    job_description: str,
    analysis: JobAnalysis,
) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    cache_path = get_cache_path(job_description)
    temporary_path = cache_path.with_suffix(".tmp")

    temporary_path.write_text(
        analysis.model_dump_json(indent=2),
        encoding="utf-8",
    )

    temporary_path.replace(cache_path)