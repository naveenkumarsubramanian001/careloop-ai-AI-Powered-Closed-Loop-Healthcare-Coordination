import os

# Mock MinIO Client
class MinIOClient:
    def __init__(self):
        self.endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
        self.access_key = os.getenv("MINIO_ROOT_USER", "careloop")
        self.secret_key = os.getenv("MINIO_ROOT_PASSWORD", "careloop_minio_password")
        self.bucket = "careloop-documents"
        
    def upload_file(self, patient_id: str, file_name: str, file_bytes: bytes) -> str:
        """Mock upload to MinIO and return a path."""
        path = f"patients/{patient_id}/documents/{file_name}"
        # In real life, use minio-python to put_object
        return path

    def get_file(self, path: str) -> bytes:
        """Mock get file from MinIO."""
        return b"mock file content"

    def delete_file(self, path: str):
        """Mock delete file from MinIO."""
        pass

minio_client = MinIOClient()
