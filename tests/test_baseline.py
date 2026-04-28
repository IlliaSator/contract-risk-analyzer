from contract_risk_analyzer.modeling.baseline_tfidf import TfidfBaselineConfig, TfidfLogisticBaseline


def test_baseline_can_fit_tiny_sample() -> None:
    texts = [
        "terminate agreement notice",
        "confidential information secret",
        "pay invoice within thirty days",
        "indemnify and hold harmless",
    ]
    labels = ["termination", "confidentiality", "payment", "indemnification"]
    model = TfidfLogisticBaseline(TfidfBaselineConfig(min_df=1))
    model.fit(texts, labels)
    predictions = model.predict_clauses(["c1"], ["party may terminate with notice"], top_k=2)
    assert predictions[0].predicted_label in labels
    assert len(predictions[0].top_k_labels) == 2
