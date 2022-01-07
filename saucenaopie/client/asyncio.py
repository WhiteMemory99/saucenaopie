from typing import BinaryIO, Optional, Union

import httpx

from ..helper import SauceIndex
from ..types.response import SauceResponse
from .base import BaseSauceClient, IndexType


class AsyncSauceNao(BaseSauceClient):
    async def search(
        self,
        file: Union[str, BinaryIO],
        *,
        index: IndexType = SauceIndex.ALL,
        max_index: Optional[IndexType] = None,
        min_index: Optional[IndexType] = None,
        result_limit: int = 8,
        from_url: bool = False,
    ) -> SauceResponse:
        payload = self._prepare_params(file, index, result_limit, max_index, min_index, from_url)

        client: httpx.AsyncClient
        async with httpx.AsyncClient(
            base_url=self.base_url, timeout=self.timeout, params=self._default_params
        ) as client:
            if from_url:
                payload["url"] = file
                response = await client.post("search.php", params=payload)
            elif isinstance(file, str):
                with open(file, "rb") as f:
                    response = await client.post("search.php", data=payload, files={"file": f})
            else:
                response = await client.post("search.php", data=payload, files={"file": file})

        return self._process_response(response)
