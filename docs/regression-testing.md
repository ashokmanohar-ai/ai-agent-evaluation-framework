# Regression testing

A baseline is a versioned metric snapshot created from a real report. It includes
agent, dataset, framework and evaluator versions plus source run ID. The comparator
calculates `baseline - current` and fails when the drop exceeds the configured
maximum.

Safety and approval drops default to zero tolerance. Dataset or evaluator-version
differences produce compatibility warnings; teams should normally refresh a baseline
only after reviewing intentional changes. Prompt, model, tool or policy changes all
deserve regression execution on the same frozen dataset.

For fair model comparison, hold dataset, prompts, tools, evaluator versions, run
count and environment constant. Report task, tools, latency, tokens and safety rather
than declaring one model globally superior from a small benchmark.
