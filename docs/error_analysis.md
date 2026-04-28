# Error Analysis

This document describes expected analysis dimensions. Do not fill in benchmark claims without running the evaluation pipeline.

## Common Misclassifications

Similar legal concepts can be hard to distinguish, especially payment versus fees, termination versus term, and liability versus indemnification.

## Rare Clause Labels

LEDGAR-like datasets can contain imbalanced labels. Macro F1 should be reviewed alongside per-class support.

## Long Clause Truncation

Transformer models may truncate long provisions. Important qualifiers at the end of a clause can be lost.

## Ambiguous Legal Wording

Clauses can serve multiple legal functions, and a single-label classifier may oversimplify them.

## Boilerplate Clauses

Boilerplate may look semantically similar across categories and can produce high-confidence mistakes.

## Out-of-Domain Documents

Contracts from unfamiliar jurisdictions, industries, or templates may degrade model quality.

## Suggested Mitigations

Use calibrated confidence, human review, label support checks, retrieval examples, active learning, and domain-specific validation sets.
