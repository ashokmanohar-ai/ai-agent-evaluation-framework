# Security policy

## Supported version

Security fixes are applied to the latest release on `main`.

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability or leaked secret. Use
GitHub's private vulnerability reporting for this repository and include impact,
reproduction steps, affected version and a suggested mitigation if available.

## Evaluation safety model

- Dataset content is data, never executable host instruction.
- Demo tools are local, mocked and explicitly allow-listed.
- Forbidden/high-impact tools are governed by `config/tool-policy.yaml`.
- Human approval is checked from observed, timestamped trace events.
- Secrets are supplied only through environment variables and are never logged.
- Normal CI uses the mock provider and requires no external credentials.

Adapters that connect production tools must add sandboxing, least-privilege identity,
tenant isolation, timeouts, audit trails and environment-specific outcome probes.
