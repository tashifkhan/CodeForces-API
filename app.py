from fastapi import FastAPI, HTTPException
from typing import Optional, Dict, Any
import httpx
import asyncio
from redis import Redis
from pydantic import BaseModel

app = FastAPI(title="Codeforces API Wrapper")

# Redis connection
redis_client = Redis(host='localhost', port=6379, decode_responses=True)

# Base API client
class CodeforcesAPI:
    def __init__(self):
        self.base_url = "https://codeforces.com/api"
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"User-Agent": "Codeforces Readme Stats"}
        )

    async def get(self, endpoint: str) -> Dict[str, Any]:
        response = await self.client.get(endpoint)
        return response.json()

api_client = CodeforcesAPI()

# Cache implementation
class KVCache:
    def __init__(self, type_prefix: str):
        self.type_prefix = type_prefix

    async def get(self, key: str) -> Optional[str]:
        return redis_client.get(f"{key}/{self.type_prefix}")

    async def set(self, key: str, value: Any, expire: int = None):
        redis_client.set(f"{key}/{self.type_prefix}", str(value), ex=expire)

# Cache instances
last_rating_cache = KVCache("rating")
last_stats_cache = KVCache("stats")

# Response models
class StatsResponse(BaseModel):
    username: str
    fullName: str
    rating: int
    maxRating: int
    rank: str
    maxRank: str
    contestsCount: int
    problemsSolved: int
    submissions: int
    friendOfCount: int
    contribution: int

def capitalize(s: str) -> str:
    return s[0].upper() + s[1:] if s else s

def count_submissions(submissions: list) -> int:
    already_solved = set()
    count = 0
    for submission in submissions:
        problem_id = f"{submission['problem']['contestId']}-{submission['problem']['index']}"
        if submission['verdict'] == "OK" and problem_id not in already_solved:
            count += 1
            already_solved.add(problem_id)
    return count

async def fetch_with_timeout(fetch_func, username: str, last_cache: KVCache):
    try:
        return await asyncio.wait_for(fetch_func(), timeout=3.0)
    except asyncio.TimeoutError:
        cached_data = await last_cache.get(username)
        if cached_data:
            return cached_data
        raise HTTPException(status_code=500, detail="Codeforces Server Error")
    except Exception as e:
        if getattr(e, 'status_code', None) == 400:
            raise HTTPException(status_code=400, detail="Codeforces Handle Not Found")
        raise HTTPException(status_code=500, detail="Codeforces Server Error")

@app.get("/rating/{username}")
async def get_rating(username: str, cache_seconds: int = 300):
    async def fetch_rating():
        response = await api_client.get(f"/user.info?handles={username}")
        rating = response['result'][0].get('rating', 0)
        await last_rating_cache.set(username, rating, cache_seconds)
        return rating

    return await fetch_with_timeout(fetch_rating, username, last_rating_cache)

@app.get("/stats/{username}", response_model=StatsResponse)
async def get_stats(username: str, cache_seconds: int = 300):
    async def fetch_stats():
        # Fetch all required data concurrently
        user_info, rating_info, status_info = await asyncio.gather(
            api_client.get(f"/user.info?handles={username}"),
            api_client.get(f"/user.rating?handle={username}"),
            api_client.get(f"/user.status?handle={username}")
        )

        user_data = user_info['result'][0]
        stats = {
            "username": username,
            "fullName": f"{user_data.get('firstName', '')} {user_data.get('lastName', '')}".strip(),
            "rating": user_data.get('rating', 0),
            "maxRating": user_data.get('maxRating', 0),
            "rank": capitalize(user_data.get('rank', 'Unrated')),
            "maxRank": capitalize(user_data.get('maxRank', 'Unrated')),
            "contestsCount": len(rating_info['result']),
            "problemsSolved": count_submissions(status_info['result']),
            "submissions": len(status_info['result']),
            "friendOfCount": user_data.get('friendOfCount', 0),
            "contribution": user_data.get('contribution', 0)
        }
        
        await last_stats_cache.set(username, stats, cache_seconds)
        return stats

    return await fetch_with_timeout(fetch_stats, username, last_stats_cache)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, port=8000)