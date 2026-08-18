#!/usr/bin/env python3
"""Falha se domain/ importar FastAPI ou SQLAlchemy (Fase D)."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOMAIN_ROOT = ROOT / "contexts"

FORBIDDEN = re.compile(
    r"^\s*(?:from|import)\s+(fastapi|sqlalchemy|pydantic|starlette)",
    re.MULTILINE,
)

errors: list[str] = []

for py_file in DOMAIN_ROOT.rglob("domain/**/*.py"):
    text = py_file.read_text(encoding="utf-8")
    if FORBIDDEN.search(text):
        errors.append(str(py_file.relative_to(ROOT)))

if errors:
    print("Violações de arquitetura em domain/:", file=sys.stderr)
    for path in errors:
        print(f"  - {path}", file=sys.stderr)
    sys.exit(1)

print("check-arch: OK — nenhum import proibido em domain/")
