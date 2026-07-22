import secrets

for name in ("JWT_SECRET", "REFRESH_TOKEN_PEPPER", "CRON_SECRET"):
    print(f"{name}={secrets.token_urlsafe(64)}")
