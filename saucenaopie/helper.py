from typing import Any, List, Optional, Sequence


class Helper:
    @classmethod
    def get_all_values(cls) -> List[Any]:
        """Get all available consts."""
        return [getattr(cls, name) for name in dir(cls) if name.isupper()]

    @classmethod
    def get_value_name(cls, value: int, human_readable: bool = False) -> Optional[str]:
        """
        Get a value name, mainly used to display a name to the user.

        :param value: Const value
        :param human_readable: Whether to make the name human-readable or leave it untouched
        :return:
        """
        for name in dir(cls):
            if not name.isupper():
                continue
            if getattr(cls, name) == value:
                if human_readable:
                    return "".join(word.capitalize() for word in name.split("_"))
                else:
                    return name


class SauceIndex(Helper):
    """Represents SauceNao database indexes."""

    H_MAGAZINES = 0
    H_GAME = 2
    DOUJINSHI_DB = 3
    PIXIV = 5
    PIXIV_HISTORICAL = 6
    SEIGA = 8
    DANBOORU = 9
    DRAWR = 10  # Site no longer functioning :(
    NIJIE = 11
    YANDERE = 12
    SHUTTERSTOCK = 15
    FAKKU = 16
    N_HENTAI = 18
    TWO_D_MARKET = 19
    MEDI_BANG = 20
    ANIME = 21
    H_ANIME = 22
    MOVIES = 23
    SHOWS = 24
    GELBOORU = 25
    KONACHAN = 26
    SANKAKU = 27
    ANIME_PICTURES = 28
    E621 = 29
    IDOL_COMPLEX = 30
    BCY_ILLUST = 31
    BCY_COSPLAY = 32
    PORTAL_GRAPHICS = 33  # Based on web archive
    DEVIANT_ART = 34
    PAWOO = 35
    MADOKAMI = 36
    MANGA_DEX = 37
    E_HENTAI = 38
    ART_STATION = 39
    FUR_AFFINITY = 40
    TWITTER = 41
    FURRY_NETWORK = 42
    ALL = 999

    @classmethod
    def get_booru_indexes(cls) -> Sequence[int]:
        """Returns booru source indexes."""
        return cls.DANBOORU, cls.YANDERE, cls.GELBOORU, cls.KONACHAN, cls.E621

    @classmethod
    def get_video_indexes(cls) -> Sequence[int]:
        """Returns anime/video source indexes."""
        return cls.ANIME, cls.H_ANIME, cls.MOVIES, cls.SHOWS

    @classmethod
    def get_manga_indexes(cls) -> Sequence[int]:
        """Returns all manga source indexes."""
        return (
            cls.H_MAGAZINES,
            cls.DOUJINSHI_DB,
            cls.FAKKU,
            cls.N_HENTAI,
            cls.MADOKAMI,
            cls.MANGA_DEX,
            cls.E_HENTAI,
        )

    @classmethod
    def get_art_indexes(cls) -> Sequence[int]:
        """Returns all art source indexes, like Pixiv and DeviantArt."""
        excluded = (
            cls.get_manga_indexes()
            + cls.get_booru_indexes()
            + cls.get_video_indexes()
            + (cls.TWITTER, cls.ALL)
        )
        return [value for value in cls.get_all_values() if value not in excluded]
