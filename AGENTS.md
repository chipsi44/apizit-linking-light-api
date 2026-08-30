# Reference API repository guidelines

This repository is one autonomous member of the APIZIT reference API suite.

- Keep Python 3.12 compatibility and exactly five declared public routes.
- Preserve the shared paths and successful response contract in README.md.
- Keep /health immediate and keep /slow at exactly 80 seconds.
- Keep apizit_linking.yaml at the root and business code free of web-framework and APIZIT imports.
- Never declare APIZIT-managed apizit-linking, FastAPI, Mangum, or python-multipart packages in production requirements.
- Do not add cloud infrastructure, Dockerfiles, generated handlers, secrets, or credentials.
- Update tests, README.md, and CONTRIBUTING.md whenever the HTTP contract changes.
- Run validation, Ruff, pytest, and an APIZIT scan before publication.
- Use a codex/ branch, a Conventional Commit, and a reviewed pull request.
