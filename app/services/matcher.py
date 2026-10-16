from app.schemas import CandidateProfile, JobAnalysis

ALIASES = {
    "node": "nodejs",
    "node.js": "nodejs",
    "node js": "nodejs",
    "nodejs": "nodejs",
    "react.js": "react",
    "reactjs": "react",
    "react": "react",
    "rest api": "rest",
    "rest apis": "rest",
    "rest api development": "rest",
    "restful api": "rest",
    "restful apis": "rest",
}


def normalize_skill(skill: str) -> str:
    cleaned = " ".join(skill.casefold().split())
    return ALIASES.get(cleaned, cleaned)


def compare_skills(
    requirements: list[str],
    candidate_skills: list[str],
) -> dict:
    candidate_lookup = {}

    for skill in candidate_skills:
        normalized = normalize_skill(skill)

        if normalized:
            candidate_lookup[normalized] = skill

    matched = []
    not_established = []
    seen = set()

    for requirement in requirements:
        normalized = normalize_skill(requirement)

        # Avoid counting the same requirement twice.
        if not normalized or normalized in seen:
            continue

        seen.add(normalized)

        if normalized in candidate_lookup:
            matched.append({
                "requirement": requirement,
                "profile_evidence": candidate_lookup[normalized],
            })
        else:
            not_established.append(requirement)

    total = len(matched) + len(not_established)

    return {
        "matched": matched,
        "not_established": not_established,
        "total": total,
        "ratio": len(matched) / total if total else None,
    }


def match_job(
    profile: CandidateProfile,
    job: JobAnalysis,
) -> dict:
    required = compare_skills(
        job.required_skills,
        profile.skills,
    )

    preferred = compare_skills(
        job.preferred_skills,
        profile.skills,
    )

    weighted_total = 0.0
    active_weight = 0.0

    for comparison, weight in (
        (required, 0.8),
        (preferred, 0.2),
    ):
        if comparison["ratio"] is not None:
            weighted_total += comparison["ratio"] * weight
            active_weight += weight

    skill_score = (
        round(100 * weighted_total / active_weight, 1)
        if active_weight
        else None
    )

    candidate_years = profile.total_experience_years
    minimum_years = job.minimum_experience_years

    if minimum_years is None:
        experience_status = "Job minimum is unspecified"
    elif candidate_years is None:
        experience_status = "Candidate experience is unknown"
    elif candidate_years < minimum_years:
        experience_status = "Total experience is below the job minimum"
    else:
        experience_status = (
            "Total experience reaches the numeric minimum; "
            "verify relevant experience"
        )

    if skill_score is None:
        recommendation = "Review: insufficient skill requirements"
    elif candidate_years is not None and (
        minimum_years is not None
        and candidate_years < minimum_years
    ):
        recommendation = "Lower priority: experience gap needs review"
    elif required["not_established"]:
        recommendation = "Review: required skills need evidence"
    elif required["total"] == 0:
        recommendation = "Review: required skills are unspecified"
    elif skill_score >= 75:
        recommendation = "Shortlist for criteria and experience review"
    else:
        recommendation = "Review: limited documented skill alignment"

    return {
        "job_title": job.title,
        "skill_match_score": skill_score,
        "required_skills": required,
        "preferred_skills": preferred,
        "experience": {
            "candidate_total_years": candidate_years,
            "job_minimum_years": minimum_years,
            "status": experience_status,
        },
        "recommendation": recommendation,
        "limitations": [
            "Uses listed skills and explicit aliases only.",
            "Unlisted skills are unknown, not confirmed gaps.",
            "Total experience does not prove relevant experience.",
            "Location, salary, qualifications and work mode "
            "are not evaluated yet.",
            "This score is not a probability of getting hired.",
        ],
    }