# EdgeBoard v3

EdgeBoard is a subscription-ready sports analytics platform. This repository contains a production-oriented MLB launch module with a FastAPI API, a Next.js App Router frontend, PostgreSQL persistence, Stripe subscriptions, secure cookie authentication, automated model refreshes, official-pick tracking, grading, ROI/CLV reporting, and an admin operations center.

## What is included

- Public marketing site, pricing page, model record, and free-pick endpoint
- Member registration, login, refresh-token rotation, email verification hooks, and password reset hooks
- Free, Pro, and Elite entitlement tiers
- Stripe Checkout, Customer Portal, and signed webhook processing
- MLB schedule, team/pitcher statistics, FanDuel/DraftKings odds, weather, and park inputs
- Hybrid projection engine with market anchoring and Monte Carlo simulation
- Moneyline, run-line, and total evaluation
- Frozen official cards, bet grading, units, ROI, and closing-line value
- Premium dashboard, game pages, history/performance center, and admin center
- Render Blueprint, Dockerfiles, Docker Compose, Alembic migrations, and tests
- Sport-module architecture designed for later NFL/NBA expansion

## Important limits

This release uses sources that can be obtained reliably from the configured APIs. Umpire assignments, verified injury impact, public betting percentages, and sharp/steam feeds are represented as extension points rather than fabricated data. Add a licensed provider before exposing those labels to paying customers.

## Repository layout

```text
apps/api   FastAPI + SQLAlchemy + Stripe + MLB model
apps/web   Next.js 16 App Router frontend
render.yaml
```

## Local setup

1. Copy `.env.example` to `.env` and replace every placeholder.
2. Install Docker Desktop.
3. Run:

```bash
docker compose up --build
```

4. Open `http://localhost:3000`.
5. API docs are at `http://localhost:8000/docs` in development.

Create the first admin account:

```bash
docker compose exec api python -m app.seed
```

Refresh model data manually:

```bash
curl -X POST http://localhost:8000/api/v1/admin/refresh \
  -H "X-Cron-Secret: replace-me"
```

## Stripe setup

Create recurring Stripe Prices for Pro and Elite, then set:

```text
STRIPE_PRICE_PRO_MONTHLY
STRIPE_PRICE_ELITE_MONTHLY
```

Register this webhook endpoint:

```text
https://YOUR_API_DOMAIN/api/v1/webhooks/stripe
```

Listen for at least:

- `checkout.session.completed`
- `customer.subscription.created`
- `customer.subscription.updated`
- `customer.subscription.deleted`
- `invoice.paid`
- `invoice.payment_failed`

Use Stripe test mode until access provisioning, cancellations, failed payments, and portal changes are verified end-to-end.

## Render deployment

The included `render.yaml` defines:

- `edgeboard-api` web service
- `edgeboard-web` Next.js web service
- `edgeboard-refresh` cron job
- `edgeboard-grade` cron job
- PostgreSQL database

In Render, create a new Blueprint from this repository. Fill all environment variables marked `sync: false`.

## Before charging customers

- Rotate any API key that has ever been committed publicly.
- Put the product behind your own domain and HTTPS.
- Complete Terms, Privacy, Refund, Responsible Gambling, and jurisdiction review with qualified counsel.
- Add transactional email, uptime monitoring, error tracking, database backups, and a support workflow.
- Run the model in shadow mode and publish an independently auditable record before marketing performance claims.
- Never imply guaranteed profit.

## License

All rights reserved. See `LICENSE.md`.
