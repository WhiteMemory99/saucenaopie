import io
import httpx
from typing import Optional, Union

from .base import BaseSauceClient, IndexType
from ..helper import SauceIndex
from ..types import SauceResponse


class AsyncSauceNao(BaseSauceClient):
    def __init__(self, api_key: str, test_mode: bool = False) -> None:
        super().__init__(api_key, test_mode)

    async def search(
        self, file: Union[str, io.BytesIO], *, index: IndexType = SauceIndex.ALL,
        max_index: Optional[IndexType] = None, min_index: Optional[IndexType] = None,
        result_limit: int = 8, from_url: bool = False
    ) -> SauceResponse:
        params = {"db": index, "numres": result_limit}
        if max_index is not None:  # Barely works, actually..
            params["dbmask"] = (2 ** max_index) if max_index > 0 else 1
        if min_index is not None:
            params["dbmaski"] = (2 ** (min_index - 1)) if max_index > 0 else 1

        if from_url and not isinstance(file, str):
            raise AttributeError(f"The file url must be str, not {type(file).__name__}")

        client: httpx.AsyncClient
        async with httpx.AsyncClient(base_url=self.base_url, timeout=40, params=self._default_params) as client:
            if from_url:
                params["url"] = file
                response = await client.post("search.php", params=params)
            elif isinstance(file, io.BytesIO):
                response = await client.post("search.php", data=params, files={"file": file})
            else:
                with open(file, "rb") as f:
                    response = await client.post(
                        "search.php", data=params, files={"file": f}
                    )

        return self._process_response(response)
