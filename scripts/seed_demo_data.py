from _common import BACKEND_DIR  # noqa: F401
from app.db.models import Conversion, User
from app.db.session import SessionLocal
from sqlalchemy import select


DEMO_EMAILS = ("demo1@example.com", "demo2@example.com")
PASSWORD_HASH_PLACEHOLDER = "password-hash-placeholder"


def main() -> None:
    with SessionLocal() as db:
        users: dict[str, User] = {}
        for email in DEMO_EMAILS:
            user = db.scalar(select(User).where(User.email == email))
            if user is None:
                user = User(email=email, password_hash=PASSWORD_HASH_PLACEHOLDER)
                db.add(user)
            users[email] = user
        db.commit()
        for user in users.values():
            db.refresh(user)

        demo_user = users[DEMO_EMAILS[0]]
        conversion = db.scalar(
            select(Conversion)
            .where(
                Conversion.user_id == demo_user.id,
                Conversion.input_type == "pdf",
                Conversion.output_type == "docx",
                Conversion.status == "completed",
            )
            .order_by(Conversion.id)
            .limit(1)
        )
        if conversion is None:
            db.add(Conversion(
                user_id=demo_user.id,
                input_type="pdf",
                output_type="docx",
                status="completed",
                input_url="demo/sample.pdf",
                output_url="demo/sample.docx",
                original_size=0,
                output_size=0,
                ttl=None,
            ))
        db.commit()

    print("Seeded demo data")


if __name__ == "__main__":
    main()
