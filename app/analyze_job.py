import json

from app.config import PROJECT_ROOT
from app.services.job_analyzer import analyze_job


def main() -> int:
    job_path = PROJECT_ROOT / "data" / "jobs" / "sample_job.txt"

    try:
        job_description = job_path.read_text(encoding="utf-8")
    except OSError as error:
        print(f"Could not read job description: {error}")
        return 1

    print("Analyzing the job with Ollama...")
    print("On a CPU, the first response may take some time.")

    try:
        result = analyze_job(job_description)
    except Exception as error:
        print(f"Analysis failed ({type(error).__name__}): {error}")
        return 1

    print("\nJob analysis:")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())