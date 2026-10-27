"""Fixtures compartilhadas para os testes E2E (Playwright + Uvicorn)."""

from __future__ import annotations

import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@pytest.fixture(scope="session")
def server_url():
    pytest.importorskip(
        "playwright.sync_api",
        reason="Playwright não instalado; rode 'pip install -r requirements-dev.txt'.",
    )
    port = _free_port()
    base_url = f"http://127.0.0.1:{port}"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")

    log = tempfile.TemporaryFile(mode="w+", encoding="utf-8", errors="replace")
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.api.server:app",
         "--host", "127.0.0.1", "--port", str(port), "--log-level", "warning"],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=log,
        stderr=subprocess.STDOUT,
    )

    try:
        deadline = time.time() + 60
        while time.time() < deadline:
            if process.poll() is not None:
                log.seek(0)
                raise RuntimeError(f"Servidor encerrou ao iniciar:\n{log.read()}")
            try:
                with urllib.request.urlopen(f"{base_url}/api/health", timeout=1):
                    pass
                break
            except Exception:
                time.sleep(0.3)
        else:
            log.seek(0)
            raise RuntimeError(f"Servidor não respondeu em 60s:\n{log.read()}")
        yield base_url
    finally:
        process.terminate()
        try:
            process.wait(timeout=15)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
        log.close()
