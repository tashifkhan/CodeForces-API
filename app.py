import requests
import json
import time
from typing import Dict, List, Optional, Any, Set
from pydantic import BaseModel, Field

class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str


class UserInfo(BaseModel):
    """Model for user information from Codeforces."""
    handle: str
    rating: Optional[int] = None
    maxRating: Optional[int] = None
    rank: Optional[str] = None
    maxRank: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    organization: Optional[str] = None
    contribution: Optional[int] = None
    registrationTimeSeconds: Optional[int] = None
    friendOfCount: Optional[int] = None
    titlePhoto: Optional[str] = None
    avatar: Optional[str] = None


class RatingChangeContest(BaseModel):
    """Model for contest in a rating change."""
    id: int
    name: str


class RatingHistory(BaseModel):
    """Model for rating change history."""
    contestId: int
    contestName: str
    handle: str
    rank: int
    ratingUpdateTimeSeconds: int
    oldRating: int
    newRating: int


class SolvedProblemsCount(BaseModel):
    """Model for the number of solved problems."""
    handle: str
    count: int


class Contest(BaseModel):
    """Model for a contest."""
    id: int
    name: str
    type: str
    phase: str
    frozen: bool
    durationSeconds: int
    startTimeSeconds: int
    relativeTimeSeconds: Optional[int] = None
    preparedBy: Optional[str] = None
    websiteUrl: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[int] = None
    kind: Optional[str] = None
    icpcRegion: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None
    season: Optional[str] = None


class UserAllStats(UserInfo):
    """Model for comprehensive user statistics including profile, contests, and problems."""
    contests_count: int = Field(0, description="Number of contests participated in")
    solved_problems_count: int = Field(0, description="Number of problems solved")
    rating_history: Optional[List[RatingHistory]] = Field(None, description="History of rating changes")


