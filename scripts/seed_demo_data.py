from secrets import token_urlsafe
from pathlib import Path

from _common import BACKEND_DIR  # noqa: F401
from app.core.config import settings
from app.db.models import Conversion, User
from app.db.session import SessionLocal
from app.services.passwords import hash_password
from fpdf import FPDF
from sqlalchemy import select


DEMO_EMAILS = ("demo1@conprezer.local", "demo2@conprezer.local")


def create_sample_pdf(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=16)
    pdf.cell(text="Conprezer demo conversion")
    pdf.output(str(path))


def main() -> None:
    passwords = {email: token_urlsafe(24) for email in DEMO_EMAILS}
    settings.output_dir.mkdir(parents=True, exist_ok=True)

    with SessionLocal() as db:
        users: dict[str, User] = {}
        for email in DEMO_EMAILS:
            user = db.scalar(select(User).where(User.email == email))
            if user is None:
                user = User(email=email, password_hash=hash_password(passwords[email]))
                db.add(user)
            else:
                user.password_hash = hash_password(passwords[email])
            users[email] = user
        db.commit()
        for user in users.values():
            db.refresh(user)

        demo_user = users[DEMO_EMAILS[0]]
        conversion = db.scalar(
            select(Conversion)
            .where(
                Conversion.user_id == demo_user.id,
                Conversion.input_type == "docx",
                Conversion.output_type == "pdf",
                Conversion.status == "completed",
            )
            .order_by(Conversion.id)
            .limit(1)
        )
        if conversion is None:
            output_name = f"demo-{demo_user.id}.pdf"
            conversion = Conversion(
                user_id=demo_user.id,
                input_type="docx",
                output_type="pdf",
                status="completed",
                input_url="demo.docx",
                output_url=output_name,
                original_size=1024,
                output_size=0,
            )
            create_sample_pdf(settings.output_dir / output_name)
            conversion.output_size = (settings.output_dir / output_name).stat().st_size
            db.add(conversion)
        elif conversion.output_url and not (settings.output_dir / conversion.output_url).is_file():
            create_sample_pdf(settings.output_dir / conversion.output_url)
            conversion.output_size = (settings.output_dir / conversion.output_url).stat().st_size
        db.commit()

    print("Demo users are ready (passwords are regenerated each time this script runs):")
    for email, password in passwords.items():
        print(f"  {email}: {password}")


if __name__ == "__main__":
    main()
