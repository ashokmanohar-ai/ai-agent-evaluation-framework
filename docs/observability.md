# Observability

OpenTelemetry spans nest evaluation run and case execution. Adapters may add model,
tool and evaluator spans using the same run and case IDs. Key attributes include
duration, status, tokens, tool name and metric.

Tracing answers why a case failed, where time was spent, which dependency failed and
how current behaviour differs from the baseline. It also exposes repeated calls and
routing loops hidden by final-answer metrics.

Offline evaluation is the default (`OTEL_SDK_DISABLED=true`). For Phoenix-compatible
inspection, install `.[phoenix]`, start `docker compose --profile observability up -d
phoenix`, set `OTEL_SDK_DISABLED=false` and point `OTEL_EXPORTER_OTLP_ENDPOINT` at the
collector. Keep sensitive arguments/results redacted in real adapters.
