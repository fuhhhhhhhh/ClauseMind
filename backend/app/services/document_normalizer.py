"""Document normalizer: convert MinerU markdown into structured contract JSON."""

import json
import re
from pathlib import Path


# ── Regex patterns ───────────────────────────────────────────────────────────

SECTION_RE = re.compile(
    r"^(第[一二三四五六七八九十百千0-9]+条|[一二三四五六七八九十]+、|[0-9]+[.、]|[0-9]+\.[0-9]+|（[一二三四五六七八九十]+）)"
)

PARTY_PATTERNS = [
    (r"甲方[：:]\s*(.+)", "甲方"),
    (r"乙方[：:]\s*(.+)", "乙方"),
    (r"买方[：:]\s*(.+)", "买方"),
    (r"卖方[：:]\s*(.+)", "卖方"),
    (r"委托方[：:]\s*(.+)", "委托方"),
    (r"受托方[：:]\s*(.+)", "受托方"),
    (r"出租方[：:]\s*(.+)", "出租方"),
    (r"承租方[：:]\s*(.+)", "承租方"),
    (r"发包方[：:]\s*(.+)", "发包方"),
    (r"承包方[：:]\s*(.+)", "承包方"),
]

TITLE_RE = re.compile(r"^#+\s*(.+)$|^(.+合同)$")


# ── Normalizer ───────────────────────────────────────────────────────────────


class DocumentNormalizer:
    """Normalize MinerU markdown into structured contract JSON."""

    def normalize(
        self,
        markdown_text: str,
        content_json_path: str | Path | None = None,
    ) -> dict:
        """Convert raw markdown text into structured contract JSON."""
        title = self._extract_title(markdown_text)
        contract_type = None
        tables = []
        if content_json_path:
            try:
                content = json.loads(Path(content_json_path).read_text(encoding="utf-8"))
                contract_type = self._extract_contract_type(content)
                tables = self._extract_tables(content)
            except (json.JSONDecodeError, FileNotFoundError, OSError):
                pass

        parties = self._extract_parties(markdown_text)
        sections, clauses = self._extract_sections_and_clauses(markdown_text)

        return {
            "title": title,
            "contract_type": contract_type,
            "parties": parties,
            "sections": sections,
            "clauses": clauses,
            "tables": tables,
            "metadata": {
                "parse_engine": "mineru",
                "content_json_available": bool(
                    content_json_path and Path(content_json_path).exists()
                ),
            },
        }

    # ── Private helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _extract_title(text: str) -> str | None:
        for line in text.splitlines()[:10]:
            line = line.strip()
            if not line:
                continue
            m = TITLE_RE.match(line)
            if m:
                return (m.group(1) or m.group(2)).strip()
        return None

    @staticmethod
    def _extract_contract_type(content: list) -> str | None:
        if content and isinstance(content[0], dict):
            ctype = content[0].get("type")
            if ctype and isinstance(ctype, str):
                return ctype
        return None

    @staticmethod
    def _extract_tables(content: list) -> list[dict]:
        tables = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "table":
                tables.append({
                    "table_id": f"T{len(tables) + 1}",
                    "html": item.get("html", ""),
                    "page": item.get("page"),
                    "caption": item.get("caption", ""),
                })
        return tables

    @staticmethod
    def _extract_parties(text: str) -> list[dict]:
        parties = []
        seen = set()
        for pattern, role in PARTY_PATTERNS:
            m = re.search(pattern, text)
            if m and role not in seen:
                name = m.group(1).strip()
                parties.append({
                    "name": name,
                    "role": role,
                    "source": m.group(0).strip(),
                })
                seen.add(role)
        return parties

    @staticmethod
    def _extract_sections_and_clauses(text: str) -> tuple[list[dict], list[dict]]:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        sections: list[dict] = []
        clauses: list[dict] = []
        current_section: dict | None = None

        for line in lines:
            if SECTION_RE.match(line):
                if current_section:
                    sections.append(current_section)
                sec_id = f"S{len(sections) + 1}"
                current_section = {
                    "id": sec_id,
                    "title": line,
                    "order_index": len(sections) + 1,
                    "clause_ids": [],
                }
                clause = {
                    "id": f"C{len(clauses) + 1}",
                    "section_id": sec_id,
                    "title": line,
                    "text": line,
                    "order_index": len(clauses) + 1,
                    "clause_type": "heading",
                }
                clauses.append(clause)
                current_section["clause_ids"].append(clause["id"])
            elif current_section:
                clause = {
                    "id": f"C{len(clauses) + 1}",
                    "section_id": current_section["id"],
                    "title": line[:60],
                    "text": line,
                    "order_index": len(clauses) + 1,
                }
                clauses.append(clause)
                current_section["clause_ids"].append(clause["id"])

        if current_section:
            sections.append(current_section)

        if not sections and text.strip():
            sec_id = "S1"
            sections.append({
                "id": sec_id,
                "title": "全文",
                "order_index": 1,
                "clause_ids": [],
            })
            for i, line in enumerate(lines):
                cid = f"C{i + 1}"
                clauses.append({
                    "id": cid,
                    "section_id": sec_id,
                    "title": line[:60],
                    "text": line,
                    "order_index": i + 1,
                })
                sections[0]["clause_ids"].append(cid)

        return sections, clauses
