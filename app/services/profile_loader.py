from pathlib import Path

from app.schemas import CandidateProfile


def load_profile(file_path: Path) -> CandidateProfile:
    if not file_path.is_file():
        raise FileNotFoundError(
            f"Candidate profile not found: {file_path}"
        )

    content = file_path.read_text(encoding="utf-8")

    return CandidateProfile.model_validate_json(content)