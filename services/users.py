import asyncio
from models.users import UserAllStats
from services.client import api
from services.stats import get_solved_problem_count, get_solved_tags, solved_problems
from services.rating import get_user_rating
from services.contests import get_upcoming_contests, get_contests_participated_by_user, get_common_contests
from services.heatmap import get_user_activity_heatmap, _build_heatmap_response


async def get_user_info(handles):
    return await api('user.info', handles=';'.join(handles))


async def get_user_all_stats(handle):
    if isinstance(handle, list):
        handle = handle[0] if handle else None
    if not handle:
        return None
    info, submissions, ratings = await asyncio.gather(
        get_user_info([handle]), api('user.status', handle=handle), get_user_rating(handle))
    return UserAllStats(**info[0], contests_count=len({s['contestId'] for s in submissions if 'contestId' in s}),
                        solved_problems_count=len(solved_problems(submissions)), rating_history=ratings)
