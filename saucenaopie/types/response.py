from typing import Iterable, List, Type, Union

from pydantic import BaseModel, validator

from ..helper import SauceIndex
from .account import AccountInfo
from .result import GenericSauce, SauceResult

_IndexType = Union[SauceIndex, int]


class Header(BaseModel):
    """
    SauceNao response header, containing info like the
    minimum relevant similarity for request results etc.
    """

    results_requested: int
    search_depth: int
    min_similarity: int
    results_returned: int


class SauceResponse(BaseModel):
    """Basic object containing a customized SauceNao response."""

    header: Header
    account_info: AccountInfo
    results: List[SauceResult]

    @validator("results")
    def _sort_results(cls, v: List[SauceResult]) -> List[SauceResult]:
        return sorted(v, key=lambda r: r.similarity, reverse=True)

    def get_likely_results(self, must_have_url: bool = False) -> List[SauceResult]:
        """
        Returns all the results that are above
        the minimum similarity number for this request.

        :param must_have_url: Only return results that have at least one URL
        """
        if must_have_url:
            return [
                result
                for result in self.results
                if result.data.first_url and result.similarity >= self.header.min_similarity
            ]

        return [
            result for result in self.results if result.similarity >= self.header.min_similarity
        ]

    def get_all_source_urls(self, above_min_similarity: bool = True) -> List[str]:
        """
        Quickly returns all the source URLs that are present.

        :param above_min_similarity: Only include URLs of results that are above the min similarity
        """
        urls = []
        for result in self.results:
            if above_min_similarity and result.similarity < self.header.min_similarity:
                continue
            urls += result.data.urls

        return urls

    def filter_results_by_type(
        self, result_type: Type[GenericSauce], above_min_similarity: bool = True
    ) -> List[SauceResult[GenericSauce]]:
        """
        Get all results of the specified type from the results list.

        :param result_type: Type of sauce that is required
        :param above_min_similarity: Only include results that are above the min similarity
        :return:
        """
        required_results: List[SauceResult[result_type]] = []
        for result in self.results:
            if isinstance(result.data, result_type):
                if above_min_similarity and result.similarity < self.header.min_similarity:
                    continue
                required_results.append(result)

        return required_results

    def filter_results_by_index(
        self,
        index: Union[Iterable[_IndexType], _IndexType],
        above_min_similarity: bool = True,
    ) -> List[SauceResult]:
        """
        Get all results of the specified index(es) from the results list.

        :param index: Sauce index, can pass many as iterable.
        :param above_min_similarity: Only include results that are above the min similarity
        :return:
        """
        if isinstance(index, int):
            index = (index,)

        required_results: List[SauceResult] = []
        for result in self.results:
            if result.index.id in index:
                if above_min_similarity and result.similarity < self.header.min_similarity:
                    continue
                required_results.append(result)

        return required_results
