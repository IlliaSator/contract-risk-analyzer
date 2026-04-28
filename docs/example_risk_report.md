# Example Risk Report

This is a shortened example generated from `data/samples/sample_contract.txt` using the trained TF-IDF baseline model. It is included to show the output shape, not to make legal claims.

Command:

```bash
python scripts/analyze_document.py \
  --input data/samples/sample_contract.txt \
  --output data/outputs/risk_report_real_model.json \
  --model models/baseline_tfidf.joblib
```

Shortened output:

```json
{
  "document_id": "sample_contract",
  "summary": "Analyzed 6 clauses and detected 5 potential risk indicators. Findings require human review.",
  "total_clauses": 6,
  "predicted_clause_types": {
    "Agreements": 1,
    "Applicable Laws": 1,
    "Confidentiality": 1,
    "Indemnifications": 1,
    "Payments": 1,
    "Terminations": 1
  },
  "overall_risk_score": 85.96,
  "severity_breakdown": {
    "critical": 0,
    "high": 2,
    "medium": 3,
    "low": 0
  },
  "risk_flags": [
    {
      "flag_type": "TERMINATION_RISK",
      "severity": "high",
      "reason": "Termination language may require closer human review."
    },
    {
      "flag_type": "CONFIDENTIALITY_RISK",
      "severity": "medium",
      "reason": "Confidentiality obligations should be validated against business expectations."
    },
    {
      "flag_type": "PAYMENT_RISK",
      "severity": "medium",
      "reason": "Payment terms contain indicators that may require operational review."
    }
  ],
  "disclaimer": "This tool is for document analysis and risk triage only. It is not legal advice and does not replace review by a qualified lawyer."
}
```

The score is produced by heuristic rules and confidence values. It should be interpreted as a triage signal only.
