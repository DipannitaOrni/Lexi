"""
Simple in-memory per-client token-bucket rate limiter, sufficient for a
single-process hackathon deployment. Keyed by client IP.
"""
import time
from collections import defaultdict
from threading import Lock
from typing import Dict, List


class RateLimiter:
    def __init__(self, max_requests_per_minute: int):
        self.max_requests = max_requests_per_minute
        self._hits: Dict[str, List[float]] = defaultdict(list)
        self._lock = Lock()

    def allow(self, client_key: str) -> bool:
        now = time.monotonic()
        window_start = now - 60.0
        with self._lock:
            hits = self._hits[client_key]
            # Drop hits outside the 60s window
            while hits and hits[0] < window_start:
                hits.pop(0)
            if len(hits) >= self.max_requests:
                return False
            hits.append(now)
            return True
