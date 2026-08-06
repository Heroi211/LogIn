"""
Agrega latência a partir de access.jsonl (e rotacionados access.jsonl.*).
Grava resumo CSV em PATH_MAINTENANCE_REPORTS.

Saída: uma linha por módulo de rota monitorado + linha consolidada (ALL).
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

_SRC = Path(__file__).resolve().parents[2]
_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from core.configs import settings  # noqa: E402
from core.logging_setup import setup_root_logging  # noqa: E402

logger = logging.getLogger(__name__)

MONITORED_ROUTES = {
    "users": "/users",
    "roles": "/roles",
}


def _load_jsonl_files(log_dir: Path) -> list[dict]:
    rows: list[dict] = []
    if not log_dir.is_dir():
        return rows
    for name in sorted(log_dir.glob("access.jsonl*")):
        if not name.is_file():
            continue
        with open(name, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return rows


def _normalize_latency_rows(raw: list[dict]) -> pd.DataFrame:
    out = []
    for r in raw:
        if "duration_ms" not in r:
            continue
        out.append(
            {
                "timestamp": r.get("ts") or r.get("timestamp"),
                "latency_ms": float(r["duration_ms"]),
                "status_code": r.get("status")
                if r.get("status") is not None
                else r.get("status_code"),
                "request_id": r.get("request_id"),
                "path": r.get("path", ""),
            }
        )
    return pd.DataFrame(out)


def _route_label(path: str) -> str:
    for label, fragment in MONITORED_ROUTES.items():
        if fragment in path:
            return label
    return "other"


def _build_summary(df: pd.DataFrame, label: str, slo_p95_ms: float) -> dict:
    if df.empty:
        return {}
    q = df["latency_ms"].quantile([0.5, 0.9, 0.95, 0.99])
    p95 = float(q.loc[0.95])
    error_mask = df["status_code"].apply(
        lambda s: isinstance(s, (int, float)) and s >= 400
    )
    error_rate = round(error_mask.sum() / len(df) * 100, 2)
    return {
        "route": label,
        "count": len(df),
        "mean_ms": round(float(df["latency_ms"].mean()), 2),
        "p50_ms": round(float(q.loc[0.5]), 2),
        "p90_ms": round(float(q.loc[0.9]), 2),
        "p95_ms": round(p95, 2),
        "p99_ms": round(float(q.loc[0.99]), 2),
        "error_rate_pct": error_rate,
        "slo_threshold_ms": slo_p95_ms,
        "slo_status": "ok" if p95 <= slo_p95_ms else "breach",
    }


def main() -> None:
    setup_root_logging()

    parser = argparse.ArgumentParser(description="Relatório de latência da API")
    parser.add_argument(
        "--slo-ms",
        type=float,
        default=500.0,
        help="Threshold p95 em ms para SLO geral (padrão: 500ms)",
    )
    args = parser.parse_args()

    log_dir = Path(settings.PATH_API_REQUEST_LOGS)
    if not log_dir.is_absolute():
        log_dir = _REPO_ROOT / log_dir

    raw = _load_jsonl_files(log_dir)
    if not raw:
        logger.error("Nenhuma linha válida em %s (access.jsonl*)", log_dir)
        sys.exit(1)

    df = _normalize_latency_rows(raw)
    if df.empty:
        logger.error("Nenhuma coluna duration_ms encontrada.")
        sys.exit(1)

    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
    df["route_label"] = df["path"].apply(_route_label)

    rows = []
    for label in list(MONITORED_ROUTES.keys()) + ["other"]:
        subset = df[df["route_label"] == label]
        summary = _build_summary(subset, label, slo_p95_ms=args.slo_ms)
        if summary:
            rows.append(summary)

    overall = _build_summary(df, "ALL", slo_p95_ms=args.slo_ms)
    if overall:
        rows.append(overall)

    summary_df = pd.DataFrame(rows)

    out_dir = Path(settings.PATH_MAINTENANCE_REPORTS)
    if not out_dir.is_absolute():
        out_dir = _REPO_ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_csv = out_dir / f"latency_summary_{stamp}.csv"
    summary_df.to_csv(out_csv, index=False)

    logger.info("Resumo gravado: %s", out_csv)
    logger.info("\n%s", summary_df.to_string(index=False))

    breaches = summary_df[summary_df["slo_status"] == "breach"]
    if not breaches.empty:
        logger.warning("SLO breach detectado nas rotas: %s", breaches["route"].tolist())
    else:
        logger.info("Todas as rotas dentro do SLO.")


if __name__ == "__main__":
    main()
