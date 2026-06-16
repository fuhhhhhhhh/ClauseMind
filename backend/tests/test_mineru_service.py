"""Tests for MinerU service subprocess configuration."""

import os
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from app.services.mineru_service import MinerUService


def test_parse_passes_configured_cuda_visible_devices(tmp_path: Path):
    service = MinerUService(
        command="mineru",
        backend="hybrid-auto-engine",
        timeout=10,
        cuda_visible_devices="2",
    )

    with (
        patch("shutil.which", return_value="/usr/bin/mineru"),
        patch("subprocess.run", return_value=SimpleNamespace(returncode=0, stderr="")) as mock_run,
        patch.object(service, "collect_outputs", return_value={"raw_markdown": "ok"}),
    ):
        service.parse("contract.pdf", tmp_path)

    assert mock_run.call_args.kwargs["env"]["CUDA_VISIBLE_DEVICES"] == "2"


def test_parse_does_not_force_cuda_visible_devices_when_unset(tmp_path: Path):
    service = MinerUService(
        command="mineru",
        backend="pipeline",
        timeout=10,
        cuda_visible_devices="",
    )

    with (
        patch.dict(os.environ, {}, clear=True),
        patch("shutil.which", return_value="/usr/bin/mineru"),
        patch("subprocess.run", return_value=SimpleNamespace(returncode=0, stderr="")) as mock_run,
        patch.object(service, "collect_outputs", return_value={"raw_markdown": "ok"}),
    ):
        service.parse("contract.pdf", tmp_path)

    assert "CUDA_VISIBLE_DEVICES" not in mock_run.call_args.kwargs["env"]
