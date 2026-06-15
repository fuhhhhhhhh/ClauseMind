import subprocess
from pathlib import Path

from app.core.config import settings


class MinerUService:
    def parse(self, input_path: str | Path, output_dir: str | Path) -> dict:
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)

        command = [
            settings.mineru_command,
            "-p",
            str(input_path),
            "-o",
            str(output),
            "-b",
            settings.mineru_backend,
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=settings.mineru_timeout,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr or "MinerU command failed")

        return self.collect_outputs(output)

    def collect_outputs(self, output_dir: Path) -> dict:
        markdown_files = list(output_dir.rglob("*.md"))
        content_json_files = list(output_dir.rglob("content_list.json"))
        middle_json_files = list(output_dir.rglob("*middle.json"))
        layout_pdf_files = list(output_dir.rglob("*layout*.pdf"))

        markdown_path = markdown_files[0] if markdown_files else None
        raw_markdown = markdown_path.read_text(encoding="utf-8") if markdown_path else ""

        return {
            "markdown_path": str(markdown_path) if markdown_path else None,
            "content_json_path": str(content_json_files[0]) if content_json_files else None,
            "middle_json_path": str(middle_json_files[0]) if middle_json_files else None,
            "layout_pdf_path": str(layout_pdf_files[0]) if layout_pdf_files else None,
            "image_dir": str(output_dir),
            "raw_markdown": raw_markdown,
        }
