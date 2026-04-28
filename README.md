# Contract Risk Analyzer

Contract Risk Analyzer is a portfolio NLP project for contract document intelligence. It classifies contract clauses, highlights simple risk indicators, retrieves similar clauses, and exposes the workflow through a FastAPI service.

The project is intentionally built as an engineering system, not as a notebook demo. The interesting parts are the reproducible data pipeline, a classical baseline, evaluation, error analysis, structured report generation, API layer, Docker setup, tests, CI, and honest documentation about what the model can and cannot do.

**Important disclaimer:** this tool is for document analysis and risk triage only. It is not legal advice and does not replace review by a qualified lawyer.

## Why I Built This

Contract review has a lot of repetitive structure: termination clauses, governing law, payment terms, indemnification, confidentiality, assignment, and many other recurring provisions. NLP can help organize that text and point a reviewer toward clauses that may deserve attention.

I chose this domain because I have a legal background and wanted to connect it with practical ML engineering. That background helps me frame the problem realistically: the goal is not to automate legal judgment, but to build a careful document analysis workflow with clear boundaries, transparent rules, and human review at the center.

That said, this project does not try to be a legal chatbot or an automatic legal decision maker. It is closer to a document intelligence service: classify the clause, attach confidence, apply transparent rules, and produce a structured report that a human can review.

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

## What Is Included

- LEDGAR data download and preparation pipeline
- Optional CUAD preparation path
- TF-IDF + Logistic Regression baseline
- Optional Hugging Face transformer training pipeline
- Evaluation with accuracy, macro F1, micro F1, weighted F1, per-class metrics, and top confusions
- Rule-based risk scoring on top of model predictions
- Semantic clause search with a lightweight TF-IDF fallback
- FastAPI service that can run in mock mode or with a trained local model
- Docker and docker-compose setup
- Unit tests, API tests, linting, and GitHub Actions CI
- Model card, dataset notes, error analysis notes, benchmark template, and release notes

## Dataset

The primary dataset is **LexGLUE LEDGAR**, a public contract provision classification dataset. The repository does not commit raw or processed dataset files. They are generated locally:

```bash
python -m pip install -e ".[data]"
python scripts/download_data.py --dataset ledgar
```

The current pipeline normalizes LEDGAR into JSONL splits under `data/processed/`:

- `ledgar_train.jsonl`
- `ledgar_validation.jsonl`
- `ledgar_test.jsonl`

Tiny sample files in `data/samples/` are committed only so tests and demos can run without internet access.

## Modeling

The main baseline is TF-IDF plus Logistic Regression. It is simple, fast, reproducible, and useful as a reference point before moving to heavier transformer models.

Macro F1 is tracked because LEDGAR is imbalanced: a model can look good on accuracy while doing poorly on rare clause classes.

Train the baseline after downloading LEDGAR:

```bash
python scripts/train_baseline.py --config configs/baseline.yaml
```

Optional transformer training is available, but it is intentionally not run in CI:

```bash
python scripts/train_transformer.py --config configs/transformer.yaml --max-train-samples 500 --max-eval-samples 200 --epochs 1
```

## Latest Local Baseline Results

These metrics were produced locally on the real LEDGAR splits:

- validation macro F1: `0.7737`
- test accuracy: `0.8307`
- test macro F1: `0.7826`
- test weighted F1: `0.8332`

Commands used:

```bash
python scripts/train_baseline.py --config configs/baseline.yaml
python scripts/evaluate_model.py --config configs/baseline.yaml --model models/baseline_tfidf.joblib
```

The trained model, processed dataset files, and generated reports are not committed. They are local artifacts and are ignored by Git.

Additional local latency and model-size measurements are documented in [docs/benchmark_report.md](docs/benchmark_report.md).

## Will It Work For Belarusian Or Russian Documents?

Technically, the service will accept any text. Practically, the trained baseline should **not** be treated as reliable for Belarusian or Russian contracts.

The current model is trained on LEDGAR, which is an English-language contract provision dataset. That means the model has learned English legal drafting patterns and LEDGAR label conventions. Russian-language or Belarusian-language contracts, and contracts governed by Belarusian or Russian law, are a different domain.

For Belarusian or Russian documents, this project would need at least:

- Russian and/or Belarusian contract data
- a local clause taxonomy
- jurisdiction-aware risk rules written with legal experts
- evaluation on representative local documents
- probably multilingual embeddings or a multilingual transformer model

So the honest answer is: it can be used as an engineering framework, but not as a validated legal-domain model for Belarus or Russia yet.

## Demo

Run a deterministic demo without any trained model:

```bash
python scripts/analyze_document.py \
  --input data/samples/sample_contract.txt \
  --output data/outputs/risk_report.json \
  --mock
```

Run the same flow with a trained baseline:

```bash
python scripts/analyze_document.py \
  --input data/samples/sample_contract.txt \
  --output data/outputs/risk_report_real_model.json \
  --model models/baseline_tfidf.joblib
```

The report contains the document id, predicted clause types, risk flags, severity breakdown, recommendations, overall score, and the legal disclaimer.

A shortened model-backed report example is available in [docs/example_risk_report.md](docs/example_risk_report.md).

## API

Start in mock mode:

```bash
CONTRACT_RISK_MOCK_MODEL=true uvicorn contract_risk_analyzer.api.main:app --host 0.0.0.0 --port 8000
```

Start with a trained baseline:

```bash
CONTRACT_RISK_MOCK_MODEL=false CONTRACT_RISK_MODEL_PATH=models/baseline_tfidf.joblib uvicorn contract_risk_analyzer.api.main:app --host 0.0.0.0 --port 8000
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

More API examples are in [docs/api_usage.md](docs/api_usage.md).

## Docker

```bash
docker build -t contract-risk-analyzer:local .
docker run --rm -p 8000:8000 -e CONTRACT_RISK_MOCK_MODEL=true contract-risk-analyzer:local
```

The image does not include datasets, model weights, or retrieval indexes.

## Tests

The test suite is deliberately small and deterministic. It does not require internet access, GPU, Hugging Face downloads, FAISS, or trained model weights.

```bash
python -m compileall src tests scripts
python -m pytest -q
python -m ruff check src tests scripts
```

## Limitations

- This is not legal advice.
- The risk scoring layer is heuristic.
- LEDGAR classification is not the same thing as legal validity.
- The current trained baseline is English-domain only.
- Belarusian and Russian legal documents are out of domain for the current model.
- Long clauses, boilerplate, rare labels, and ambiguous provisions remain difficult.
- Human review is required before making legal or business decisions.

## Roadmap

- Add a real CUAD extraction workflow
- Try a multilingual model for non-English contracts
- Add calibrated confidence estimates
- Add better retrieval reranking
- Add human feedback loops
- Add model monitoring and drift checks
- Build a separate evaluation set for Russian and Belarusian contracts

## Russian Version

A Russian version is available in [README.ru.md](README.ru.md).
