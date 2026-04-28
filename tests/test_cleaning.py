from contract_risk_analyzer.preprocessing.cleaning import clean_legal_text, normalize_whitespace, remove_control_chars


def test_normalize_whitespace() -> None:
    assert normalize_whitespace("  alpha\n\n beta\t gamma  ") == "alpha beta gamma"


def test_remove_control_chars() -> None:
    assert remove_control_chars("alpha\x00beta").startswith("alpha beta")


def test_clean_empty_text() -> None:
    assert clean_legal_text(None) == ""
