import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    mysql_host: str = os.getenv("MYSQL_HOST", "localhost")
    mysql_port: int = int(os.getenv("MYSQL_PORT", "3306"))
    mysql_database: str = os.getenv("MYSQL_DATABASE", "conprezer")
    mysql_user: str = os.getenv("MYSQL_USER", "app_user")
    mysql_password: str = os.getenv("MYSQL_PASSWORD", "placeholder_app_password")
    secret_key: str = os.getenv("SECRET_KEY", "local-development-only-change-this-secret")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    guest_mode: bool = os.getenv("GUEST_MODE", "false").lower() in {"1", "true", "yes", "on"}
    guest_job_ttl_hours: int = int(os.getenv("GUEST_JOB_TTL_HOURS", "24"))
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    upload_dir: Path = Path(os.getenv("UPLOAD_DIR", "data/uploads"))
    output_dir: Path = Path(os.getenv("OUTPUT_DIR", "data/outputs"))

    @property
    def database_url(self) -> str:
        from urllib.parse import quote_plus

        password = quote_plus(self.mysql_password)
        return (
            f"mysql+pymysql://{self.mysql_user}:{password}@"
            f"{self.mysql_host}:{self.mysql_port}/{self.mysql_database}"
        )


settings = Settings()
