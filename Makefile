.PHONY: \
	install \
	test \
	lint \
	format \
	api \
	download-ledgar \
	prepare-data \
	train-baseline \
	train-transformer-debug \
	evaluate \
	build-index \
	analyze-sample \
	docker-build \
	docker-run

PYTHON ?= python

install:
	$(PYTHON) -m pip install -e ".[dev]"

test:
	$(PYTHON) -m compileall src tests scripts
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m ruff check src tests scripts

format:
	$(PYTHON) -m ruff format src tests scripts

api:
	CONTRACT_RISK_MOCK_MODEL=true $(PYTHON) -m uvicorn contract_risk_analyzer.api.main:app --host 0.0.0.0 --port 8000

download-ledgar:
	$(PYTHON) scripts/download_data.py --dataset ledgar

prepare-data:
	$(PYTHON) scripts/prepare_data.py --dataset ledgar

train-baseline:
	$(PYTHON) scripts/train_baseline.py --config configs/baseline.yaml

train-transformer-debug:
	$(PYTHON) scripts/train_transformer.py \
		--config configs/transformer.yaml \
		--max-train-samples 500 \
		--max-eval-samples 200 \
		--epochs 1

evaluate:
	$(PYTHON) scripts/evaluate_model.py --config configs/baseline.yaml --model models/baseline_tfidf.joblib

build-index:
	$(PYTHON) scripts/build_retrieval_index.py --input data/samples/sample_clauses.jsonl --output models/retrieval

analyze-sample:
	$(PYTHON) scripts/analyze_document.py \
		--input data/samples/sample_contract.txt \
		--output data/outputs/risk_report.json \
		--mock

docker-build:
	docker build -t contract-risk-analyzer:local .

docker-run:
	docker run --rm -p 8000:8000 \
		-e CONTRACT_RISK_MOCK_MODEL=true \
		-v "$$(pwd)/models:/app/models" \
		-v "$$(pwd)/data:/app/data" \
		contract-risk-analyzer:local
