"""File storage service with validation and UUID naming."""

from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import AppError

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


class FileStorageService:
    def __init__(self, upload_dir: Path | None = None) -> None:
        self.upload_dir = upload_dir or settings.upload_dir

    def validate_extension(self, filename: str) -> str:
        """Validate file extension and return lowercase suffix."""
        suffix = Path(filename).suffix.lower()
        if suffix not in ALLOWED_EXTENSIONS:
            raise AppError(
                f"不支持的文件类型: {suffix}，仅支持 {', '.join(sorted(ALLOWED_EXTENSIONS))}",
                code=400,
                status_code=400,
            )
        return suffix

    async def save_upload(self, file: UploadFile) -> tuple[str, str, int]:
        """
        Save an uploaded file with UUID filename.

        Returns tuple of (stored_file_name, file_path, file_size).
        Stored file name is UUID + original extension (safe for DB/FE).
        File path is the full server path (never exposed to frontend).
        """
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        original_filename = file.filename or "unknown"
        suffix = self.validate_extension(original_filename)

        stored_file_name = f"{uuid4().hex}{suffix}"
        target_path = self.upload_dir / stored_file_name

        content = await file.read()
        file_size = len(content)
        if file_size > MAX_FILE_SIZE:
            raise AppError(
                f"文件大小超过限制 ({MAX_FILE_SIZE // (1024 * 1024)}MB)",
                code=400,
                status_code=400,
            )

        target_path.write_bytes(content)
        return stored_file_name, str(target_path), file_size
