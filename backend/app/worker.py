import logging
import time
from datetime import datetime

from sqlalchemy import select, update

from app.core.config import settings
from app.db.models import Conversion
from app.db.session import SessionLocal
from app.services.conversion import compress_pdf, convert_docx_to_pdf

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def process_one() -> bool:
    cleanup_expired_guest_jobs()
    with SessionLocal() as db:
        conversion = db.scalar(
            select(Conversion)
            .where(Conversion.status == "pending")
            .order_by(Conversion.created_at)
            .limit(1)
        )
        if conversion is None:
            return False
        claimed = db.execute(
            update(Conversion)
            .where(Conversion.id == conversion.id, Conversion.status == "pending")
            .values(status="processing")
        )
        if claimed.rowcount != 1:
            db.rollback()
            return False
        db.commit()
        conversion_id = conversion.id
        input_name = conversion.input_url
        input_type = conversion.input_type
        output_type = conversion.output_type

    source = settings.upload_dir / input_name
    output_name = f"{conversion_id}.{output_type}"
    destination = settings.output_dir / output_name
    try:
        settings.output_dir.mkdir(parents=True, exist_ok=True)
        if input_type == "docx" and output_type == "pdf":
            convert_docx_to_pdf(source, destination)
        elif input_type == "pdf" and output_type == "pdf":
            compress_pdf(source, destination)
        else:
            raise ValueError(f"Unsupported conversion: {input_type} to {output_type}")
        output_size = destination.stat().st_size
        with SessionLocal() as db:
            db.execute(
                update(Conversion)
                .where(Conversion.id == conversion_id)
                .values(status="completed", output_url=output_name, output_size=output_size)
            )
            db.commit()
        logger.info("Conversion %s completed", conversion_id)
    except Exception:
        logger.exception("Conversion %s failed", conversion_id)
        destination.unlink(missing_ok=True)
        with SessionLocal() as db:
            db.execute(
                update(Conversion)
                .where(Conversion.id == conversion_id)
                .values(status="failed")
            )
            db.commit()
    return True


def cleanup_expired_guest_jobs() -> None:
    with SessionLocal() as db:
        expired = db.scalars(
            select(Conversion).where(
                Conversion.anon_id.is_not(None),
                Conversion.expires_at <= datetime.utcnow(),
                Conversion.status != "processing",
            )
        ).all()
        for conversion in expired:
            (settings.upload_dir / conversion.input_url).unlink(missing_ok=True)
            if conversion.output_url:
                (settings.output_dir / conversion.output_url).unlink(missing_ok=True)
            db.delete(conversion)
        if expired:
            db.commit()


def main() -> None:
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    while True:
        if not process_one():
            time.sleep(2)


if __name__ == "__main__":
    main()
