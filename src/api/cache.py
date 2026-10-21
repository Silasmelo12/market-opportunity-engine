"""
Unified Daily Cache with Redis support and transparent Local Memory + Disk fallback.
Strictly non-blocking on Redis connection/network failures (FR-018).
"""

import os
import json
import time
from pathlib import Path
from typing import Any, Optional, List, Dict

try:
    import redis
except ImportError:
    redis = None


class DailyCache:
    """
    Cache with daily/TTL invalidation.
    Prefers Redis if REDIS_URL environment variable is provided and reachable.
    Gracefully and transparently falls back to disk + process memory on any exception.
    """

    def __init__(self, cache_dir: Optional[Path] = None, default_ttl_seconds: int = 93600):
        self.default_ttl = default_ttl_seconds
        self.cache_dir = cache_dir or (Path(".cache") / "radar_daily")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._mem_store: Dict[str, Dict[str, Any]] = {}
        self.redis_client = None
        self._backend = "disk"

        redis_url = os.environ.get("REDIS_URL")
        if redis and redis_url:
            try:
                client = redis.from_url(redis_url, socket_timeout=0.5, socket_connect_timeout=0.5)
                client.ping()
                self.redis_client = client
                self._backend = "redis"
            except Exception:
                self.redis_client = None
                self._backend = "disk"

    @property
    def backend(self) -> str:
        """Returns active backend ('redis' or 'disk')."""
        if self.redis_client:
            try:
                self.redis_client.ping()
                return "redis"
            except Exception:
                return "disk"
        return "disk"

    def get(self, key: str) -> Optional[Any]:
        """Retrieves deserialized JSON data from active cache backend."""
        # 1. Try Redis if configured
        if self.redis_client:
            try:
                raw = self.redis_client.get(key)
                if raw is not None:
                    return json.loads(raw)
            except Exception:
                # Redis failure -> continue to fallback
                pass

        # 2. Check memory store
        mem_entry = self._mem_store.get(key)
        now = time.time()
        if mem_entry and (now - mem_entry["time"] < self.default_ttl):
            return mem_entry["data"]

        # 3. Check disk store
        safe_name = key.replace(":", "_").replace("/", "_").replace("*", "_") + ".json"
        cache_file = self.cache_dir / safe_name
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    entry = json.load(f)
                if now - entry.get("timestamp", 0) < self.default_ttl:
                    data = entry.get("data")
                    self._mem_store[key] = {"time": now, "data": data}
                    return data
            except Exception:
                pass

        return None

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Stores serializable value in cache."""
        actual_ttl = ttl or self.default_ttl
        now = time.time()

        # 1. Store in Redis
        if self.redis_client:
            try:
                dumped = json.dumps(value)
                self.redis_client.set(key, dumped, ex=actual_ttl)
            except Exception:
                pass

        # 2. Store in memory
        self._mem_store[key] = {"time": now, "data": value}

        # 3. Store in disk
        safe_name = key.replace(":", "_").replace("/", "_").replace("*", "_") + ".json"
        cache_file = self.cache_dir / safe_name
        try:
            entry = {"timestamp": now, "data": value}
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(entry, f)
        except Exception:
            pass


# Global singleton instance
daily_cache = DailyCache()
