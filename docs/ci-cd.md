# CI/CD

PR CI installs Python 3.12, runs Ruff lint/format, MyPy, Pytest, a mock smoke suite,
the safety gate and report upload. It needs no paid model or secret.

The regression workflow runs all 70 cases, compares the committed reviewed baseline
and uploads JSON/HTML/JUnit evidence. It also supports manual execution with another
provider when repository secrets are deliberately configured. The benchmark workflow
accepts two labels but uses an identical dataset/configuration for both runs.

Quality-gate failure returns a non-zero CLI exit code, so GitHub Actions, Jenkins and
Azure DevOps can block promotion. JUnit maps each dataset case to one test case;
machine-readable JSON preserves full trace evidence.
