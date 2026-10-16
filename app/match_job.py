import json

from app.config import PROJECT_ROOT
from app.schemas import JobAnalysis, JobCriteria
from app.services.criteria_checker import check_criteria
from app.services.job_analyzer import analyze_job
from app.services.matcher import match_job
from app.services.profile_loader import load_profile


def main() -> int:
    try:
        profile = load_profile(
            PROJECT_ROOT / "data" / "profile.json"
        )

        criteria = JobCriteria.model_validate_json(
            (
                PROJECT_ROOT / "data" / "criteria.json"
            ).read_text(encoding="utf-8")
        )

        job_description = (
            PROJECT_ROOT / "data" / "jobs" / "sample_job.txt"
        ).read_text(encoding="utf-8")

        print("Analyzing job requirements...")

        job = JobAnalysis.model_validate(
            analyze_job(job_description)
        )

        print("Comparing requirements with your profile...")

        report = match_job(profile, job)

        print("Checking your job preferences...")

        report["criteria"] = check_criteria(
            job,
            criteria,
            report["skill_match_score"],
        )

    except Exception as error:
        print(f"Matching failed ({type(error).__name__}): {error}")
        return 1

    print("\nMatch report:")
    print(json.dumps(report, indent=2, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())