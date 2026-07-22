# EdgeBoard v3 — Consolidated Milestone 3.1

Built directly from the uploaded project.

Included:
- Existing Milestone 2 application preserved
- Duplicate-safe game upserts and exact quote deduplication
- Friendly pipeline error classification
- Refresh duration tracking
- Scheduled refresh retries at 0, 30, and 120 seconds
- Admin-only System Health page at `/live-odds`
- API/database/scheduler/MLB/odds/weather status
- Upcoming games, 24-hour quote count, active picks, and bookmaker count
- Recent pipeline run summaries without raw database errors in the UI
- Rich pick reasoning, break-even probability, data quality, best sportsbook, and primary risks

Deployment:
1. Upload the contents of this folder to the root of `gmeasel3211/edgeboard-v3`.
2. Commit the changes to `main`.
3. Wait for Render to redeploy the API and web services.
4. Log in as admin, run a refresh, and open `/live-odds`.
