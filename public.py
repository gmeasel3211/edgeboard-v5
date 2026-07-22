from sqlalchemy import select

from .config import get_settings
from .db import Base, SessionLocal, engine
from .models import User
from .security import hash_password, normalize_email


def main() -> None:
    settings = get_settings()
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        email = normalize_email(settings.admin_email)
        user = db.scalar(select(User).where(User.email == email))
        if not user:
            user = User(
                email=email,
                display_name="EdgeBoard Admin",
                password_hash=hash_password(settings.admin_password),
                role="admin",
                tier="elite",
                is_active=True,
                is_verified=True,
            )
            db.add(user)
        else:
            user.role = "admin"
            user.tier = "elite"
            user.is_active = True
            user.is_verified = True
        db.commit()
        print(f"Admin ready: {email}")


if __name__ == "__main__":
    main()
