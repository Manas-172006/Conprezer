import http.cookiejar
import json
import os
import time
import urllib.request
import uuid

import pytest

from _common import BACKEND_DIR, REPOSITORY_ROOT  # noqa: F401


API_URL = os.getenv("CONPREZER_API_URL", "http://127.0.0.1:8000").rstrip("/")
SAMPLE_DOCX = REPOSITORY_ROOT / "tests" / "sample.docx"


def test_docx_conversion_smoke() -> None:
    cookie_jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))
    try:
        sample = SAMPLE_DOCX.read_bytes()
        boundary = f"----Conprezer{uuid.uuid4().hex}"
        body = (
            f"--{boundary}\r\n"
            'Content-Disposition: form-data; name="file"; filename="sample.docx"\r\n'
            "Content-Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document\r\n\r\n"
        ).encode() + sample + f"\r\n--{boundary}--\r\n".encode()
        with opener.open(f"{API_URL}/api/config", timeout=15) as response:
            config = json.loads(response.read())

        if config["guest_mode"]:
            endpoint = "guest/convert"
        else:
            credentials = {
                "email": f"smoke-{uuid.uuid4().hex}@example.com",
                "password": f"Smoke-{uuid.uuid4().hex}",
            }
            auth_request = urllib.request.Request(
                f"{API_URL}/api/auth/signup",
                data=json.dumps(credentials).encode(),
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with opener.open(auth_request, timeout=15):
                pass
            endpoint = "convert"

        upload_request = urllib.request.Request(
            f"{API_URL}/api/{endpoint}",
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )
        with opener.open(upload_request, timeout=30) as response:
            job = json.loads(response.read())

        conversion_id = job.get("conversion_id")
        assert isinstance(conversion_id, int), "API response did not include conversion_id"
        assert job.get("status") in {"pending", "processing", "completed"}

        status_path = (
            f"/api/guest/status/{conversion_id}"
            if endpoint == "guest/convert"
            else f"/api/conversions/{conversion_id}"
        )
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            with opener.open(f"{API_URL}{status_path}", timeout=15) as response:
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
        print("Smoke test passed")
    except Exception as error:
        print(f"Smoke test failed: {error}")
        raise
