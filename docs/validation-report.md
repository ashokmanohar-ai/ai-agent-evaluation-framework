# Validation report

Validated on 2026-08-21 with Python 3.12.13 and the offline mock provider.

| Check | Result | Evidence |
|---|---|---|
| Editable dependency installation | PASS | `python -m pip install -e '.[dev]'` |
| Ruff lint | PASS | No findings |
| Ruff formatting | PASS | 90 files already formatted |
| MyPy | PASS | 62 source/test files checked with no issues |
| Unit/evaluator/adapter/security/regression/E2E tests | PASS | 32 passed |
| Dataset validation | PASS | 70 unique, typed cases |
| Complete offline evaluation | PASS | 70/70 cases, quality gate PASS |
| Task/tool/argument/plan/trajectory/grounding metrics | PASS | All aggregate scores 1.0 |
| Safety/HITL/recovery/retry/efficiency metrics | PASS | All aggregate scores 1.0 |
| Mock judge and provider interface | PASS | Valid, malformed, repeated and timeout tests |
| Baseline creation | PASS | Created from a real 70-case report |
| Regression comparison | PASS | All configured drops within limits |
| Console/JSON/HTML/JUnit reports | PASS | Generated and parsed |
| FastAPI health and CLI smoke flow | PASS | Automated E2E tests |
| Dockerfile | STATIC PASS | Base, non-root user and entry point validated |
| Docker image execution | PENDING CI | Docker is not installed in the local validation environment |
| Workflow/Compose YAML | PASS | Parsed successfully |
| Credentials and unfinished markers | PASS | No committed secrets or critical TODO/FIXME markers found |

## Required negative behaviours

Automated tests prove wrong tool, wrong argument, forbidden tool, missing execution,
wrong sequence, unsupported claim, approval bypass, endless retry, duplicate write
retry, latency breach and safety regression fail as expected. The transient timeout
followed by one successful retry passes.

## Known limitations

- Live provider behaviour was not exercised because offline reproducibility is the
  mandatory default; live SDK adapters require intentional credentials.
- Docker build/run awaits the repository's Docker CI job because the local runtime
  has no Docker executable.
- The 70-case mock benchmark validates framework correctness, not a production
  agent's business readiness.
- Open-text claim extraction and production state verification require domain-specific
  adapters; unavailable tokens and cost are skipped rather than invented.

Current status: **ready for GitHub CI validation and technical review**.
