from fastapi import APIRouter, Path

from models.canonical import make_envelope
from services import canonical_mapper


router = APIRouter(tags=["Canonical"])


@router.get("/{userid}/topics")
async def get_topics(userid: str = Path(..., description="Codeforces handle")):
    stats = await canonical_mapper.build_stats(userid)
    return make_envelope(userid, stats.topicAnalysis)
