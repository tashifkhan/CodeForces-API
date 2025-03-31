import requests
import json
import time
from typing import Dict, List, Optional, Any, Set
from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException, Query, Path
import uvicorn

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


app = FastAPI(
    title="Codeforces API",
    description="A FastAPI wrapper for the Codeforces API",
    version="1.0.0",
)

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint that provides basic API information."""
    return {"message": "Welcome to the Codeforces API wrapper. Visit /docs for documentation."}

@app.get("/{userid}", response_model=UserAllStats, responses={404: {"model": ErrorResponse}})
async def user_all_stats(userid: str = Path(..., description="Codeforces handle")):
    """
    Get comprehensive statistics for a Codeforces user.
    
    This includes profile info, contests participated, problems solved, and rating history.
    """
    stats = get_user_all_stats(userid)
    if stats is None:
        raise HTTPException(status_code=404, detail=f"Stats not found for {userid}")
    return stats

@app.get("/{userid}/basic", response_model=UserInfo, responses={404: {"model": ErrorResponse}})
async def user_basic_info(userid: str = Path(..., description="Codeforces handle")):
    """Get basic information about a Codeforces user."""
    user_info = get_user_info([userid])
    if not user_info:
        raise HTTPException(status_code=404, detail=f"User information not found for {userid}")
    return user_info[0]

@app.get("/multi/{userids}", response_model=List[UserInfo], responses={404: {"model": ErrorResponse}})
async def users_info(userids: str = Path(..., description="Semicolon-separated list of Codeforces handles")):
    """Get information about multiple Codeforces users."""
    handles_list = []
    if ';' in userids:
        handles_list = userids.split(';')
    elif ',' in userids:
        handles_list = userids.split(',')
    else:
        handles_list = [userids]
    
    # Clean up handles list to remove any empty strings
    handles_list = [h.strip() for h in handles_list if h.strip()]
    
    if not handles_list:
        raise HTTPException(status_code=400, detail="No valid handles provided")
    
    # Call get_user_info directly with the list of handles
    user_info = get_user_info(handles_list)
    
    if not user_info:
        raise HTTPException(status_code=404, detail=f"User information not found")
    
    return user_info

@app.get("/{userid}/rating", response_model=List[RatingHistory], responses={404: {"model": ErrorResponse}})
async def user_rating(userid: str = Path(..., description="Codeforces handle")):
    """Get rating history of a Codeforces user."""
    rating_history = get_user_rating(userid)
    if rating_history is None:
        raise HTTPException(status_code=404, detail=f"Rating history not found for {userid}")
    return rating_history

@app.get("/{userid}/solved", response_model=SolvedProblemsCount, responses={404: {"model": ErrorResponse}})
async def solved_problems(userid: str = Path(..., description="Codeforces handle")):
    """Get the number of solved problems for a Codeforces user."""
    solved_count = get_solved_problem_count(userid)
    if solved_count is None:
        raise HTTPException(status_code=404, detail=f"Solved problem count not found for {userid}")
    return {"handle": userid, "count": solved_count}

@app.get("/contests/upcoming", response_model=List[Contest], responses={404: {"model": ErrorResponse}})
async def upcoming_contests(gym: bool = False):
    """Get upcoming contests from Codeforces."""
    contests = get_upcoming_contests(gym)
    if contests is None:
        raise HTTPException(status_code=404, detail=f"Upcoming contests data not found")
    return contests

@app.get("/{userid}/contests", response_model=Dict[str, Any], responses={404: {"model": ErrorResponse}})
async def contests_participated(userid: str = Path(..., description="Codeforces handle")):
    """Get contests participated by a Codeforces user."""
    contests = get_contests_participated_by_user(userid)
    if not contests:
        raise HTTPException(status_code=404, detail=f"Contest participation data not found for {userid}")
    return {"handle": userid, "contests": list(contests)}

@app.get("/users/common-contests/{userids}", response_model=Dict[str, Any], responses={404: {"model": ErrorResponse}})
async def common_contests(userids: str = Path(..., description="Semicolon-separated list of Codeforces handles")):
    """Get common contests participated by multiple Codeforces users."""
    # Support both semicolon and comma as separators
    handles_list = []
    if ';' in userids:
        handles_list = userids.split(';')
    elif ',' in userids:
        handles_list = userids.split(',')
    else:
        handles_list = [userids]  # Single handle

    # Remove any empty strings from the list
    handles_list = [h.strip() for h in handles_list if h.strip()]
    
    if not handles_list:
        raise HTTPException(status_code=400, detail="No valid handles provided")

    common = get_common_contests(handles_list)
    if common is None:
        raise HTTPException(status_code=404, detail=f"Common contest data not found for {handles}")
    return {"handles": handles_list, "common_contests": list(common)}

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
        A set of contest IDs representing the contests participated in by all users,
        or None if there was a critical error fetching data.
    """
    if not handles:
        return set()  # No users, no contests

    all_users_contests = []
    
    for handle in handles:
        user_contests = get_contests_participated_by_user(handle)
        if user_contests is None:
            print(f"Could not retrieve contest data for {handle}. Skipping.")
            continue
        
        if not user_contests:  # If user has no contests
            print(f"User {handle} has no contest participation")
            # If any user has no contests, the intersection will be empty
            return set()
        
        all_users_contests.append(user_contests)
    
    if not all_users_contests:
        # If we couldn't retrieve contest data for any user
        return set()
    
    # Start with the first user's contests
    common_contests = all_users_contests[0]
    
    # Take intersection with each subsequent user's contests
    for user_contests in all_users_contests[1:]:
        common_contests = common_contests.intersection(user_contests)
    
    return common_contests

def get_user_all_stats(handle):
    """
    Gets comprehensive statistics for a Codeforces user including profile info,
    number of contests participated in, and number of problems solved.

    Args:
        handle: A Codeforces user handle.

    Returns:
        A UserAllStats object with all user statistics, or None if there was an error.
    """
    # Make sure handle is a string, not a list
    if isinstance(handle, list):
        # This function only works with a single handle
        # If a list is passed, we'll just use the first one
        if not handle:  # Empty list
            return None
        handle = handle[0]
        
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
    uvicorn.run("app:app", host="0.0.0.0", port=58353, reload=True)