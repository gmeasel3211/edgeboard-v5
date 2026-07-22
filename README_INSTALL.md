# EdgeBoard Milestone 3 — Phase 3.1

## Included
- Fixes duplicate MLB game inserts with safe update-or-create logic
- Deduplicates repeated schedule records
- Safely updates team and pitcher snapshots
- Upserts Odds API games
- Skips exact duplicate odds snapshots
- Adds bounded automatic retries: immediately, after 30 seconds, and after 2 minutes
- Runs the first refresh immediately after API startup
- Classifies failures into understandable messages
- Replaces raw SQL tracebacks with a System Health dashboard
- Shows database, scheduler, MLB, odds, and weather status
- Shows freshness, counts, duration, and expandable job details

## Installation

1. Extract this ZIP.
2. Copy `patch_pipeline.py` into the root of `edgeboard-v3`.
3. Run:
   `python patch_pipeline.py`
4. Copy everything inside `replacement_files` into the repository root.
5. Replace the three matching files.
6. Commit and push.
7. Wait for both Render services to redeploy.
8. Open `/admin` and run **Full refresh**.
9. Open `/live-odds`.

The previous `ix_games_external_id` duplicate-key failure should stop because existing games are updated rather than inserted again.
