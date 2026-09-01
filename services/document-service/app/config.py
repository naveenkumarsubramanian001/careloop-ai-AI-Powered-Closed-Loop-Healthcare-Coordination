from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    APP_NAME: str = "document-service"
    APP_VERSION: str = "1.0.0"
    APP_ENV: str = os.getenv("APP_ENV", "development")

    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "postgres")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "careloop")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "careloop")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "careloop_dev_password")

    MINIO_ENDPOINT: str = os.getenv("MINIO_ENDPOINT", "minio:9000")
    MINIO_ACCESS_KEY: str = os.getenv("MINIO_ROOT_USER", "careloop")
    MINIO_SECRET_KEY: str = os.getenv("MINIO_ROOT_PASSWORD", "careloop_minio_password")
    MINIO_SECURE: bool = os.getenv("MINIO_SECURE", "false").lower() == "true"
    MINIO_BUCKET: str = os.getenv("MINIO_BUCKET", "documents")

    def get_database_url(self) -> str:
        return (
            f"postgresql+psycopg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )


settings = Settings()