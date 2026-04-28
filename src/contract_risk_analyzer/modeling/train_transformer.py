from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np

from contract_risk_analyzer.config.settings import load_yaml, resolve_path
from contract_risk_analyzer.evaluation.metrics import compute_classification_metrics
from contract_risk_analyzer.modeling.train_baseline import load_supervised_jsonl
from contract_risk_analyzer.utils.io import write_json
from contract_risk_analyzer.utils.reproducibility import set_seed


class TransformerTrainingUnavailable(RuntimeError):
    """Raised when optional transformer dependencies are not installed."""


def _import_transformers() -> dict[str, Any]:
    try:
        from datasets import Dataset
        from transformers import (
            AutoModelForSequenceClassification,
            AutoTokenizer,
            DataCollatorWithPadding,
            Trainer,
            TrainingArguments,
        )
    except ImportError as exc:
        raise TransformerTrainingUnavailable(
            "Transformer training requires optional dependencies. "
            "Run `python -m pip install '.[transformers,data]'` and retry."
        ) from exc
    return {
        "Dataset": Dataset,
        "AutoModelForSequenceClassification": AutoModelForSequenceClassification,
        "AutoTokenizer": AutoTokenizer,
        "DataCollatorWithPadding": DataCollatorWithPadding,
        "Trainer": Trainer,
        "TrainingArguments": TrainingArguments,
    }


def train_transformer(
    config_path: str | Path,
    max_train_samples: int | None = None,
    max_eval_samples: int | None = None,
    epochs: int | None = None,
) -> dict[str, Any]:
    modules = _import_transformers()
    config = load_yaml(config_path)
    data_config = config["data"]
    model_config = config["model"]
    training_config = config["training"]
    set_seed(int(training_config.get("random_state", 42)))

    train_path = resolve_path(data_config["train_path"])
    validation_path = resolve_path(data_config["validation_path"])
    test_path = resolve_path(data_config["test_path"])
    for path in (train_path, validation_path, test_path):
        if not path.exists():
            raise FileNotFoundError(
                f"Required prepared LEDGAR split not found: {path}. Run `make download-ledgar` first."
            )

    train_texts, train_labels = load_supervised_jsonl(train_path)
    validation_texts, validation_labels = load_supervised_jsonl(validation_path)
    test_texts, test_labels = load_supervised_jsonl(test_path)
    if max_train_samples:
        train_texts, train_labels = train_texts[:max_train_samples], train_labels[:max_train_samples]
    if max_eval_samples:
        validation_texts, validation_labels = validation_texts[:max_eval_samples], validation_labels[:max_eval_samples]
        test_texts, test_labels = test_texts[:max_eval_samples], test_labels[:max_eval_samples]

    labels = sorted(set(train_labels) | set(validation_labels) | set(test_labels))
    label2id = {label: index for index, label in enumerate(labels)}
    id2label = {index: label for label, index in label2id.items()}

    tokenizer = modules["AutoTokenizer"].from_pretrained(model_config["model_name"])
    max_length = int(model_config.get("max_length", 256))

    def make_dataset(texts: list[str], labels_: list[str]) -> Any:
        dataset = modules["Dataset"].from_dict({"text": texts, "label": [label2id[label] for label in labels_]})

        def tokenize(batch: dict[str, list[str]]) -> dict[str, Any]:
            return tokenizer(batch["text"], truncation=True, max_length=max_length)

        return dataset.map(tokenize, batched=True)

    train_dataset = make_dataset(train_texts, train_labels)
    validation_dataset = make_dataset(validation_texts, validation_labels)
    test_dataset = make_dataset(test_texts, test_labels)

    model = modules["AutoModelForSequenceClassification"].from_pretrained(
        model_config["model_name"],
        num_labels=len(labels),
        label2id=label2id,
        id2label=id2label,
    )

    output_dir = resolve_path(model_config["output_dir"])
    training_args = modules["TrainingArguments"](
        output_dir=str(output_dir),
        learning_rate=float(training_config.get("learning_rate", 2e-5)),
        per_device_train_batch_size=int(training_config.get("batch_size", 8)),
        per_device_eval_batch_size=int(training_config.get("batch_size", 8)),
        num_train_epochs=int(epochs or training_config.get("epochs", 3)),
        weight_decay=float(training_config.get("weight_decay", 0.01)),
        evaluation_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="macro_f1",
        report_to=[],
    )

    def compute_metrics(eval_pred: Any) -> dict[str, float]:
        logits, label_ids = eval_pred
        predictions = np.argmax(logits, axis=-1)
        y_true = [id2label[int(label_id)] for label_id in label_ids]
        y_pred = [id2label[int(pred)] for pred in predictions]
        metrics = compute_classification_metrics(y_true, y_pred)
        return {
            "accuracy": float(metrics["accuracy"]),
            "macro_f1": float(metrics["macro_f1"]),
            "micro_f1": float(metrics["micro_f1"]),
            "weighted_f1": float(metrics["weighted_f1"]),
        }

    trainer = modules["Trainer"](
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=validation_dataset,
        tokenizer=tokenizer,
        data_collator=modules["DataCollatorWithPadding"](tokenizer=tokenizer),
        compute_metrics=compute_metrics,
    )
    trainer.train()
    test_output = trainer.predict(test_dataset)
    y_pred = [id2label[int(index)] for index in np.argmax(test_output.predictions, axis=-1)]
    metrics = compute_classification_metrics(test_labels, y_pred)
    metrics["model_name"] = model_config["model_name"]
    metrics["output_dir"] = str(output_dir)
    trainer.save_model(str(output_dir))
    tokenizer.save_pretrained(str(output_dir))
    write_json(resolve_path(config["evaluation"]["metrics_path"]), metrics)
    return metrics
