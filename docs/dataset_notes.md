# Dataset Notes

## LEDGAR

LEDGAR is the primary dataset for contract provision classification. The data pipeline targets:

```python
from datasets import load_dataset
dataset = load_dataset("coastalcph/lex_glue", "ledgar")
```

If the Hugging Face identifier changes, update `configs/data.yaml` and rerun `make download-ledgar`.

The latest local download produced:

- train: `60,000` records
- validation: `10,000` records
- test: `10,000` records
- train labels: `100`

LEDGAR is an English-language dataset. It is useful for demonstrating NLP engineering around contract clause classification, but it does not validate the model for Russian-language, Belarusian-language, Russian-law, or Belarusian-law documents.

## CUAD

CUAD is useful for clause extraction and risk-oriented extensions, but availability can vary by host and download requirements. The project includes optional CUAD preparation code and does not block the main workflow on CUAD.

## Storage Policy

Raw datasets, processed full splits, model artifacts, and retrieval indexes are not committed to Git. Use local scripts to reproduce them.

## Sample Data

`data/samples/sample_clauses.jsonl` and `data/samples/sample_contract.txt` are tiny committed fixtures for tests and demos only.

## Regional Extension Notes

For Belarusian or Russian documents, a separate dataset and evaluation process would be needed. A reasonable extension would include:

- Russian and/or Belarusian contract samples
- a local clause taxonomy
- human-reviewed validation labels
- jurisdiction-aware risk rules written with legal experts
- multilingual embeddings or a multilingual transformer baseline
