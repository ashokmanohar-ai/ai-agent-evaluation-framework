# Trajectory evaluation

The normalized trace makes behaviour testable across orchestration frameworks. It
records model, tool call, tool result, routing, approval, memory, error and final
events with timestamps and identities.

Evaluators answer:

- Did every mandatory step occur?
- Was the order safe?
- Were optional steps harmless?
- Did a forbidden action occur?
- Was a retry caused by a real failure and within limit?
- Did the final output use the successful result?
- Was a multi-agent request routed to the right specialist?
- Did handoffs terminate within the maximum?

Trace comparison should align names and call IDs, then highlight additions,
deletions, duplicates, argument changes and result/status changes. A current trace
with `search → get_ticket → get_ticket → final` differs materially from a baseline
`get_ticket → final`, even if final text matches.
