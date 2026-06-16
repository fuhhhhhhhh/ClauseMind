"""Repository-level checks for shareable config and docs."""

from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECKED_FILES = [
    REPO_ROOT / "README.md",
    REPO_ROOT / "backend" / ".env.example",
    REPO_ROOT / "third_party" / "README.md",
]


def test_shareable_docs_do_not_contain_machine_specific_paths_or_secrets():
    forbidden_snippets = [
        "/home/fuxiangyu",
        "/home/",
        "miniconda3/envs/wepipeline",
        "api.yunjintao.com",
        "sk-",
    ]

    for path in CHECKED_FILES:
        text = path.read_text(encoding="utf-8")
        for snippet in forbidden_snippets:
            assert snippet not in text, f"{path.relative_to(REPO_ROOT)} contains {snippet}"
