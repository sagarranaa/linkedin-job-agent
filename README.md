# LinkedIn Job Agent

A learning project by **Sagar Rana** that uses a local LLM to explain job descriptions, compare them with a candidate profile, and evaluate job preferences. LangSmith provides tracing for the analysis step.

**Current stage:** a command-line, LLM-powered job-analysis workflow. Automatic job discovery, LinkedIn browsing, and application submission are not implemented.

## Features

- Load and validate a candidate profile with Pydantic.
- Read a job description from a local text file.
- Explain the role in simple language using Ollama.
- Extract responsibilities, required and preferred skills, minimum experience, location, work mode, and salary.
- Calculate an explainable skill-match score with profile evidence.
- Distinguish unlisted skills from confirmed skill gaps.
- Compare total experience against the extracted numeric minimum, while flagging relevant experience for review.
- Evaluate location, work mode, and a minimum skill score using pass/fail/unknown results.
- Trace the `analyze_job` function in LangSmith.
- Cache extracted analyses locally and support a `--refresh` option in the latest command version.

Profile validation, analysis, matching, criteria checks, and LangSmith tracing have been exercised during development. Cache integration is the latest addition: verify the two-run check below after updating `app/match_job.py`.

## Technology

| Tool | Purpose |
| --- | --- |
| Python | Command-line application and business logic |
| Ollama | Local LLM inference |
| Pydantic | Candidate and model-output validation |
| LangSmith | Analysis tracing and debugging |
| python-dotenv | Configuration from `.env` |
| JSON files | Candidate profile, preferences, and cached analyses |

Development environment: Ubuntu and Python 3.12. No OpenAI API key is required for the current Ollama implementation.

## How it works

1. Load and validate the candidate profile and job criteria.
2. Read the job description from `data/jobs/sample_job.txt`.
3. Load a cached analysis when available, or call Ollama and validate its response.
4. Compare extracted skills with the candidate's listed skills.
5. Calculate the score and check job preferences.
6. Print a JSON report.

The LLM extracts information and explains the role. Python performs scoring and criteria checks. The application currently follows a fixed workflow; tool selection, workflow state, and broader agent orchestration are future work.

## Project files

| Path | Responsibility |
| --- | --- |
| `app/__init__.py` | Python package marker |
| `app/main.py` | Candidate profile check |
| `app/config.py` | Project paths and environment configuration |
| `app/schemas.py` | `CandidateProfile`, `JobAnalysis`, and `JobCriteria` models |
| `app/analyze_job.py` | Standalone job-analysis command |
| `app/match_job.py` | Analysis, matching, and criteria workflow |
| `app/services/__init__.py` | Services package marker |
| `app/services/profile_loader.py` | Profile loading and validation |
| `app/services/job_analyzer.py` | Ollama call and LangSmith trace |
| `app/services/matcher.py` | Skill normalization, scoring, and experience comparison |
| `app/services/criteria_checker.py` | Location, work-mode, and score checks |
| `app/services/analysis_store.py` | Local analysis cache |
| `data/profile.json` | Private candidate facts; created locally |
| `data/criteria.json` | Private selection preferences; created locally |
| `data/jobs/sample_job.txt` | Local job input |
| `data/analysis_cache/` | Generated cache entries |
| `.env.example` | Configuration template without credentials |
| `requirements.txt` | Python dependencies |
| `docs/learning-log.md` | Learning notes |

## Setup

Download or clone this repository, then open a terminal in its root directory.

### 1. Create a Python environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

The application uses `pydantic`, `ollama`, `langsmith`, and `python-dotenv`.

### 2. Prepare Ollama

Install Ollama using its official instructions: <https://ollama.com/download>.

```bash
ollama list
```

If you want the model used in this tutorial and it is not installed:

```bash
ollama pull llama3
```

Use the exact installed model name in `.env`. If the Ollama service is not running, start `ollama serve` in a separate terminal. CPU inference can take some time.

### 3. Configure environment variables