def get_user_info(handles):
    """
    Fetches information about Codeforces users.

    Args:
        handles: A list of Codeforces user handles.

    Returns:
        A list of user objects, or None if there was an error.
    """
    url = f"https://codeforces.com/api/user.info?handles={';'.join(handles)}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        data = response.json()
        if data["status"] == "OK":
            return data["result"]
        else:
            print(f"Error fetching user info: {data['comment']}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None

def get_user_rating(handle):
    """
    Fetches the rating history of a Codeforces user.

    Args:
        handle: The Codeforces user handle.

    Returns:
        A list of rating change objects, or None if there was an error.
    """
    url = f"https://codeforces.com/api/user.rating?handle={handle}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "OK":
            return data["result"]
        else:
            print(f"Error fetching user rating: {data['comment']}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    
def get_solved_problem_count(handle):
    """
    Calculates the number of solved problems for a Codeforces user.

    Args:
        handle: The Codeforces user handle.

    Returns:
        The number of solved problems, or None if there was an error.
    """
    url = f"https://codeforces.com/api/user.status?handle={handle}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "OK":
            solved_problems = set()
            for submission in data["result"]:
                if submission["verdict"] == "OK":
                    problem_id = (submission["problem"]["contestId"], submission["problem"]["index"])
                    solved_problems.add(problem_id)
            return len(solved_problems)
        else:
            print(f"Error fetching user status: {data['comment']}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    
def get_upcoming_contests(gym=False):
    """
    Fetches a list of upcoming contests from the Codeforces API.

    Args:
        gym: If True, only gym contests are returned. Otherwise, only regular contests.

    Returns:
        A list of upcoming contest objects, or None if there was an error.
    """
    url = f"https://codeforces.com/api/contest.list?gym={str(gym).lower()}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "OK":
            upcoming_contests = []
            current_time = time.time()  # Current time in seconds since epoch
            for contest in data["result"]:
                if contest["phase"] == "BEFORE" and contest["startTimeSeconds"] > current_time:
                    upcoming_contests.append(contest)
            return upcoming_contests
        else:
            print(f"Error fetching contest list: {data['comment']}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    

def get_contests_participated_by_user(handle):
    """
    Gets a list of contests that the given Codeforces user has participated in.

    Args:
        handle: A Codeforces user handle.

    Returns:
        A set of contest IDs representing the contests participated in by the user.
    """
    contests = set()
    time.sleep(2)  # Respect rate limit (1 request per 2 seconds)
    url = f"https://codeforces.com/api/user.status?handle={handle}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data["status"] == "OK":
            for submission in data["result"]:
                if 'contestId' in submission:
                    contests.add(submission["contestId"])
        else:
            print(f"Error fetching submissions for {handle}: {data['comment']}")
    except requests.exceptions.RequestException as e:
        print(f"Request error for {handle}: {e}")
    return contests


def get_common_contests(handles):
    """
    Gets the common contests that a list of Codeforces users have participated in.

    Args:
        handles: A list of Codeforces user handles.

    Returns:
        A set of contest IDs representing the contests participated in by all users.
    """
    if not handles:
        return set()  # No users, no contests

    common_contests = None  # Initialize to None

    for handle in handles:
        user_contests = get_contests_participated_by_user(handle)
        if user_contests is None:
            print(f"Could not retrieve contest data for {handle}. Skipping.")
            continue  # Skip to the next user

        if common_contests is None:
            # For the first user, initialize common_contests to their contests
            common_contests = user_contests
        else:
            # For subsequent users, take the intersection with the current common_contests
            common_contests = common_contests.intersection(user_contests)

    return common_contests if common_contests is not None else set()


def get_user_all_stats(handle):
    """
    Gets comprehensive statistics for a Codeforces user including profile info,
    number of contests participated in, and number of problems solved.

    Args:
        handle: A Codeforces user handle.

    Returns:
        A UserAllStats object with all user statistics, or None if there was an error.
    """
    user_info = get_user_info([handle])
    if not user_info:
        return None
    
    # Get contest participation
    contests = get_contests_participated_by_user(handle)
    contests_count = len(contests) if contests else 0
    
    # Get solved problems count
    solved_count = get_solved_problem_count(handle)
    if solved_count is None:
        solved_count = 0
    
    # Get rating history
    rating_history = get_user_rating(handle)
    
    # Create UserAllStats object
    all_stats = UserAllStats(**user_info[0])
    all_stats.contests_count = contests_count
    all_stats.solved_problems_count = solved_count
    all_stats.rating_history = rating_history
    
    return all_stats


if __name__ == '__main__':
    handles = ["tourist", "AdarSharma"]
    user_info = get_user_info(handles)

    if user_info:
        print("User Info:")
        for user in user_info:
            print(json.dumps(user, indent=4)) # Print formatted JSON
            print("-" * 20)
    
    for handle in handles:
        solved_count = get_solved_problem_count(handle)
        if solved_count is not None:
            print(f"Number of solved problems for {handle}: {solved_count}")
        else:
            print(f"Could not retrieve solved problem count for {handle}")

    upcoming = get_upcoming_contests()
    if upcoming:
        print("Upcoming Contests:")
        for contest in upcoming:
            print(f"  Name: {contest['name']}")
            print(f"  ID: {contest['id']}")
            print(f"  Start Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(contest['startTimeSeconds']))}")  # Format the time
            print("-" * 20)
    else:
        print("Could not retrieve upcoming contests.")

    for handle in handles:
        rating_history = get_user_rating(handle)
        if rating_history:
            print(f"\nRating History for {handle}:")
            for change in rating_history:
                print(json.dumps(change, indent=4))
                print("-" * 20)
        else:
            print(f"Could not retrieve rating history for {handle}")

    for handle in handles:
        contests = get_contests_participated_by_user(handle)
        if contests:
            print(f"Contests participated in by the user {handle}:\n", contests, "\n")
        else:
            print("Could not retrieve contest data.")
    
    common_contests = get_common_contests(handles)

    if common_contests:
        print(f"Common contests participated in by the users: " , handles, "\n", common_contests)
    else:
        print("No common contests found, or could not retrieve contest data for all users.")
    
    # Test the new get_user_all_stats function
    for handle in handles:
        print(f"\nGetting all statistics for {handle}...")
        all_stats = get_user_all_stats(handle)
        if all_stats:
            print(f"User: {all_stats.handle}")
            print(f"Rating: {all_stats.rating}")
            print(f"Rank: {all_stats.rank}")
            print(f"Contests participated: {all_stats.contests_count}")
            print(f"Problems solved: {all_stats.solved_problems_count}")
            print(f"Rating changes: {len(all_stats.rating_history) if all_stats.rating_history else 0}")
        else:
            print(f"Could not retrieve all statistics for {handle}")