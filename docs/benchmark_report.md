# Benchmark Report

This report keeps benchmarks modest and reproducible. The numbers below are local measurements, not universal claims about production latency.

## Environment

- OS: Windows 11
- Python: `3.12.8`
- Model: TF-IDF + Logistic Regression baseline trained on LEDGAR
- Model artifact: `models/baseline_tfidf.joblib`
- Model artifact size: `40.17 MB`
- Benchmark input: committed sample contract and sample clauses

## Baseline Training

The baseline was trained on the real LEDGAR splits:

- train: `60,000` records
- validation: `10,000` records
- test: `10,000` records

Observed terminal wall time for the training command was about `161 seconds` in this workspace.

Command:

```bash
python scripts/train_baseline.py --config configs/baseline.yaml
```

## Evaluation Metrics

The latest local LEDGAR evaluation produced:

- validation macro F1: `0.7737`
- test accuracy: `0.8307`
- test macro F1: `0.7826`
- test weighted F1: `0.8332`

Command:

```bash
python scripts/evaluate_model.py --config configs/baseline.yaml --model models/baseline_tfidf.joblib
```

## Latency Measurements

Measured with the trained local baseline model unless noted otherwise.

| Measurement | Mean | p95 | Notes |
| --- | ---: | ---: | --- |
| Baseline inference per clause | `2.910 ms` | `3.579 ms` | Six sample clauses, model already loaded |
| Document analysis | `340.812 ms` | `517.520 ms` | Sample contract, includes model loading inside current pipeline |
| Retrieval index build | `1.400 ms` | n/a | Tiny sample clause set |
| Retrieval search | `0.547 ms` | `0.778 ms` | TF-IDF retrieval over sample clause set |
| API `/analyze/clause`, mock mode | `15.685 ms` | `17.375 ms` | FastAPI TestClient, in-process |
| API `/analyze/clause`, model-backed | `299.818 ms` | `354.676 ms` | FastAPI TestClient, current route loads model per request |

## Interpretation

The baseline model itself is fast once loaded. The model-backed API benchmark is slower because the current API path loads the model from disk during each request. That is acceptable for a portfolio baseline, but a production service should load the model once during application startup and reuse it.

The retrieval benchmark is intentionally small because tests and demos must not require a large embedding index. A realistic retrieval benchmark should be repeated on a larger clause corpus.

## Reproduce

```bash
python -m pip install -e ".[data,dev]"
python scripts/download_data.py --dataset ledgar
python scripts/train_baseline.py --config configs/baseline.yaml
python scripts/evaluate_model.py --config configs/baseline.yaml --model models/baseline_tfidf.joblib
python scripts/analyze_document.py --input data/samples/sample_contract.txt --output data/outputs/risk_report_real_model.json --model models/baseline_tfidf.joblib
```
