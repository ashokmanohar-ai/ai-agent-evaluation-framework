# Safety evaluation

Safety combines independent policy with case expectations. Tool classes are `READ`,
`WRITE`, `HIGH_IMPACT` and `FORBIDDEN`. A high-impact call requires a recorded human
approval decision before the call timestamp. Rejection must stop execution.

The suite covers prompt injection, injected tool instructions, unauthorized and
cross-user access, destructive calls, unsafe retries, secret-like output, excessive
handoffs and cross-user memory. Retrieved text is always data, never a host command.

One critical violation hard-fails the quality gate; aggregate quality cannot mask it.
Production adapters must also enforce identity, tenant boundaries, least privilege,
network egress controls and audit retention at execution time. Evaluation detects
violations—it is not the primary authorization control.
