import http.cookiejar
import json
import os
import time
import uuid
import urllib.error
import urllib.request
from io import BytesIO

import pytest
from docx import Document

from _common import BACKEND_DIR  # noqa: F401


API_URL = os.getenv("CONPREZER_API_URL", "http://127.0.0.1:8000").rstrip("/")


def test_docx_conversion_smoke() -> None:
    document = Document()
    document.add_paragraph(f"Conprezer smoke test {uuid.uuid4()}")
    document_bytes = BytesIO()
    document.save(document_bytes)

    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    boundary = f"----Conprezer{uuid.uuid4().hex}"
    payload = document_bytes.getvalue()
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="file"; filename="smoke.docx"\r\n'
        "Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document\r\n\r\n"
    ).encode() + payload + f"\r\n--{boundary}--\r\n".encode()
    request = urllib.request.Request(
        f"{API_URL}/api/convert",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    try:
        with opener.open(request, timeout=30) as response:
            job = json.loads(response.read())
    except urllib.error.URLError as error:
        pytest.fail(f"Could not submit DOCX to {API_URL}: {error}")

    conversion_id = job.get("conversion_id")
    assert isinstance(conversion_id, int), "API response did not include conversion_id"
    assert job.get("status") in {"pending", "processing", "completed"}

    deadline = time.monotonic() + 90
    status_url = f"{API_URL}/api/conversions/{conversion_id}"
    while time.monotonic() < deadline:
        with opener.open(status_url, timeout=15) as response:
            status = json.loads(response.read())
        if status["status"] == "completed":
            break
        assert status["status"] != "failed", f"Conversion {conversion_id} failed"
        time.sleep(1)
    else:
        pytest.fail(f"Conversion {conversion_id} did not complete before timeout")

    download_url = status.get("download_url")
    assert download_url, "Completed conversion did not include download_url"
    if download_url.startswith("/"):
        download_url = f"{API_URL}{download_url}"
    with opener.open(download_url, timeout=30) as response:
        pdf = response.read()
        assert response.headers.get_content_type() == "application/pdf"
    assert pdf.startswith(b"%PDF-"), "Download did not contain a valid PDF header"
    assert b"%%EOF" in pdf[-1024:], "Downloaded PDF is missing its end-of-file marker"
