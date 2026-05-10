from collections import defaultdict

import aiohttp


async def get_solved_problem_count(handle: str) -> int | None:
    """Calculates the number of solved problems for a Codeforces user."""
    url = f"https://codeforces.com/api/user.status?handle={handle}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                data = await response.json()
                if data["status"] == "OK":
                    solved_problems = {
                        (s["problem"]["contestId"], s["problem"]["index"])
                        for s in data["result"]
                        if s["verdict"] == "OK"
                    }
                    return len(solved_problems)
                return None

        except aiohttp.ClientError:
            return None


async def get_solved_tags(handle: str) -> list[dict]:
    """Aggregates problem tags across distinct solved problems (topic analysis).

    Returns a list of ``{"topic": str, "count": int}`` dicts sorted by count.
    """
    url = f"https://codeforces.com/api/user.status?handle={handle}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                data = await response.json()
        except aiohttp.ClientError:
            return []

    if data.get("status") != "OK":
        return []

    seen: set[tuple] = set()
    tag_counts: defaultdict = defaultdict(int)
    for submission in data["result"]:
        if submission.get("verdict") != "OK":
            continue
        problem = submission.get("problem", {})
        key = (problem.get("contestId"), problem.get("index"))
        if key in seen:
            continue
        seen.add(key)
        for tag in problem.get("tags", []):
            tag_counts[tag] += 1

    return [
        {"topic": topic, "count": count}
        for topic, count in sorted(
            tag_counts.items(), key=lambda kv: kv[1], reverse=True
        )
    ]
