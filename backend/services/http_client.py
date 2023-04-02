from typing import Any

import aiohttp
from fake_useragent import UserAgent


async def get_async(url: str) -> dict[str, Any]:
    '''Makes an asynchronous GET request.'''

    headers = {'User-Agent': UserAgent().random}
    async with aiohttp.ClientSession() as client:
        async with client.get(url, headers=headers) as res:
            if res.status not in [200, 201]:
                await res.raise_for_status()
            else:
                return await res.json()
            

async def post_async(
    url: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    '''Makes an asynchronous POST request.'''

    headers = {'User-Agent': UserAgent().random}
    async with aiohttp.ClientSession() as client:
        async with client.post(url, headers=headers, json=payload) as res:
            if res.status not in [200, 201]:
                await res.raise_for_status()
            else:
                return await res.json()
