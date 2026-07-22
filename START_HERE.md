# Start here

This package is a complete replacement project. Do not copy individual files into the old `edgeboard_mlb_production` directory.

## Safest GitHub method

Use GitHub Desktop so the folder structure stays intact.

1. Install and open GitHub Desktop.
2. Choose **File → Clone repository**.
3. Select `gmeasel3211/edgeboard-mlb` and clone it.
4. Open the cloned repository folder from GitHub Desktop.
5. Delete the old project files inside that local folder. Do not delete the hidden `.git` folder.
6. Copy **the contents of this `edgeboard-v3` folder** into the cloned repository folder. At the repository root, you should now see:

```text
apps/
docs/
scripts/
render.yaml
docker-compose.yml
README.md
```

7. In GitHub Desktop, enter the summary `Replace project with EdgeBoard v3 commercial foundation`.
8. Click **Commit to main**.
9. Click **Push origin**.

## Deploy

The new project is a monorepo and no longer uses `edgeboard_mlb_production` as Render's root directory.

The cleanest deployment is:

1. In Render, create a **New Blueprint**.
2. Select the `edgeboard-mlb` repository.
3. Render will detect the root `render.yaml`.
4. Supply every secret value Render asks for.
5. After the database and API deploy, run this once from the API shell:

```bash
python -m app.seed
```

6. Set `NEXT_PUBLIC_API_URL` to the public API URL.
7. Set the API's `FRONTEND_URL` and `CORS_ORIGINS` to the public web URL.
8. Redeploy both services.

Do not reuse an Odds API key that was previously committed to a public repository. Rotate it first.
