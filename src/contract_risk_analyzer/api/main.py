from __future__ import annotations

from fastapi import FastAPI

from contract_risk_analyzer.api.routes import router
from contract_risk_analyzer.config.settings import load_yaml

config = load_yaml("configs/api.yaml")

app = FastAPI(
    title=config["service"]["title"],
    version=config["service"]["version"],
    description="NLP document intelligence service for contract clause analysis and risk triage.",
)
app.include_router(router)
