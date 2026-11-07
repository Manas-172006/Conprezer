from datetime import datetime

from pydantic import BaseModel


class ConversionResponse(BaseModel):
    id: int
    conversion_id: int
    job_id: int
    input_type: str
    output_type: str
    status: str
    original_size: int
    output_size: int | None
    created_at: datetime
    expires_at: datetime | None = None
    ttl: datetime | None = None
    download_url: str | None = None
