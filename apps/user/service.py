from .repository import UserRepository
from .models import user_dict
import aiohttp
from tortoise.queryset import (
    QuerySetSingle, )
from typing import (Optional, TypeVar, TYPE_CHECKING)

if TYPE_CHECKING:  # pragma: nocoverage
    from tortoise.models import Model

MODEL = TypeVar("MODEL", bound="Model")


async def user_login(username=None,
                     password=None) -> QuerySetSingle[Optional[MODEL]]:
    res = await get_token(username, password)
    if not res:
        return None
    filter_kw = {"username": username}
    exclude_kw = {}
    try:
        newUserRepository = UserRepository()
        is_exists = await newUserRepository.exists(filter_kw=filter_kw,
                                                   exclude_kw=exclude_kw)
        if not is_exists:
            user_info = await get_user_info(res["authorizeToken"])
            user_info["authorize_token"] = res["authorizeToken"]
            return await newUserRepository.create(filter_kw=filter_kw,
                                                  create_kw=user_info)
        user = await newUserRepository.query(filter_kw=filter_kw,
                                       exclude_kw=exclude_kw)
        print("========>", user.__dict__)
        return user.__dict__
    except Exception as e:
        print(e)
        return None


async def get_user_info(authorizeToken):
    async with aiohttp.ClientSession() as session:
        async with session.get(
                'http://localhost:6180/v1/api/user',
                headers={'Authorization': f'Bearer {authorizeToken}'}) as resp:
            json_resp = await resp.json()
            user_info = user_dict(json_resp["data"])
            return user_info


async def get_token(username, password) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.post("http://localhost:6180/v1/api/user/authorize",
                                json={
                                    "username": username,
                                    "password": password
                                }) as response:
            if response.status == 200:
                res = await response.json()
                return res["data"]