Create `.env` in the project root. Use `.env.example` as a template if present:

```bash
cp .env.example .env
```

Example configuration:

```dotenv
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3:latest

LANGSMITH_TRACING=false
LANGSMITH_API_KEY=
LANGSMITH_PROJECT=linkedin-job-agent
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
```

To enable tracing, create a LangSmith API key, set `LANGSMITH_TRACING=true`, and populate `LANGSMITH_API_KEY` locally. Use the API endpoint for your LangSmith deployment. Set `LANGSMITH_WORKSPACE_ID` when required by your key's workspace scope.

Account and key setup: <https://docs.langchain.com/langsmith/create-account-api-key>.

Never commit `.env` or put a real key in `.env.example`.

### 4. Create local input files

The `data/` directory is ignored by Git. After cloning, create these files yourself:

```bash
mkdir -p data/jobs
```

`data/profile.json`:

```json
{
  "name": "Your Name",
  "skills": ["Node.js", "React", "MySQL", "MongoDB"],
  "total_experience_years": null,
  "notice_period_days": null,
  "qualifications": [],
  "preferred_roles": ["Backend Developer", "Full Stack Developer"],
  "preferred_locations": []
}
```

Replace these examples with accurate facts. `null` means unknown, not zero. The criteria checker reads location preferences from `criteria.json`; the profile's `preferred_locations` field is not currently used by that checker.

`data/criteria.json`:

```json
{
  "allowed_locations": ["Bengaluru"],
  "allowed_work_modes": ["hybrid", "onsite"],
  "minimum_skill_score": 75
}
```

An empty allowed list means no restriction. Supported work modes are `remote`, `hybrid`, and `onsite`.

`data/jobs/sample_job.txt`:

```text
Role: Backend Developer

We are looking for a Backend Developer with at least 3 years
of professional backend development experience.

Required skills:
- Node.js
- REST API development
- MySQL
- Git

Preferred skills:
- MongoDB
- AWS
- Experience building AI-powered features

Responsibilities:
- Build and maintain backend APIs.
- Design database tables and optimize queries.
- Investigate production issues.
- Collaborate with frontend developers.

Location: Bengaluru
Work mode: Hybrid, 3 days per week in the office.

Salary and educational requirements are not specified.
```

This is a fictional example for development.

## Run the application

Run commands from the repository root with the virtual environment active.

```bash
# Validate and display the candidate profile
python -m app.main

# Analyze the sample job with Ollama
python -m app.analyze_job

# Analyze, compare, and check preferences
python -m app.match_job

# Force fresh extraction in the cache-enabled version
python -m app.match_job --refresh
```

The standalone `app.analyze_job` command calls the analyzer directly. Caching is connected through the latest `app.match_job` command.

## Scoring

| Category | Weight |
| --- | ---: |
| Required skills | 80% |
| Preferred skills | 20% |

Each category's ratio is matched unique skills divided by listed unique skills. For a job containing both categories:

```text
Skill score = 100 × (0.8 × required ratio + 0.2 × preferred ratio)
```

If a category is absent, its weight is redistributed to the available category. If both categories are absent, the score is `null`.

Skill matching uses case normalization and an explicit alias map. For example, `Node.js` and `nodejs` match. Duplicate requirements are counted once. Broadly related terms are not automatically treated as equivalent.

Example: two of four required skills and one of three preferred skills produce **46.7/100**. A profile with Node.js, MySQL, and MongoDB can produce this result for the sample posting if Git and REST API development are not listed.

The score measures documented skill alignment under these rules. It is not a hiring probability or a complete eligibility assessment.

## Criteria and recommendations

Each criteria check returns `pass`, `fail`, or `unknown`.

| Overall criteria decision | Meaning |
| --- | --- |
| `does_not_meet_configured_criteria` | At least one check failed |
| `needs_review` | No failed checks, but at least one unknown |
| `meets_checked_criteria` | Every implemented check passed |

Location matching recognizes explicit aliases such as Bangalore/Bengaluru. Unmatched free-text locations require review. Work mode is inferred with simple text rules; complex descriptions may need manual review.

