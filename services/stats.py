from collections import Counter
from services.client import api


def solved_problems(submissions):
    return {(s['problem'].get('contestId'), s['problem'].get('index')): s['problem']
            for s in submissions if s.get('verdict') == 'OK' and s.get('problem')}


async def get_solved_problem_count(handle):
    return len(solved_problems(await api('user.status', handle=handle)))


async def get_solved_tags(handle):
    counts = Counter(tag for p in solved_problems(await api('user.status', handle=handle)).values() for tag in set(p.get('tags', [])))
    return [{'topic': tag, 'count': count} for tag, count in sorted(counts.items(), key=lambda x: (-x[1], x[0]))]
