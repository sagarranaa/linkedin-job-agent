from pathlib import Path

from pydantic import ValidationError

from app.services.profile_loader import load_profile


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    profile_path = PROJECT_ROOT / "data" / "profile.json"

    try:
        profile = load_profile(profile_path)
    except (OSError, ValidationError) as error:
        print(f"Could not load candidate profile:\n{error}")
        return 1

    experience = (
        "Not provided"
        if profile.total_experience_years is None
        else f"{profile.total_experience_years:g} years"
    )

    print("LinkedIn Job Agent — profile check")
    print(f"Name: {profile.name}")
    print(f"Experience: {experience}")
    print(f"Skills: {', '.join(profile.skills)}")
    print(f"Preferred roles: {', '.join(profile.preferred_roles)}")
    print("\nProfile loaded and validated successfully.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())