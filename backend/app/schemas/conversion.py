from datetime import datetime

from pydantic import BaseModel


class ConversionResponse(BaseModel):
    id: int
    input_type: str
    output_type: str
    status: str
    original_size: int
    output_size: int | None
    created_at: datetime
    download_url: str | None = None
