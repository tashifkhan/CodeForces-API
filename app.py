import requests
import json
import time

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
    Gets a list of contests that the given Codeforces users have participated in.

    Args:
        handles: A list of Codeforces user handles.

    Returns:
        A set of contest IDs representing the contests participated in by the users.
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