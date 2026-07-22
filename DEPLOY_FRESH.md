# EdgeBoard v4.1 — Fresh Render Deployment

## GitHub
1. Create a new empty repository.
2. Extract this ZIP.
3. Upload the contents of the extracted folder, not the ZIP itself.
4. Confirm the repository root shows `render.yaml`, `Dockerfile`, `apps`, and `README.md`.

## Render Blueprint (recommended)
1. Delete or suspend older EdgeBoard services so their old settings cannot interfere.
2. In Render select **New > Blueprint**.
3. Select the new repository and branch `main`.
4. Leave Blueprint Path as `render.yaml`.
5. Deploy the Blueprint.
6. Enter values for environment variables marked `sync: false`.

## Important
- Do not put `render.yaml` in a service's Root Directory field.
- Do not set Root Directory to `api`.
- The Blueprint uses explicit repo-root Dockerfile paths and build contexts.
- A fallback root-level `Dockerfile` is included so an accidentally created Docker web service can still find a Dockerfile. The Blueprint remains the recommended deployment method.
