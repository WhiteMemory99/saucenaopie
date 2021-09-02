from typing import List, Optional, Union
from pydantic import BaseModel, validator


class BaseSauce(BaseModel):
    """Base source object. You can use it for type checking."""

    urls: List[str]
    title: Optional[str]

    @property
    def first_url(self) -> Optional[str]:
        """Quickly get the first URL from the result URLs."""
        if self.urls:
            return self.urls[0]

    @validator("author", pre=True, check_fields=False)
    def _validate_author(cls, v: Union[List[str], str]) -> str:
        if isinstance(v, list):
            return v[0]
        return v


class MangaSauce(BaseSauce):
    """Manga sources."""

    chapter: Optional[str]
    author: Optional[str]


class BooruSauce(BaseSauce):
    """Booru related sources. Thanks to pysaucenao for this great idea."""

    danbooru_id: Optional[int]
    gelbooru_id: Optional[int]
    characters: List[str]
    material: List[str]
    source_url: Optional[str]

    @validator("characters", "material", pre=True)
    def _split_values(cls, v: str) -> List[str]:
        if v:
            return v.replace(", ", ",").split(",")
        return []


class TwitterSauce(BaseSauce):
    """Twitter source."""

    tweet_id: int
    user_id: int
    username: str

    @property
    def author_url(self) -> str:
        return f"https://twitter.com/i/user/{self.user_id}"


class VideoSauce(BaseSauce):
    """Video/Anime sources."""

    episode: Optional[str]
    year: str
    timestamp: str


class ArtSauce(BaseSauce):
    """Art sources, such as Pixiv and DeviantArt."""

    author: Optional[str]
    author_url: Optional[str]
