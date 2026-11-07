from _common import BACKEND_DIR  # noqa: F401
from app.core.config import settings
from app.db.models import Conversion
from app.db.session import SessionLocal
from sqlalchemy import delete, func, select


def main() -> None:
    with SessionLocal() as db:
        expired = db.scalars(
            select(Conversion).where(Conversion.ttl < func.now())
        ).all()
        for conversion in expired:
            (settings.upload_dir / conversion.input_url).unlink(missing_ok=True)
            if conversion.output_url:
                (settings.output_dir / conversion.output_url).unlink(missing_ok=True)
        result = db.execute(
            delete(Conversion).where(Conversion.ttl < func.now())
        )
        db.commit()
    print(f"Expired jobs removed: {result.rowcount or 0}")


if __name__ == "__main__":
    main()
