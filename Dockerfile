FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    EVAL_MODEL_PROVIDER=mock

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
COPY config ./config
COPY datasets ./datasets
COPY prompts ./prompts
COPY baselines ./baselines
RUN python -m pip install --upgrade pip && python -m pip install .

RUN useradd --create-home --uid 10001 evaluator && mkdir -p /app/reports && chown -R evaluator:evaluator /app
USER evaluator

ENTRYPOINT ["agent-eval"]
CMD ["run", "--dataset", "datasets/support/support-v1.jsonl", "--agent", "mock"]
