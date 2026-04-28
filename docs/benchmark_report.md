# Benchmark Report

No benchmark numbers are committed by default. Run benchmarks locally after preparing data and models.

## Suggested Measurements

- Baseline training time
- Baseline inference latency per clause
- Document analysis latency
- Retrieval index build time
- Retrieval search latency
- Model artifact size
- API p95 latency in mock and model-backed modes

## Commands

```bash
make download-ledgar
make train-baseline
make evaluate
make analyze-sample
make build-index
```

Record hardware, Python version, dataset split, model path, and command output before publishing numbers.
