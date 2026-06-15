import re
from pathlib import Path


SECTION_RE = re.compile(r"^(第[一二三四五六七八九十百千0-9]+条|[一二三四五六七八九十]+、|[0-9]+[.、]|[0-9]+\\.[0-9]+|（[一二三四五六七八九十]+）)")


class DocumentNormalizer:
    def normalize(self, markdown_path: str | Path, content_json_path: str | Path | None = None) -> dict:
        text = Path(markdown_path).read_text(encoding="utf-8")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        sections = []
        current: dict | None = None

        for line in lines:
            if SECTION_RE.match(line):
                if current:
                    sections.append(current)
                current = {
                    "section_id": f"S{len(sections) + 1}",
                    "title": line,
                    "content": "",
                    "page": None,
                    "order": len(sections) + 1,
                    "source_text": line,
                }
            elif current:
                current["content"] = f"{current['content']}\n{line}".strip()
                current["source_text"] = f"{current['source_text']}\n{line}".strip()

        if current:
            sections.append(current)

        if not sections and text.strip():
            sections.append(
                {
                    "section_id": "S1",
                    "title": "全文",
                    "content": text.strip(),
                    "page": None,
                    "order": 1,
                    "source_text": text.strip(),
                }
            )

        return {
            "title": sections[0]["title"] if sections else "",
            "full_text": text,
            "sections": sections,
            "tables": [],
            "metadata": {
                "parse_engine": "mineru",
                "content_json_path": str(content_json_path) if content_json_path else None,
            },
        }
