# Repository Guidelines

## Project Structure & Module Organization
- Anchor the service around `src/app.py`, exposing the Flask factory; register blueprints in `src/routes/` grouped by domain (`uploads`, `thumbnails`, `metadata`).
- Shared settings, logging, and storage adapters live in `src/core/`; business logic belongs in `src/services/`, while persistence adapters sit inside `src/repositories/` (GridFS, S3, or filesystem implementations).
- Place sample payloads under `assets/samples/`; scratch image output goes to `storage/{raw,processed}` and stays out of Git via `.gitignore`.
- Mirror production modules inside `tests/`; keep Docker or compose artefacts at the repo root and automation helpers under `scripts/`.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate` provisions the Python 3.11 virtualenv shared across ECOES services.
- `pip install -r requirements.txt` restores Flask, Pillow, boto3, and other imaging dependencies whenever they change.
- `flask --app src.app:create_app run --port 5010` starts the API locally with hot reload; export `FLASK_ENV=development` for verbose logging.
- `pytest` executes the full suite; use `pytest -k upload --maxfail=1 -vv` when iterating on a single flow.
- `docker compose up images-service minio` boots the container plus the object-storage stub that backs uploads.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation, `snake_case` functions, `PascalCase` classes, and descriptive module names (`routes/upload_routes.py`).
- Use type hints end-to-end; prefer dataclasses or Pydantic models for request/response contracts stored in `src/models/`.
- Format with `black src tests` and organize imports via `isort`; wire both into pre-commit once hooks are added.
- Name image variants with suffixes (`<uuid>_thumb.jpg`, `<uuid>_orig.png`) and centralize constants in `src/core/constants.py`.

## Testing Guidelines
- Write pytest modules in `tests/routes` and `tests/services`; name files `test_<feature>.py` and share fixtures through `tests/conftest.py`.
- Mock storage through fixtures that rely on `tempfile` to avoid writing under `storage/`; keep golden files in `tests/fixtures/`.
- Target 80% line coverage (`pytest --cov=src --cov-report=term-missing`); call out temporary gaps in PR descriptions.
- Document manual checks (curl upload + metadata retrieval) alongside automated assertions for new endpoints.

## Commit & Pull Request Guidelines
- Follow the house style: Spanish, lowercase prefixes (`feat: agrega thumbnail service`, `fix: corrige validación de mime`).
- Keep commits scoped to one concern and ship migrations or sync scripts whenever storage schemas change.
- PRs need a short summary, linked Trello/issue, test evidence (`pytest`, curl, docker compose logs), and screenshots for new image variants.
- Mention infra follow-ups (bucket policies, CDN changes) so release planning captures cross-service impacts.

## Security & Configuration Tips
- Configure secrets through `.env`: `STORAGE_DRIVER`, `BUCKET_NAME`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `JWT_SECRET_KEY`, `MAX_UPLOAD_MB`.
- Never upload real credentials or sample PII; rely on `.env.example` with safe placeholders.
- Validate content types and file size limits in `src/middleware/validation.py`; log rejects without storing payload bytes.
- When enabling public URLs, generate short-lived presigned links and ensure storage access logs remain enabled.
