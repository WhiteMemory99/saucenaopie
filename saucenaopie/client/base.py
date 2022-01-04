import logging
from abc import ABC, abstractmethod
from typing import BinaryIO, Dict, List, Optional, Union

import httpx
from pydantic import ValidationError

from ..exceptions import (
    AccountBanned,
    BadAPIKey,
    FileIsTooLarge,
    ImageInvalid,
    LongLimitReached,
    ShortLimitReached,
    TooManyFailedRequests,
    UnknownClientError,
    UnknownServerError,
)
from ..helper import AccountType, Helper, SauceIndex
from ..types.response import AccountInfo, Header, SauceResponse
from ..types.result import ResultIndex, SauceResult
from ..types.sauce import ArtSauce, BooruSauce, MangaSauce, TwitterSauce, VideoSauce

log = logging.getLogger(__name__)


class _OutputType(Helper):
    HTML = 0
    XML = 1  # Not yet supported by SauceNao
    JSON = 2


IndexType = Union[SauceIndex, int]


class BaseSauceClient(ABC):
    def __init__(self, api_key: str, test_mode: bool = False) -> None:
        """
        :param api_key: SauceNao API key (https://saucenao.com/user.php)
        :param test_mode: Makes the API return at least 1 result to (almost) every search
         query for testing purposes
        """
        self.base_url = "https://saucenao.com"
        self._default_params = {
            "api_key": api_key,
            "output_type": _OutputType.JSON,
        }
        if test_mode:
            self._default_params["testmode"] = 1

    @abstractmethod
    def search(
        self,
        file: Union[str, BinaryIO],
        *,
        index: IndexType = SauceIndex.ALL,
        max_index: Optional[IndexType] = None,
        min_index: Optional[IndexType] = None,
        result_limit: int = 8,
        from_url: bool = False,
    ) -> SauceResponse:
        """
        Perform a search with SauceNao. You can provide a file path,
        BytesIO or URL (along with the from_url argument).

        :param file: File path / BytesIO / URL (with from_url=True)
        :param index: SauceNao database index to search in,
         look at :class:`saucenaopie.helper.DBIndex`
        :param max_index: Search all the indexes that are less or equal to the specified one
        :param min_index: Search all the indexes that are greater or equal to the specified one
        :param result_limit: Limit the number of results, 8 is the API default.
        :param from_url: Set True if the file is a URL
        :return: Returns SauceResponse object on success
        """
        pass

    @staticmethod
    def _prepare_params(
        file: Union[str, BinaryIO],
        index: IndexType,
        result_limit: int,
        max_index: Optional[IndexType],
        min_index: Optional[IndexType],
        from_url: bool,
    ) -> Dict[str, Union[str, int]]:
        params = {"db": index, "numres": result_limit}
        if max_index is not None:
            params["dbmask"] = (2 ** max_index) if max_index > 0 else 1
        if min_index is not None:
            params["dbmaski"] = (2 ** (min_index - 1)) if max_index > 0 else 1

        if from_url and not isinstance(file, str):
            raise AttributeError(f"The file url must be str, not {type(file).__name__}")

        return params

    def _process_response(self, response: httpx.Response) -> SauceResponse:
        try:
            response.raise_for_status()
            return self._parse_response_data(response.json())
        except httpx.HTTPStatusError as error:
            if error.response.status_code == 403:
                raise BadAPIKey("The API key is invalid.")
            elif error.response.status_code == 413:
                raise FileIsTooLarge("The file is too large.")
            elif error.response.status_code == 429:
                header = response.json()["header"]
                if header.get("status") == -2:
                    raise TooManyFailedRequests(header.get("message"))

                if "Daily" in header["message"]:
                    raise LongLimitReached(
                        "Daily limit reached.",
                        long_remaining=header["long_remaining"],
                        short_remaining=header["short_remaining"],
                        long_limit=header["long_limit"],
                        short_limit=header["short_limit"],
                    )
                raise ShortLimitReached(
                    "30 second limit reached.",
                    long_remaining=header["long_remaining"],
                    short_remaining=header["short_remaining"],
                    long_limit=header["long_limit"],
                    short_limit=header["short_limit"],
                )

            raise UnknownServerError(
                "Server returned unknown error.", status_code=error.response.status_code
            )

    def _parse_response_data(self, data: dict) -> SauceResponse:
        log.debug(f"SauceNao Response: {data}")
        header = data["header"]
        if header["status"] < 0:  # Client side error
            if header["status"] == -1:
                raise AccountBanned(header["message"])
            if header["status"] in (-3, -4, -6):
                raise ImageInvalid(header["message"])

            raise UnknownClientError(header.get("message"))
        if header["status"] > 0:  # Server side error
            raise UnknownServerError(header.get("message"))

        processed_results: List[SauceResult] = []
        if data["results"]:
            for result in data["results"]:
                try:
                    processed_results.append(self._result_to_object(result))
                except ValidationError as ex:
                    log.exception(ex)

        return SauceResponse(
            account_info=AccountInfo(
                user_id=header["user_id"],
                short_limit=header["short_limit"],
                long_limit=header["long_limit"],
                long_remaining=header["long_remaining"],
                short_remaining=header["short_remaining"],
                account_type=AccountType.get_value_name(int(header["account_type"])).lower(),
            ),
            header=Header(
                results_requested=header["results_requested"],
                search_depth=header["search_depth"],
                min_similarity=header["minimum_similarity"],
                results_returned=header["results_returned"],
            ),
            results=processed_results,
        )

    def _result_to_object(self, result: dict) -> SauceResult:
        header: dict = result["header"]
        data: dict = result["data"]

        title = self._get_title(data)
        urls = data.get("ext_urls", [])
        if header["index_id"] in SauceIndex.get_video_indexes():
            sauce = VideoSauce(
                urls=urls,
                title=title,
                episode=data.get("part"),
                year=data.get("year"),
                timestamp=data.get("est_time"),
            )
        elif header["index_id"] in SauceIndex.get_manga_indexes():
            sauce = MangaSauce(
                urls=urls,
                title=title,
                chapter=data.get("part"),
                author=self._get_author(data),
            )
        elif header["index_id"] in SauceIndex.get_booru_indexes():
            sauce = BooruSauce(
                urls=urls,
                title=title,
                gelbooru_id=data.get("gelbooru_id"),
                danbooru_id=data.get("danbooru_id"),
                characters=data.get("character"),
                material=data.get("material"),
                source_url=data.get("source"),
            )
        elif header["index_id"] == SauceIndex.TWITTER:
            sauce = TwitterSauce(
                urls=urls,
                title=title,
                tweet_id=data["tweet_id"],
                user_id=data["twitter_user_id"],
                username=data["twitter_user_handle"],
            )
        else:
            author_id = data.get("member_id")
            if header["index_id"] in {SauceIndex.PIXIV, SauceIndex.PIXIV_HISTORICAL}:
                author_url = f"https://www.pixiv.net/users/{author_id}"
            elif header["index_id"] == SauceIndex.NIJIE:
                author_url = f"https://sp.nijie.info/members.php?id={author_id}"
            elif header["index_id"] == SauceIndex.MEDI_BANG:
                author_url = f"https://medibang.com/author/{author_id}"
            elif header["index_id"] in {SauceIndex.BCY_ILLUST, SauceIndex.BCY_COSPLAY}:
                author_url = f"https://bcy.net/u/{author_id}"
            elif header["index_id"] == SauceIndex.PORTAL_GRAPHICS:
                author_url = f"https://web.archive.org/web/http://www.portalgraphics.net/pg/profile/?user_id={author_id}"  # noqa
            elif header["index_id"] == SauceIndex.PAWOO:
                author_url = urls[0]
            else:
                author_url = data.get("author_url")

            sauce = ArtSauce(
                urls=urls,
                title=title,
                author=self._get_author(data),
                author_url=author_url,
            )

        return SauceResult[type(sauce)](
            similarity=header["similarity"],
            thumbnail=header["thumbnail"],
            data=sauce,
            index=ResultIndex(
                id=header["index_id"],
                name=SauceIndex.get_value_name(header["index_id"], human_readable=True),
            ),
        )

    @staticmethod
    def _get_title(result_data: dict) -> Optional[str]:
        keys = ("title", "eng_name", "material", "source")
        for key in keys:
            if value := result_data.get(key):
                if key == "source" and value.startswith("http"):
                    continue
                return value

    @staticmethod
    def _get_author(result_data: dict) -> Optional[str]:
        keys = (
            "author",
            "author_name",
            "member_name",
            "creator",
            "pawoo_user_display_name",
            "company",
        )
        for key in keys:
            if value := result_data.get(key):
                return value
