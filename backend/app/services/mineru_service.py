"""MinerU document parsing service.

Invokes the MinerU CLI to parse uploaded contract files (PDF/DOCX/images) and
collects the resulting Markdown, JSON, and layout outputs.
"""

import shutil
import subprocess
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import AppError


class MinerUService:
    """Wraps MinerU CLI invocation with error handling and output collection."""

    def __init__(
        self,
        command: str | None = None,
        backend: str | None = None,
        timeout: int | None = None,
    ) -> None:
        self.command = command or settings.mineru_command
        self.backend = backend or settings.mineru_backend
        self.timeout = timeout or settings.mineru_timeout

    def _check_command(self) -> None:
        """Raise if the MinerU command is not found on PATH."""
        if shutil.which(self.command) is None:
            raise AppError(
                f"MinerU 命令不可用: {self.command}，请检查 MINERU_COMMAND 配置",
                code=500,
                status_code=500,
            )

    def parse(self, input_path: str | Path, output_dir: str | Path) -> dict:
        """Run MinerU on *input_path* and collect outputs into *output_dir*."""
        self._check_command()

        input_path = Path(input_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        command = [
            self.command,
            "-p", str(input_path),
            "-o", str(output_dir),
            "-b", self.backend,
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
        except subprocess.TimeoutExpired:
            raise AppError(
                f"MinerU 执行超时（超过 {self.timeout} 秒），请增大 MINERU_TIMEOUT 或检查文件大小",
                code=500,
                status_code=500,
            )

        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            raise AppError(
                f"MinerU 执行失败 (exit {result.returncode}): {stderr}" if stderr
                else f"MinerU 执行失败 (exit {result.returncode})",
                code=500,
                status_code=500,
            )

        return self.collect_outputs(output_dir)

    def collect_outputs(self, output_dir: Path) -> dict:
        """Scan *output_dir* for MinerU output files and return a dict of paths / text."""
        markdown_files = list(output_dir.rglob("*.md"))
        content_json_files = list(output_dir.rglob("content_list.json"))
        middle_json_files = list(output_dir.rglob("*middle.json"))
        layout_pdf_files = list(output_dir.rglob("*layout*.pdf"))

        markdown_path = markdown_files[0] if markdown_files else None

        if markdown_path is None:
            raise AppError(
                "MinerU 未生成 Markdown 输出文件，解析可能不完整",
                code=500,
                status_code=500,
            )

        raw_markdown = markdown_path.read_text(encoding="utf-8") if markdown_path else ""

        return {
            "markdown_path": str(markdown_path),
            "content_json_path": str(content_json_files[0]) if content_json_files else None,
            "middle_json_path": str(middle_json_files[0]) if middle_json_files else None,
            "layout_pdf_path": str(layout_pdf_files[0]) if layout_pdf_files else None,
            "image_dir": str(output_dir),
            "raw_markdown": raw_markdown,
        }