The report currently contains both a matcher `recommendation` and a separate `criteria.decision`. They describe different checks and have not yet been combined into a final application decision. A passing criteria result does not trigger submission.

## Analysis caching

The cache key includes the job description, model name, analysis schema, and `ANALYSIS_VERSION`. JSON files are saved under `data/analysis_cache/`.

After connecting `analysis_store.py` to `app/match_job.py`, run the matching command twice. The first uncached run should print:

```text
Analyzing job requirements with Ollama...
Analysis saved.
```

The second should print:

```text
Using saved job analysis; Ollama call skipped.
```

Profile matching and preference checks still run on every invocation. Use `--refresh` to regenerate an analysis. Increase `ANALYSIS_VERSION` when changing the extraction prompt or when a model update should invalidate existing results.

The current cache is intended for a single local CLI process. Concurrent writes and automatic recovery from corrupted cache files are not implemented.

## LangSmith tracing

The analyzer uses:

```python
@traceable(name="analyze_job", run_type="chain")
```

Open the `linkedin-job-agent` project in LangSmith to inspect the function's input, output, duration, and errors. Cached analyses do not create a new `analyze_job` run.

Current instrumentation is one function-level trace. Separate model-call spans, token accounting, matcher traces, and end-to-end workflow tracing are future improvements.

Ollama inference runs locally. When tracing is enabled, the traced job description and analysis are sent to LangSmith. The current matcher is not decorated and does not send the candidate profile to LangSmith.

## Troubleshooting

| Problem | Check |
| --- | --- |
| Environment values are missing | Save `.env` in the project root and confirm `app/config.py` calls `load_dotenv` |
| LangSmith returns 403 | Check the full API key, deployment endpoint, expiration, and workspace access |
| API key contains `...` | Replace the shortened table value with the full secret copied at creation |
| Ollama connection fails | Check that Ollama is running and `OLLAMA_BASE_URL` is correct |
| Model is unavailable | Run `ollama list` and use the exact installed name |
| Skill score stays unchanged | Check the saved `data/profile.json`; rerunning does not add missing evidence |
| Every match run calls Ollama | Confirm the cache-enabled `app/match_job.py` was saved |
| No new trace after a cached run | Expected: the analyzer was not called |

## Current limitations

- Job input comes from a local file; automatic discovery and fetching are not implemented.
- Skill comparison uses names and aliases, not project-level evidence or semantic matching.
- Total years of experience do not prove relevant backend or technology-specific experience.
- Salary, qualifications, and work authorization are not checked for eligibility.
- JSON schema validation checks structure; extracted facts can still be incomplete or incorrect. For example, missing salary may appear as `null` without being listed in `unclear_details`.
- Automated test coverage has not yet been established; development has used CLI runs and targeted assertion checks.
- No database, API server, dashboard, resume upload, application tracking, or submission integration is implemented.
- The project does not currently automate LinkedIn browsing or Easy Apply. Any future live integration requires an appropriate supported access route and review of platform rules.

## Roadmap

- Add relevant experience and project evidence.
- Consolidate matching and criteria into one explainable recommendation.
- Add structured salary and qualification checks.
- Save job history and reports in a database.
- Build a FastAPI backend and React dashboard.
- Add evaluation examples and regression tests.
- Introduce agent tools, workflow state, and recovery behavior.
- Practice application automation on a local demo form.
- Explore supported job-source and application integrations.

## Before publishing

Keep `.env`, private candidate data, resumes, and cached analyses out of the repository. A suitable `.gitignore` includes:

```gitignore
.venv/
.env
__pycache__/
*.pyc
.pytest_cache/
data/
*.db
*.db-shm
*.db-wal
```

Include a credential-free `.env.example`. If a credential was exposed in a screenshot or committed previously, revoke it and replace it; adding `.gitignore` does not remove existing tracked files or history.

## Author

Sagar Rana — building practical AI application skills through an incremental, explainable project.