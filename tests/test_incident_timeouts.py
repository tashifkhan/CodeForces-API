"""Offline regressions for the Vercel timeout incident (no network, no Redis)."""

import asyncio
import json
import os
import sys
import time
import unittest
from collections import Counter
from unittest.mock import patch

import httpx

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app  # noqa: E402
from core import cache, rate_limit, runtime  # noqa: E402

REAL_ASYNC_CLIENT = httpx.AsyncClient
NOW = int(time.time())


def codeforces(calls, stall=False, status_override=None):
    """A fake Codeforces API behind httpx.MockTransport that counts each call."""

    async def handler(request):
        method = request.url.path.rsplit("/", 1)[-1]
        calls[method] += 1
        if stall:
            await asyncio.sleep(60)
        if status_override:
            status, body = status_override
            return httpx.Response(status, **body)
        result = {
            "user.info": [{"handle": "alice", "rating": 1500, "maxRating": 1600, "rank": "specialist",
                           "registrationTimeSeconds": NOW - 400 * 86400}],
            "user.rating": [{"contestId": 1, "contestName": "Round 1", "handle": "alice", "rank": 10,
                             "ratingUpdateTimeSeconds": NOW - 86400, "oldRating": 1400, "newRating": 1500}],
            "user.status": [
                {"contestId": 1, "creationTimeSeconds": NOW - 3600, "verdict": "OK",
                 "problem": {"contestId": 1, "index": "A", "tags": ["math"]}},
                {"contestId": 2, "creationTimeSeconds": NOW - 7200, "verdict": "OK",
                 "problem": {"contestId": 2, "index": "B", "tags": ["math", "dp"]}},
            ],
        }[method]
        return httpx.Response(200, json={"status": "OK", "result": result})

    transport = httpx.MockTransport(handler)
    return lambda *args, **kwargs: REAL_ASYNC_CLIENT(*args, **{**kwargs, "transport": transport})


class FakeStore:
    """Minimal in-memory store with redis-py's method signatures."""

    def __init__(self):
        self.data = {}
        self.lease_calls = []

    async def get(self, key):
        return self.data.get(key)

    async def setex(self, key, ttl, value):
        self.data[key] = value

    async def set(self, key, value, ex=None, px=None, nx=False):
        self.lease_calls.append({"ex": ex, "px": px, "nx": nx})
        if nx and key in self.data:
            return None
        self.data[key] = value
        return True

    async def eval(self, script, numkeys, *args):
        return None


class Base(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.calls = Counter()
        self.patches = [
            patch("core.middleware.redis_enabled", return_value=False),
            patch("core.source.redis_enabled", return_value=False),
            patch.object(cache, "get_redis", return_value=None),
        ]
        for item in self.patches:
            item.start()

    def tearDown(self):
        for item in reversed(self.patches):
            item.stop()

    async def get(self, path, upstream):
        with patch.object(runtime.httpx, "AsyncClient", upstream):
            transport = httpx.ASGITransport(app=app)
            async with REAL_ASYNC_CLIENT(transport=transport, base_url="http://test") as http:
                return await http.get(path, headers={"Origin": "https://example.org"})


class SharedSourceTests(Base):
    async def test_summary_downloads_each_source_once(self):
        response = await self.get("/alice", codeforces(self.calls))
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body["solved_problems_count"], 2)
        self.assertEqual(body["contests_count"], 2)
        self.assertEqual(body["rating_history"][0]["newRating"], 1500)
        self.assertEqual(self.calls, Counter({"user.info": 1, "user.status": 1, "user.rating": 1}))

    async def test_stats_shares_one_submission_download(self):
        response = await self.get("/alice/stats", codeforces(self.calls))
        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["totalSolved"], 2)
        self.assertEqual(data["topicAnalysis"][0], {"topic": "math", "count": 2})
        self.assertEqual(self.calls["user.status"], 1)

    async def test_card_fans_out_to_one_call_per_source(self):
        from services import canonical_mapper
        upstream = codeforces(self.calls)
        with patch.object(runtime.httpx, "AsyncClient", upstream):
            async with upstream() as http:
                current = runtime.RequestState(time.monotonic() + 5, http)
                token = runtime.state.set(current)
                try:
                    card = await canonical_mapper.build_card("alice")
                finally:
                    runtime.state.reset(token)
        self.assertEqual(card.stats.totalSolved, 2)
        self.assertEqual(self.calls, Counter({"user.info": 1, "user.status": 1, "user.rating": 1}))

    async def test_source_does_not_leak_across_requests(self):
        upstream = codeforces(self.calls)
        await self.get("/alice/stats", upstream)
        await self.get("/alice/stats", upstream)
        self.assertEqual(self.calls["user.status"], 2)
        self.assertIsNone(runtime.state.get())

    async def test_upstream_failures_map_to_controlled_statuses(self):
        cases = [
            # Codeforces answers an unknown handle with HTTP 400, not 404.
            (400, {"status": "FAILED", "comment": "handles: User with handle ghost not found"}, 404),
            (503, {"status": "FAILED", "comment": "Call limit exceeded"}, 503),
            (500, None, 502),
        ]
        for upstream_status, payload, expected in cases:
            with self.subTest(upstream_status=upstream_status):
                upstream = codeforces(self.calls, status_override=(upstream_status, {"json": payload}
                                                                  if payload else {"text": "<html>"}))
                response = await self.get("/ghost/profile", upstream)
                self.assertEqual(response.status_code, expected)


