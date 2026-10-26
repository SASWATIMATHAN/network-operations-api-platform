"""Initialize Lab 12 authentication storage and provision the first admin."""

import getpass

from sqlalchemy import select

from app.database import Base, SessionLocal, engine

from auth_models import AuthUser
from security import hash_password


def main() -> None:
    # Create only this lab's table; do not alter existing project tables.
    AuthUser.__table__.create(bind=engine, checkfirst=True)

    with SessionLocal() as db:
        existing_admin = db.scalar(
            select(AuthUser.username).where(AuthUser.role == "ADMIN").limit(1)
        )

        if existing_admin:
            print("An ADMIN account already exists. No account was created.")
            return

        username = input("New administrator username: ").strip()

        if len(username) < 3 or len(username) > 80:
            raise SystemExit("Username must contain 3–80 characters.")

        if not all(char.isalnum() or char in "_.-" for char in username):
            raise SystemExit(
                "Use only letters, numbers, dots, underscores, or hyphens."
            )

        if db.get(AuthUser, username):
            raise SystemExit("That username already exists.")

        password = getpass.getpass("New administrator password (12+ characters): ")
        confirmation = getpass.getpass("Confirm administrator password: ")

        if password != confirmation:
            raise SystemExit("Passwords do not match.")

        try:
            password_hash = hash_password(password)
        except ValueError as exc:
            raise SystemExit(str(exc)) from exc

        admin = AuthUser(
            username=username,
            password_hash=password_hash,
            role="ADMIN",
            is_active=True,
        )

        db.add(admin)
        db.commit()

        print(f"Administrator account '{username}' created successfully.")


if __name__ == "__main__":
    main()
