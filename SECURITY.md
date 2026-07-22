# Security policy

Report suspected vulnerabilities privately to the repository owner. Do not open a public issue containing credentials, customer data, or exploit details.

Production requirements:

- Rotate exposed credentials immediately.
- Keep Stripe, Odds API, JWT, database, email, and cron secrets out of Git.
- Require HTTPS and secure cookies.
- Verify Stripe webhook signatures against the raw request body.
- Restrict administrator accounts and use unique strong passwords.
- Enable database backups and restore testing.
- Review dependency alerts and deploy security updates promptly.
