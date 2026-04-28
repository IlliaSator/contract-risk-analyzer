from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from contract_risk_analyzer.data.schemas import ClausePrediction


@dataclass
class TfidfBaselineConfig:
    max_features: int = 50000
    ngram_range: tuple[int, int] = (1, 2)
    min_df: int = 2
    class_weight: str | None = "balanced"
    random_state: int = 42


class TfidfLogisticBaseline:
    def __init__(self, config: TfidfBaselineConfig | None = None) -> None:
        self.config = config or TfidfBaselineConfig()
        self.pipeline = Pipeline(
            steps=[
                (
                    "tfidf",
                    TfidfVectorizer(
                        lowercase=True,
                        strip_accents="unicode",
                        max_features=self.config.max_features,
                        ngram_range=self.config.ngram_range,
                        min_df=self.config.min_df,
                    ),
                ),
                (
                    "classifier",
                    LogisticRegression(
                        max_iter=1000,
                        class_weight=self.config.class_weight,
                        random_state=self.config.random_state,
                        n_jobs=None,
                    ),
                ),
            ]
        )
        self.model_name = "tfidf_logistic_regression"

    @property
    def classes_(self) -> np.ndarray:
        return self.pipeline.named_steps["classifier"].classes_

    def fit(self, texts: list[str], labels: list[str]) -> TfidfLogisticBaseline:
        if not texts or not labels:
            raise ValueError("Training data is empty.")
        if len(set(labels)) < 2:
            raise ValueError("Baseline classifier needs at least two labels.")
        self.pipeline.fit(texts, labels)
        return self

    def predict(self, texts: list[str]) -> list[str]:
        return [str(label) for label in self.pipeline.predict(texts)]

    def predict_proba(self, texts: list[str]) -> np.ndarray:
        if hasattr(self.pipeline, "predict_proba"):
            return self.pipeline.predict_proba(texts)
        decision = self.pipeline.decision_function(texts)
        exp_scores = np.exp(decision - np.max(decision, axis=1, keepdims=True))
        return exp_scores / exp_scores.sum(axis=1, keepdims=True)

    def predict_clauses(self, clause_ids: list[str], texts: list[str], top_k: int = 3) -> list[ClausePrediction]:
        probabilities = self.predict_proba(texts)
        classes = [str(label) for label in self.classes_]
        outputs: list[ClausePrediction] = []
        for clause_id, proba in zip(clause_ids, probabilities, strict=True):
            top_indices = np.argsort(proba)[::-1][:top_k]
            top_labels = [(classes[index], float(proba[index])) for index in top_indices]
            outputs.append(
                ClausePrediction(
                    clause_id=clause_id,
                    predicted_label=top_labels[0][0],
                    confidence=top_labels[0][1],
                    top_k_labels=top_labels,
                    model_name=self.model_name,
                )
            )
        return outputs

    def save(self, path: str) -> None:
        joblib.dump({"model": self, "model_name": self.model_name, "config": self.config}, path)

    @classmethod
    def load(cls, path: str) -> TfidfLogisticBaseline:
        payload: Any = joblib.load(path)
        if isinstance(payload, cls):
            return payload
        if isinstance(payload, dict) and isinstance(payload.get("model"), cls):
            return payload["model"]
        raise TypeError(f"Unsupported baseline artifact format: {path}")
