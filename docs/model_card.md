# Model Card

## Intended Use

Contract clause classification, semantic search, and document risk triage for NLP engineering demonstration and internal review assistance.

## Out-of-Scope Use

The system must not be used as legal advice, final contract approval, enforceability assessment, or replacement for qualified legal review.

## Training Data

Primary target data is LexGLUE LEDGAR prepared locally through the data pipeline. Tiny sample data is included only for tests and demos.

## Evaluation Data

Use LEDGAR validation and test splits after local download. The latest local run used:

- train: `60,000` LEDGAR records
- validation: `10,000` LEDGAR records
- test: `10,000` LEDGAR records

## Metrics

Supported metrics include accuracy, macro F1, micro F1, weighted F1, per-class precision/recall/F1, confusion matrix, and top confusing label pairs.

Latest local TF-IDF baseline metrics:

- validation macro F1: `0.7737`
- test accuracy: `0.8307`
- test macro F1: `0.7826`
- test weighted F1: `0.8332`

## Limitations

Legal clause labels can be ambiguous. Rare classes may perform poorly. Long provisions may require truncation. Out-of-domain contracts and jurisdiction-specific wording can reduce reliability.

The current trained baseline is English-domain only. It should not be treated as a validated model for Russian-language, Belarusian-language, Belarusian-law, or Russian-law contracts.

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
- Weak behavior on non-English legal text
- Poor transfer to Belarusian or Russian contract drafting without local training and evaluation data

## Monitoring Recommendations

Track input drift, label distribution, confidence distribution, latency, error samples, and human feedback on false positives and false negatives.
