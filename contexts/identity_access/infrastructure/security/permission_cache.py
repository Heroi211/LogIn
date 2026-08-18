from __future__ import annotations

import time
from threading import Lock


class PermissionCache:
    """Cache in-process de permissões por papel (adequado para instância única)."""

    def __init__(self, ttl_seconds: int = 60) -> None:
        self._ttl = ttl_seconds
        self._store: dict[int, tuple[frozenset[str], float]] = {}
        self._lock = Lock()

    def get(self, role_id: int) -> frozenset[str] | None:
        now = time.monotonic()
        with self._lock:
            entry = self._store.get(role_id)
            if entry is None:
                return None
            perms, expires_at = entry
            if now >= expires_at:
                del self._store[role_id]
                return None
            return perms

    def set(self, role_id: int, permissions: frozenset[str]) -> None:
        with self._lock:
            self._store[role_id] = (permissions, time.monotonic() + self._ttl)

    def invalidate(self, role_id: int | None = None) -> None:
        with self._lock:
            if role_id is None:
                self._store.clear()
            else:
                self._store.pop(role_id, None)


_permission_cache = PermissionCache()


def get_permission_cache() -> PermissionCache:
    return _permission_cache
