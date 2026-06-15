from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile


class FileStorageService:
    def __init__(self, upload_dir: Path) -> None:
        self.upload_dir = upload_dir

    async def save_upload(self, file: UploadFile) -> Path:
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        suffix = Path(file.filename or "").suffix.lower()
        target = self.upload_dir / f"{uuid4().hex}{suffix}"
        content = await file.read()
        target.write_bytes(content)
        return target
