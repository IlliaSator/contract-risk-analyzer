# API Usage

Start locally:

```bash
CONTRACT_RISK_MOCK_MODEL=true uvicorn contract_risk_analyzer.api.main:app --host 0.0.0.0 --port 8000
```

Health:

```bash
curl http://localhost:8000/health
```

Analyze one clause:

```bash
curl -X POST http://localhost:8000/analyze/clause \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Either party may terminate this Agreement without cause.\"}"
```

Analyze a document:

```bash
curl -X POST http://localhost:8000/analyze/document \
  -H "Content-Type: application/json" \
  -d "{\"document_id\":\"demo\",\"text\":\"Customer shall pay invoices. Supplier shall indemnify Customer.\"}"
```

Search similar clauses:

```bash
curl -X POST http://localhost:8000/search/similar \
  -H "Content-Type: application/json" \
  -d "{\"query\":\"indemnification and hold harmless\",\"top_k\":3}"
```

Metrics:

```bash
curl http://localhost:8000/metrics
```
