from pathlib import Path

from contract_risk_analyzer.modeling import registry


class DummyModel:
    pass


def test_local_model_loader_caches_by_resolved_path(monkeypatch, tmp_path: Path) -> None:
    model_path = tmp_path / "model.joblib"
    model_path.write_text("placeholder", encoding="utf-8")
    calls = {"count": 0}

    def fake_load(path: str) -> DummyModel:
        calls["count"] += 1
        return DummyModel()

    registry.clear_model_cache()
    monkeypatch.setattr(registry.TfidfLogisticBaseline, "load", staticmethod(fake_load))

    first = registry.load_local_model(model_path)
    second = registry.load_local_model(str(model_path))

    assert first is second
    assert calls["count"] == 1
    registry.clear_model_cache()
