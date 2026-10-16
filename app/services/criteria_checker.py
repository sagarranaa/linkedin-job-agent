import re

from app.schemas import JobAnalysis, JobCriteria


LOCATION_ALIASES = {
    "bangalore": "bengaluru",
}


def normalize_location(value: str) -> str:
    cleaned = " ".join(value.casefold().split())
    return LOCATION_ALIASES.get(cleaned, cleaned)


def normalize_work_mode(value: str | None) -> str | None:
    if not value:
        return None

    text = value.casefold()

    # Hybrid descriptions can also mention remote or office days.
    if re.search(r"\bhybrid\b", text):
        return "hybrid"

    remote = bool(re.search(r"\bremote\b", text))
    onsite = bool(
        re.search(r"\bon[\s-]?site\b|\boffice\b", text)
    )

    if remote and onsite:
        return None

    if remote:
        return "remote"

    if onsite:
        return "onsite"

    return None


def check_criteria(
    job: JobAnalysis,
    criteria: JobCriteria,
    skill_score: float | None,
) -> dict:
    checks = {}

    # Location check
    if not criteria.allowed_locations:
        checks["location"] = {
            "status": "pass",
            "reason": "No location restriction configured.",
        }
    elif not job.location:
        checks["location"] = {
            "status": "unknown",
            "reason": "Job location is unspecified.",
        }
    else:
        allowed = {
            normalize_location(location)
            for location in criteria.allowed_locations
        }

        if normalize_location(job.location) in allowed:
            checks["location"] = {
                "status": "pass",
                "reason": f"Location accepted: {job.location}.",
            }
        else:
            checks["location"] = {
                "status": "unknown",
                "reason": (
                    f"Location '{job.location}' does not exactly "
                    "match your list; review it before rejecting."
                ),
            }

    # Work-mode check
    mode = normalize_work_mode(job.work_mode)

    if not criteria.allowed_work_modes:
        checks["work_mode"] = {
            "status": "pass",
            "reason": "No work-mode restriction configured.",
        }
    elif mode is None:
        checks["work_mode"] = {
            "status": "unknown",
            "reason": "Work mode is missing or ambiguous.",
        }
    elif mode in criteria.allowed_work_modes:
        checks["work_mode"] = {
            "status": "pass",
            "reason": f"Work mode accepted: {mode}.",
        }
    else:
        checks["work_mode"] = {
            "status": "fail",
            "reason": f"Work mode not accepted: {mode}.",
        }

    # Skill-score check
    if skill_score is None:
        checks["skill_score"] = {
            "status": "unknown",
            "reason": "No skill score is available.",
        }
    else:
        passed = skill_score >= criteria.minimum_skill_score

        checks["skill_score"] = {
            "status": "pass" if passed else "fail",
            "reason": (
                f"Score {skill_score}; "
                f"minimum {criteria.minimum_skill_score}."
            ),
        }

    statuses = {
        check["status"]
        for check in checks.values()
    }

    if "fail" in statuses:
        decision = "does_not_meet_configured_criteria"
    elif "unknown" in statuses:
        decision = "needs_review"
    else:
        decision = "meets_checked_criteria"

    return {
        "decision": decision,
        "checks": checks,
    }