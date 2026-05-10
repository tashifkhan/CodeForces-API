import aiohttp

from models.rating import RatingHistory


async def get_user_rating(handle: str) -> list[RatingHistory] | None:
    """Fetches the rating history of a Codeforces user."""
    url = f"https://codeforces.com/api/user.rating?handle={handle}"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                data = await response.json()
                return data["result"] if data["status"] == "OK" else None
        except aiohttp.ClientError:
            return None
