from typing import Generic, TypeVar

from pydantic import BaseModel
from pydantic.generics import GenericModel

from .sauce import ArtSauce, BaseSauce, BooruSauce, MangaSauce, TwitterSauce, VideoSauce

GenericSauce = TypeVar(
    "GenericSauce", BaseSauce, ArtSauce, VideoSauce, BooruSauce, MangaSauce, TwitterSauce
)


class ResultIndex(BaseModel):
    """
    Custom index object to make
    storing and accessing indexes better.
    """

    id: int
    name: str

    def __str__(self):
        return self.name


class SauceResult(GenericModel, Generic[GenericSauce]):  # TODO: Add some data methods?
    """SauceNao result object, data field contains the source info."""

    data: GenericSauce
    similarity: float
    thumbnail: str
    index: ResultIndex
