# Model Card

## Intended Use

Contract clause classification, semantic search, and document risk triage for NLP engineering demonstration and internal review assistance.

## Out-of-Scope Use

The system must not be used as legal advice, final contract approval, enforceability assessment, or replacement for qualified legal review.

## Training Data

Primary target data is LexGLUE LEDGAR prepared locally through the data pipeline. Tiny sample data is included only for tests and demos.

## Evaluation Data

Use LEDGAR validation and test splits after local download. Metrics are not committed unless generated locally by the user.

## Metrics

Supported metrics include accuracy, macro F1, micro F1, weighted F1, per-class precision/recall/F1, confusion matrix, and top confusing label pairs.

## Limitations

Legal clause labels can be ambiguous. Rare classes may perform poorly. Long provisions may require truncation. Out-of-domain contracts and jurisdiction-specific wording can reduce reliability.

## Ethical Considerations

The model can create false confidence if presented as legal authority. Outputs should be framed as triage signals and reviewed by humans.

## Legal Disclaimer

This tool is for document analysis and risk triage only. It is not legal advice and does not replace review by a qualified lawyer.

## Human Review Requirement

All risk flags, predictions, and reports require review by qualified humans before business or legal decisions.

## Failure Modes

- Confusing similar clause categories
- Missing risk language not covered by rules
- Over-flagging boilerplate
- Underperforming on rare labels
- Misleading confidence on unfamiliar documents

## Monitoring Recommendations

Track input drift, label distribution, confidence distribution, latency, error samples, and human feedback on false positives and false negatives.
