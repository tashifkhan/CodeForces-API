import requests
import time
from typing import List, Set, Optional
from models.base import UserAllStats, RatingHistory


def get_user_info(handles: List[str]):
    """Fetches information about Codeforces users."""
    url = f"https://codeforces.com/api/user.info?handles={';'.join(handles)}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "OK":
            return data["result"]
        return None
    except requests.exceptions.RequestException:
        return None



def get_user_rating(handle: str) -> Optional[List[RatingHistory]]:
    """Fetches the rating history of a Codeforces user."""
    url = f"https://codeforces.com/api/user.rating?handle={handle}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data["result"] if data["status"] == "OK" else None
    except requests.exceptions.RequestException:
        return None



def get_solved_problem_count(handle: str) -> Optional[int]:
    """Calculates the number of solved problems for a Codeforces user."""
    url = f"https://codeforces.com/api/user.status?handle={handle}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "OK":
            solved_problems = {(s["problem"]["contestId"], s["problem"]["index"]) 
                             for s in data["result"] if s["verdict"] == "OK"}
            return len(solved_problems)
        return None
    except requests.exceptions.RequestException:
        return None



def get_upcoming_contests(gym: bool = False):
    """Fetches a list of upcoming contests."""
    url = f"https://codeforces.com/api/contest.list?gym={str(gym).lower()}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "OK":
            current_time = time.time()
            return [c for c in data["result"] 
                   if c["phase"] == "BEFORE" and c["startTimeSeconds"] > current_time]
        return None
    except requests.exceptions.RequestException:
        return None



def get_contests_participated_by_user(handle: str) -> Set[int]:
    """Gets contests participated in by a user."""
    time.sleep(2)  # Rate limit
    url = f"https://codeforces.com/api/user.status?handle={handle}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "OK":
            return {s["contestId"] for s in data["result"] if "contestId" in s}
        return set()
    except requests.exceptions.RequestException:
        return set()



def get_common_contests(handles: List[str]) -> Set[int]:
    """Gets common contests for multiple users."""
    if not handles:
        return set()

    all_contests = []
    for handle in handles:
        contests = get_contests_participated_by_user(handle)
        if not contests:
            return set()
        all_contests.append(contests)

    return all_contests[0].intersection(*all_contests[1:])



def get_user_all_stats(handle: str) -> Optional[UserAllStats]:
    """Gets comprehensive statistics for a user."""
    if isinstance(handle, list):
        handle = handle[0] if handle else None
        if not handle:
            return None

    user_info = get_user_info([handle])
    if not user_info:
        return None

    contests = get_contests_participated_by_user(handle)
    solved_count = get_solved_problem_count(handle) or 0
    rating_history = get_user_rating(handle)

    all_stats = UserAllStats(**user_info[0])
    all_stats.contests_count = len(contests)
    all_stats.solved_problems_count = solved_count
    all_stats.rating_history = rating_history

    return all_stats
