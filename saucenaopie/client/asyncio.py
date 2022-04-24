from pathlib import Path
from typing import BinaryIO, Optional, Union

import httpx

from ..helper import SauceIndex
from ..types.response import SauceResponse
from .base import BaseSauceClient, IndexType


class AsyncSauceNao(BaseSauceClient):
    def __init__(self, api_key: str, test_mode: bool = False, timeout: int = 30) -> None:
        super().__init__(api_key, test_mode, timeout)
        self._client = httpx.AsyncClient(
            base_url=self.base_url, timeout=self.timeout, params=self._default_params
        )

    async def close(self):
        await self._client.aclose()

    async def search(
        self,
        file: Union[str, Path, BinaryIO],
        *,
        index: IndexType = SauceIndex.ALL,
        max_index: Optional[IndexType] = None,
        min_index: Optional[IndexType] = None,
        result_limit: int = 8,
        from_url: bool = False,
    ) -> SauceResponse:
        payload = self._prepare_params(file, index, result_limit, max_index, min_index, from_url)

        if from_url:
            payload["url"] = file
            response = await self._client.post("search.php", params=payload)
        elif isinstance(file, (str, Path)):
            with open(file, "rb") as f:
                response = await self._client.post("search.php", data=payload, files={"file": f})
        else:
            response = await self._client.post("search.php", data=payload, files={"file": file})

        return self._process_response(response)
