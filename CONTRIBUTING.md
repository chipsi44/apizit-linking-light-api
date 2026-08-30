# Contributing

Keep this project small, runnable, and comparable with the other APIZIT reference APIs.

Before opening a pull request:

1. preserve the five documented routes and their successful JSON responses;
2. keep Python 3.12 and the root `apizit_linking.yaml` manifest;
3. keep business modules free of Flask, FastAPI, Mangum, and APIZIT imports;
4. keep APIZIT-managed runtime packages out of production requirements;
5. run `apizit-linking validate .`, `ruff check .`, `ruff format --check .`, and `pytest -q`.

The 80-second `/slow` route is intentional. Unit tests must patch the wait while asserting the value 80.
