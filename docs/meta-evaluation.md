# Meta-evaluation

Evaluators are also software and must be evaluated. Build a labelled corpus of true
and false trajectories, measure evaluator precision/recall and inspect false
positive/negative clusters. For judges, track inter-rater agreement with humans and
between repeated model calls.

Risks include judge drift, evaluation leakage, benchmark overfitting, dataset bias,
ambiguous labels and correlated self-evaluation. Version every material input, keep a
human-reviewed holdout, use deterministic checks for high-consequence behaviour and
review changed evaluator rules like production code.
