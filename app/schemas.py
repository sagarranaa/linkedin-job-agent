from pydantic import BaseModel, ConfigDict, Field
from typing import Literal

class CandidateProfile(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    name: str = Field(min_length=1)

    skills: list[str] = Field(min_length=1)

    total_experience_years: float | None = Field(
        default=None,
        ge=0,
    )

    notice_period_days: int | None = Field(
        default=None,
        ge=0,
    )

    qualifications: list[str] = Field(default_factory=list)
    preferred_roles: list[str] = Field(default_factory=list)
    preferred_locations: list[str] = Field(default_factory=list)



class JobAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    simple_explanation: str
    responsibilities: list[str]

    required_skills: list[str]
    preferred_skills: list[str]

    minimum_experience_years: float | None = Field(ge=0)

    location: str | None
    work_mode: str | None
    salary: str | None

    unclear_details: list[str]

class JobCriteria(BaseModel):
    model_config = ConfigDict(extra="forbid")

    allowed_locations: list[str] = Field(default_factory=list)

    allowed_work_modes: list[
        Literal["remote", "hybrid", "onsite"]
    ] = Field(default_factory=list)

    minimum_skill_score: float = Field(
        default=75,
        ge=0,
        le=100,
    )