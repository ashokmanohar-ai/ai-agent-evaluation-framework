# Deterministic evaluation

Deterministic evaluators consume explicit expectations and observed trace fields.
They do not ask a model to decide exact tool names, identifiers, approval ordering or
budget arithmetic.

Argument modes are `exact`, `casefold`, `contains` and `date_equivalent`. A custom
domain validator can be added beside these modes. `semantic` is represented in the
schema but deliberately fails the deterministic matcher so a caller cannot silently
claim deterministic success.

Trajectory order is evaluated as an ordered subsequence: optional diagnostic steps
may interleave, but required steps cannot be reversed. Retries are counted separately
and successful non-idempotent actions cannot be repeated safely.

Every failure provides a reason code and evidence object. This supports triage,
failure-category trends and CI annotations without parsing prose.
