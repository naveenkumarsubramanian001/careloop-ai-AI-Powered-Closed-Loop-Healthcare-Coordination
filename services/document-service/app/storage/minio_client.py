from io import BytesIO

from minio import Minio

from app.config import settings


class MinioStorage:
    def __init__(self):
        self.client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.bucket_name = settings.MINIO_BUCKET
        self._bucket_ready = False

    def ensure_bucket_exists(self):
        """Create the bucket if it does not already exist."""
        if self._bucket_ready:
            return
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)
        self._bucket_ready = True

    async def upload(self, storage_key: str, content: bytes, content_type: str):
        self.client.put_object(
            bucket_name=self.bucket_name,
            object_name=storage_key,
            data=BytesIO(content),
            length=len(content),
            content_type=content_type,
        )

    async def download(self, storage_key: str) -> bytes:
        response = self.client.get_object(self.bucket_name, storage_key)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    async def delete(self, storage_key: str):
        self.client.remove_object(self.bucket_name, storage_key)
