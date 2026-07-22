# EdgeBoard 3.5 Render-Ready Patch

## Fixed
- Moved the complete project to the ZIP root so GitHub uploads do not create an extra nested project directory.
- Ensured `render.yaml` is located at the repository root.
- Preserved the Render Blueprint definitions for the API, web app, PostgreSQL database, refresh cron, and grading cron.
- Removed generated Python cache files from the deployment package.

## Render Blueprint
When creating the Blueprint, use:
- Branch: `main`
- Blueprint Path: `render.yaml`

Upload the **contents** of this extracted folder to the root of the GitHub repository.

## 4.1.0 — Render deployment hardening
- Added a root-level fallback Dockerfile.
- Changed Blueprint Docker paths to explicit repository-root paths.
- Added explicit Docker build contexts for API, web, and cron services.
- Removed dependency on manually configured Root Directory values.
- Added fresh deployment instructions.
