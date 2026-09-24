import threading
import time
from collections import defaultdict, deque

from fastapi import HTTPException, Request, status

from hospital_feedback_system.config import settings

_registry: list["RateLimiter"] = []


class RateLimiter:
    def __init__(self, name: str, max_calls: int, window_seconds: int):
        self.name = name
        self.max_calls = max_calls
        self.window_seconds = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()
        _registry.append(self)

    def __call__(self, request: Request) -> None:
        key = request.client.host if request.client else "unknown"
        now = time.monotonic()
        with self._lock:
            hits = self._hits[key]
            cutoff = now - self.window_seconds
            while hits and hits[0] <= cutoff:
                hits.popleft()
            if len(hits) >= self.max_calls:
                retry_after = max(1, int(self.window_seconds - (now - hits[0])) + 1)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please try again later.",
                    headers={"Retry-After": str(retry_after)},
                )
            hits.append(now)
            if len(self._hits) > 10_000:
                self._prune(cutoff)

    def _prune(self, cutoff: float) -> None:
        stale = [k for k, hits in self._hits.items() if not hits or hits[-1] <= cutoff]
        for k in stale:
            del self._hits[k]

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


def reset_all_limiters() -> None:
    for limiter in _registry:
        limiter.reset()


login_limiter = RateLimiter("login", settings.LOGIN_RATE_LIMIT, settings.RATE_LIMIT_WINDOW_SECONDS)
qr_scan_limiter = RateLimiter(
    "qr_scan", settings.QR_SCAN_RATE_LIMIT, settings.RATE_LIMIT_WINDOW_SECONDS
)