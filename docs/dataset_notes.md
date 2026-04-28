# Dataset Notes

## LEDGAR

LEDGAR is the primary dataset for contract provision classification. The data pipeline targets:

```python
from datasets import load_dataset
dataset = load_dataset("coastalcph/lex_glue", "ledgar")
```

If the Hugging Face identifier changes, update `configs/data.yaml` and rerun `make download-ledgar`.

## CUAD

CUAD is useful for clause extraction and risk-oriented extensions, but availability can vary by host and download requirements. The project includes optional CUAD preparation code and does not block the main workflow on CUAD.

## Storage Policy

Raw datasets, processed full splits, model artifacts, and retrieval indexes are not committed to Git. Use local scripts to reproduce them.

## Sample Data

`data/samples/sample_clauses.jsonl` and `data/samples/sample_contract.txt` are tiny committed fixtures for tests and demos only.
