from .repository import UserRepository
from .models import user_dict
import aiohttp
from tortoise.queryset import (
    QuerySetSingle, )
from typing import (Optional, TypeVar, TYPE_CHECKING)

if TYPE_CHECKING:  # pragma: nocoverage
    from tortoise.models import Model

MODEL = TypeVar("MODEL", bound="Model")


async def user_login(username, token,
                     access_token) -> QuerySetSingle[Optional[MODEL]]:
    filter_kw = {"username": username}
    exclude_kw = {}
    try:
        newUserRepository = UserRepository()
        is_exists = await newUserRepository.exists(filter_kw=filter_kw,
                                                   exclude_kw=exclude_kw)
        if not is_exists:
            user_info = await get_target_user(username, token)
            res = await newUserRepository.create(filter_kw=filter_kw,
                                                 create_kw=user_info)
            return res
        user = await newUserRepository.query(filter_kw=filter_kw,
                                             exclude_kw=exclude_kw)
        return user
    except Exception as e:
        print(e)
        return None


# TODO return user information from iris server through aiohttp request
async def get_target_user(username, token):
    async with aiohttp.ClientSession as session:
        async with session.get('http://localhost:8080/user',
                               params={'access_token': token}) as resp:
            user_info = user_dict()
            print('======> user_info: %s' % user_info)
            print('======> debug: get_target_user', resp.status)