#!/usr/bin/env python3
"""Gera esqueleto de bounded context em contexts/<nome>/."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTEXTS = ROOT / "contexts"


def _slug(name: str) -> str:
    slug = re.sub(r"[^a-z0-9_]+", "_", name.strip().lower())
    if not slug or not slug.replace("_", "").isalnum():
        raise ValueError("Nome inválido — use letras, números e underscore.")
    return slug


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        print(f"skip (exists): {path.relative_to(ROOT)}")
        return
    path.write_text(content, encoding="utf-8")
    print(f"created: {path.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Cria bounded context template")
    parser.add_argument("name", help="Nome do contexto (ex.: ticket_management)")
    args = parser.parse_args()

    slug = _slug(args.name)
    base = CONTEXTS / slug
    if base.exists() and any(base.iterdir()):
        print(f"Erro: {base} já existe e não está vazio.", file=sys.stderr)
        return 1

    title = slug.replace("_", " ").title()
    pkg = slug

    dirs = [
        base / "domain" / "entities",
        base / "domain" / "value_objects",
        base / "application" / "use_cases",
        base / "application" / "ports",
        base / "application" / "dto",
        base / "infrastructure" / "persistence",
        base / "presentation" / "api" / "v1" / "endpoints",
        base / "presentation" / "schemas",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        _write(d / ".gitkeep", "")

    _write(
        base / "README.md",
        f"# Bounded Context: {title}\n\nGerado por `scripts/new_context.py`. Veja `contexts/_template/README.md`.\n",
    )
    _write(base / "domain" / "public_api.py", f'"""API pública do contexto {title}."""\n\n__all__: list[str] = []\n')
    _write(base / "domain" / "exceptions.py", "class DomainError(Exception):\n    pass\n")
    _write(
        base / "presentation" / "api" / "v1" / "api.py",
        "from fastapi import APIRouter\n\nrouter = APIRouter()\n",
    )

    print(f"\nContexto '{slug}' criado em contexts/{slug}/")
    print("Próximos passos:")
    print(f"  1. Implemente use cases em contexts/{slug}/application/")
    print(f"  2. Registre router em bootstrap/app.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
