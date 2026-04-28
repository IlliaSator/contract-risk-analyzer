FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV CONTRACT_RISK_MOCK_MODEL=true

WORKDIR /app

COPY pyproject.toml README.md requirements.txt ./
COPY src ./src
COPY configs ./configs
COPY data/samples ./data/samples

RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -e .

EXPOSE 8000

CMD ["uvicorn", "contract_risk_analyzer.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
