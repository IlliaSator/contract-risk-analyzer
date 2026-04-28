# Data Directory

Large datasets are intentionally not committed.

- `raw/`: downloaded source data, if needed locally
- `interim/`: temporary preprocessing outputs
- `processed/`: normalized JSONL splits used by training and evaluation
- `samples/`: tiny committed demo/test data
- `outputs/`: local analysis outputs

Use `make download-ledgar` and `make prepare-data` for the primary LexGLUE LEDGAR workflow.
