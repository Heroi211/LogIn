from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field


@dataclass
class AppMetrics:
    requests_total: int = 0
    requests_errors: int = 0
    latency_ms_sum: float = 0.0
    started_at: float = field(default_factory=time.time)
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def record_request(self, *, duration_ms: float, status: int | None) -> None:
        with self._lock:
            self.requests_total += 1
            self.latency_ms_sum += duration_ms
            if status is None or status >= 500:
                self.requests_errors += 1

    def snapshot(self) -> dict:
        with self._lock:
            total = self.requests_total
            avg_latency = (self.latency_ms_sum / total) if total else 0.0
            uptime = time.time() - self.started_at
            return {
                "requests_total": total,
                "requests_errors": self.requests_errors,
                "latency_avg_ms": round(avg_latency, 3),
                "uptime_seconds": round(uptime, 1),
            }


metrics = AppMetrics()
