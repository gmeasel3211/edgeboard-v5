# Commercial launch checklist

## Product

- Run at least several weeks in shadow mode.
- Confirm every official recommendation is immutable and reproducible.
- Verify grading for favorites, underdogs, run lines, totals, and pushes.
- Verify closing-price capture and CLV direction.
- Label demo or delayed data clearly.

## Payments

- Test signup, upgrade, failed payment, cancellation, reactivation, and portal flows.
- Configure Stripe tax and customer emails as required.
- Use separate test and live webhook secrets.

## Reliability

- Add Sentry or equivalent error monitoring.
- Add uptime checks for web, API, refresh job, and grade job.
- Configure database backups and test restoring them.
- Add alerts for stale odds, failed refreshes, and zero-game slates.

## Legal and trust

- Obtain legal review for subscriptions, advertising claims, privacy, refunds, and gambling-related rules in each target jurisdiction.
- Publish responsible-gambling language and age restrictions.
- Never market picks as guaranteed profit.
- Preserve a complete public methodology and result-change policy.
