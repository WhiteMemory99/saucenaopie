import io
from typing import Optional, Union

import httpx

from ..helper import SauceIndex
from ..types import SauceResponse
from .base import BaseSauceClient, IndexType


class SauceNao(BaseSauceClient):
    def __init__(self, api_key: str, test_mode: bool = False) -> None:
        super().__init__(api_key, test_mode)

    def search(
        self,
        file: Union[str, io.BytesIO],
        *,
        index: IndexType = SauceIndex.ALL,
        max_index: Optional[IndexType] = None,
        min_index: Optional[IndexType] = None,
        result_limit: int = 8,
        from_url: bool = False,
    ) -> SauceResponse:
        params = {"db": index, "numres": result_limit}
        if max_index is not None:
            params["dbmask"] = (2 ** max_index) if max_index > 0 else 1
        if min_index is not None:
            params["dbmaski"] = (2 ** (min_index - 1)) if max_index > 0 else 1

        if from_url and not isinstance(file, str):
            raise AttributeError(f"The file url must be str, not {type(file).__name__}")

        client: httpx.Client
        with httpx.Client(
            base_url=self.base_url, timeout=40, params=self._default_params
        ) as client:
            if from_url:
                params["url"] = file
                response = client.post("search.php", params=params)
            elif isinstance(file, io.BytesIO):
                response = client.post("search.php", params=params, files={"file": file})
            else:
                with open(file, "rb") as f:
                    response = client.post("search.php", params=params, files={"file": f})

        return self._process_response(response)
