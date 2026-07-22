# Architecture

## Web

Next.js App Router provides public marketing pages and authenticated application screens. Premium data is always enforced by the API; hiding interface elements is not treated as authorization.

## API

FastAPI exposes versioned routes for authentication, subscriptions, public performance, member dashboards, game intelligence, and administration. SQLAlchemy stores all durable state in PostgreSQL.

## Authentication

- Argon2 password hashing
- Short-lived access JWT in an HttpOnly cookie
- Rotating opaque refresh tokens, stored only as keyed hashes
- Double-submit CSRF token for authenticated state changes
- Optional email verification and password reset through Resend

## Billing

Stripe Checkout starts subscriptions. Signed webhook events are the source of truth for entitlement changes. Stripe Customer Portal handles payment methods, invoices, and cancellations.

## Model data flow

1. Fetch MLB schedule and probable pitchers.
2. Fetch FanDuel and DraftKings moneylines, run lines, and totals.
3. Store each observed quote for line history and CLV.
4. Fetch season/recent team data, starter data, park data, and weather.
5. Build projected run means.
6. Run deterministic Monte Carlo simulations.
7. Blend independent results with a limited no-vig market anchor.
8. Evaluate each available price for edge, EV, quality, confidence, and stake.
9. Freeze a diversified official card within daily exposure limits.
10. Grade completed games and calculate CLV from the final pregame quote.

## Expansion

The database and API use an explicit `sport` field. Future NFL and NBA modules should implement the same provider/model interface while keeping shared account, subscription, audit, and performance systems.
