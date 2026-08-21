# Contributing

1. Create a feature branch from `main`.
2. Add or update typed datasets before changing metric behaviour.
3. Prefer deterministic evaluators when code can decide the outcome.
4. Add positive and negative tests for every evaluator rule.
5. Run the complete validation suite below before opening a pull request.

```bash
python -m pip install -e '.[dev]'
ruff check .
ruff format --check .
mypy src tests
pytest
agent-eval run --dataset datasets/support/support-v1.jsonl --agent mock
```

Never commit credentials, real customer data, production traces, or fabricated
benchmark results. Explain metric formulas and compatibility impact in the PR.