class DeadlineTests(Base):
    async def test_budget_returns_504_with_cors_and_cancels_route(self):
        cancelled = asyncio.Event()

        async def stalled(handle):
            try:
                await asyncio.sleep(60)
            finally:
                cancelled.set()

        started = time.monotonic()
        with patch.object(runtime, "REQUEST_BUDGET_SECONDS", 0.1), patch(
            "routes.summary.get_user_all_stats", side_effect=stalled
        ):
            response = await self.get("/alice", codeforces(self.calls))
        self.assertLess(time.monotonic() - started, 2)
        self.assertEqual(response.status_code, 504)
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertIn("access-control-allow-origin", response.headers)
        self.assertTrue(cancelled.is_set())

    async def test_stalled_upstream_is_cut_inside_the_budget(self):
        started = time.monotonic()
        with patch.object(runtime, "REQUEST_BUDGET_SECONDS", 1.0):
            response = await self.get("/alice/stats", codeforces(self.calls, stall=True))
        elapsed = time.monotonic() - started
        # The fetch keeps RESPONSE_RESERVE back, so the route answers itself.
        self.assertEqual(response.status_code, 504)
        self.assertEqual(response.json(), {"detail": "Codeforces upstream timed out"})
        self.assertLess(elapsed, 1.0)

    async def test_stale_copy_served_when_upstream_stalls(self):
        store = FakeStore()
        with patch.object(cache, "get_redis", return_value=store), patch(
            "core.source.redis_enabled", return_value=True
        ):
            await self.get("/alice/stats", codeforces(self.calls))
            self.assertTrue(any(c["nx"] and c["ex"] == 10 and c["px"] is None for c in store.lease_calls))
            # Age every cached source past its fresh TTL.
            for key, value in list(store.data.items()):
                if key.startswith("source:") and not key.endswith(":lease"):
                    payload = json.loads(value)
                    payload["at"] -= 600
                    store.data[key] = json.dumps(payload)
            store.data = {k: v for k, v in store.data.items() if not k.endswith(":lease")}
            with patch.object(runtime, "REQUEST_BUDGET_SECONDS", 1.0):
                response = await self.get("/alice/stats", codeforces(self.calls, stall=True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["data"]["totalSolved"], 2)
        self.assertEqual(response.headers["cache-control"], "no-store")
        self.assertEqual(json.loads(response.headers["x-data-state"])["source"]["status"], "stale")

    async def test_stalled_store_does_not_block_cache_or_rate_limiter(self):
        async def stalled(*args, **kwargs):
            await asyncio.sleep(60)

        class Stalled:
            get = setex = set = eval = staticmethod(stalled)

        started = time.monotonic()
        with patch.object(cache, "get_redis", return_value=Stalled()), patch.object(cache, "OPERATION_TIMEOUT", 0.02):
            self.assertIsNone(await cache.get_json("k"))
            await cache.set_json("k", {"ok": True}, 60)
            result = await rate_limit.check_rate_limit("ip:k", 60, 60, "ip")
        self.assertTrue(result.allowed)
        self.assertLess(time.monotonic() - started, 1)


if __name__ == "__main__":
    unittest.main()
