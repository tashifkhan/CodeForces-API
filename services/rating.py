from services.client import api


async def get_user_rating(handle):
    return await api('user.rating', handle=handle)
