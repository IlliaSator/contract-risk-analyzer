# Contract Risk Analyzer

Contract Risk Analyzer is a production-style NLP system for contract clause classification, semantic clause search, and risk triage. It combines a TF-IDF baseline, optional transformer fine-tuning, rule-based risk scoring, FastAPI deployment, Docker, tests, CI, and documentation.

**Disclaimer:** This tool is for document analysis and risk triage only. It is not legal advice and does not replace review by a qualified lawyer.

## Why This Matters

Contract review is time-consuming and repetitive. NLP can help route clauses, surface potential review points, and retrieve similar provisions, but the output remains assistive. Clause classification and heuristic risk scoring do not establish legal validity, enforceability, or business acceptability.

## Architecture

```mermaid
flowchart LR
    A[Contract text] --> B[Cleaning and chunking]
    B --> C[Clause classifier]
    C --> D[Risk rules]
    B --> E[Semantic search]
    D --> F[Structured risk report]
    E --> F
    F --> G[FastAPI]
```

## Features

- LexGLUE LEDGAR data download and preparation pipeline
- Optional CUAD preparation extension when public download is available
- TF-IDF + Logistic Regression baseline
- Optional Hugging Face transformer training pipeline
- Evaluation metrics: accuracy, macro F1, micro F1, weighted F1, per-class report, top confusions
- Rule-based risk scoring with uncertainty handling
- Semantic clause search with TF-IDF fallback and optional SentenceTransformers
- FastAPI service with mock-safe startup
- Docker and docker-compose setup
- Fast deterministic tests and GitHub Actions CI
- Model card, dataset notes, error-analysis and benchmark templates

## Dataset

Primary dataset: LexGLUE LEDGAR, a contract provision classification dataset.

No datasets are committed. Download and prepare locally:

```bash
python -m pip install -e ".[data]"
make download-ledgar
```

Sample data under `data/samples/` is tiny and committed only for tests and demos. CUAD support is optional and documented in [docs/dataset_notes.md](docs/dataset_notes.md).

## Modeling

The baseline is TF-IDF + Logistic Regression with optional class balancing. Macro F1 is emphasized because legal clause datasets can be imbalanced and rare classes matter. Transformer fine-tuning is available through:

```bash
make train-transformer-debug
```

CI does not train transformers or download models.

## Evaluation

Evaluation supports accuracy, macro F1, micro F1, weighted F1, per-class metrics, top confusions, low-confidence examples, and high-confidence wrong predictions. This repository does not include fake LEDGAR metrics. After downloading data and training:

```bash
make train-baseline
make evaluate
```

## Demo

Run deterministic mock analysis without external data:

```bash
make analyze-sample
```

Equivalent command:

```bash
python scripts/analyze_document.py --input data/samples/sample_contract.txt --output data/outputs/risk_report.json --mock
```

Generated output includes fields like:

```json
{
  "document_id": "sample_contract",
  "summary": "...",
  "overall_risk_score": 0,
  "risk_flags": ["..."],
  "disclaimer": "This tool is for document analysis and risk triage only. It is not legal advice and does not replace review by a qualified lawyer."
}
```

## API Usage

Start the API in mock mode:

```bash
make api
```

Example requests:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/model/info
curl -X POST http://localhost:8000/analyze/clause -H "Content-Type: application/json" -d "{\"text\":\"Either party may terminate without cause.\"}"
curl -X POST http://localhost:8000/analyze/document -H "Content-Type: application/json" -d "{\"document_id\":\"demo\",\"text\":\"Customer shall pay invoices. Either party may terminate.\"}"
curl -X POST http://localhost:8000/search/similar -H "Content-Type: application/json" -d "{\"query\":\"termination without cause\",\"top_k\":3}"
curl http://localhost:8000/metrics
```

More examples are in [docs/api_usage.md](docs/api_usage.md).

## Docker

```bash
make docker-build
make docker-run
```

The image does not include datasets, model weights, or retrieval indexes.

## Limitations

- Not legal advice and not a substitute for a qualified lawyer
- Models trained on LEDGAR may not generalize to all contracts
- Legal language varies across jurisdictions and industries
- Clause classification does not determine legal validity
- Risk scoring is heuristic and can miss important issues
- Long clauses, rare labels, boilerplate, and ambiguous wording remain difficult
- Human review is required

## Roadmap

- CUAD-based clause extraction task
- Long-context transformer support
- Retrieval reranking
- Calibrated confidence estimates
- Active learning and human feedback loop
- Model monitoring and drift checks
- Multilingual legal-document support
