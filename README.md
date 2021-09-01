# SauceNaoPie

[![GitHub](https://img.shields.io/github/license/WhiteMemory99/saucenaopie)](https://github.com/WhiteMemory99/saucenaopie/blob/main/LICENSE)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/saucenaopie)](https://pypi.org/project/saucenaopie/)

Modern and easy-to-use Python implementation for the **SauceNao API**, with Pydantic and full asyncio support, inspired
by [PySauceNao](https://github.com/FujiMakoto/pysaucenao).

* [Installation](#installation)
* [Overview](#overview)
* [Writing your first code](#writing-your-first-code)
* [Advanced usage](#advanced-usage)
* [Error handling](#error-handling)

## Installation

**[Python 3.8](https://www.python.org)** or above is required.

```
$ pip install saucenaopie
```

## Overview

I think you all know that the SauceNao API leaves very much to be desired.  
Even so, I tried to make this wrapper as user-friendly as I could. As for benefits:

* Thanks to Pydantic and some serious work on type checking, you can get the fullest, safest and the most precise code
  completion possible in IDEs. The library is also well-documented.
* The SauceNao results have been divided into 5 types to make it easier to use - TwitterSauce, BooruSauce, VideoSauce,
  MangaSauce and ArtSauce. Each one has slightly different fields.
* Built-in methods to filter results as you see fit. More in [advanced usage](#advanced-usage).
* Results are sorted by similarity before they are given to you.
* Searching supports BytesIO objects, file paths and URLs.
* Almost every SauceNao error is handled and represented.
* The SauceNao DB indexes are fully represented in this library as a helpful object. Thanks to that, you can see, get,
  and use any SauceNao index with ease, and do stuff like getting the index name by its ID, getting indexes by a certain
  result type or all the available indexes altogether. Read more
  in [the sources](https://github.com/WhiteMemory99/saucenaopie/tree/main/saucenaopie/helper.py).

## Writing your first code

Both async and sync clients are equally supported and well-made.

<details>
  <summary>Sync client</summary>

```python
from saucenaopie import SauceNao


def main():
    client = SauceNao(api_key="api_key")
    sauce = client.search(  # Also, you can pass BytesIO or a file path
        "http://img10.joyreactor.cc/pics/post/full/iren-lovel-Anime-Art-artist-AO-6216329.jpeg",
        from_url=True
    )
    for result in sauce.results:
        print(result.data.first_url)  # Quickly get the first url from the result, can be None
        print(f"{result.index.name} - {result.similarity:.1f}%")


if __name__ == "__main__":
    main()
```

</details>
<details>
  <summary>Async client</summary>

```python
import asyncio
from saucenaopie import AsyncSauceNao


async def main():
    client = AsyncSauceNao(api_key="api_key")
    sauce = await client.search(  # Also, you can pass BytesIO or a file path
        "http://img10.joyreactor.cc/pics/post/full/iren-lovel-Anime-Art-artist-AO-6216329.jpeg",
        from_url=True
    )
    for result in sauce.results:
        print(result.data.first_url)  # Quickly get the first url from the result, can be None
        print(f"{result.index.name} - {result.similarity:.1f}%")


if __name__ == "__main__":
    asyncio.run(main())
```

</details>

To learn more, you can either scroll down to the advanced usage section or see
the [examples folder](https://github.com/WhiteMemory99/saucenaopie/tree/main/examples) to look at real-life examples.

## Advanced usage

Now let's pretend that we did a search.

```python
def main():
    client = SauceNao(api_key="api_key")
    sauce = await client.search("path_to_the_file")
```

If the search was successful, we get a SauceResponse object that contains 3 fields:

* `header` - information about the current query, such as the minimum result similarity and total number of results.
* `account_info` - information about your SauceNao account, like your current limits, account type and user_id.
* `results` - a list of results, each result has source data that can be one of 5 types, result similarity percent,
  index object and thumbnail.

Let's find out how we can filter our results to make the library give us some specific data. We'll look for Pixiv
results.

```python
from saucenaopie.helper import SauceIndex
from saucenaopie.types.sauce import ArtSauce  # just for reference

...
for result in sauce.filter_results_by_index(SauceIndex.PIXIV):
    # Every result 100% belongs to Pixiv (ArtSauce type)
    print(f"{result.data.first_url} - {result.similarity:.1f}%")

# And another way to do the same thing
for result in sauce.results:  # or sauce.filter_results_by_type(ArtSauce)
    if result.index.id == SauceIndex.PIXIV:
        print(f"Pixiv result: {result.data.first_url} - {result.similarity:.1f}%")
```

By default, saucenaopie sorts results by similarity, but it does not filter unlikely ones that have low similarity. To
learn the way to do that along with some bonuses, look at the example below.

```python
...
from saucenaopie.types.sauce import MangaSauce

...
for result in sauce.get_likely_results():  # Only results with good similarity
    print(f"{result.index} or {result.index.clean_name} is a human readable index title, like Pixiv.")
    if result.index.id in SauceIndex.get_manga_indexes():
        print("This result belongs to a manga source, like MangaDex.")
    if isinstance(result.data, MangaSauce):
        print("This result belongs to a manga source x2.")
```

At this point you should have a good idea on how you can filter the results.  
Next we'll discuss more complex searching queries.

```python
client.search(
    "path_to_the_file",
    result_limit=5,
    # You can limit results, 8 by default.
    # Just note that SauceNao DOES NOT 
    # sort the results by similarity before sending them to you.
    # In other words, you might get the worst possible garbage.
    index=SauceIndex.ALL,
    # We can provide a specific index to search from.
    # By default, all of them are in use.
    max_index=SauceIndex.YANDERE,  # NOTE: Broken by now
    # Yandere is 11th in the index list, this will EXCLUDE all the indexes that are higher.
    min_index=SauceIndex.DOUJINSHI_DB,  # NOTE: Broken by now
    # The same principle as above, just vice versa.
)
```

That's all. If you still have questions, you can browse the library source code or use your IDE capabilities.  
Don't forget to handle exceptions. By the way, this leads us to the last topic - **error handling**.

## Error handling

All the SauceNao exceptions are inherited from SauceNaoError, so you can use this whenever you just to catch everything.
For other exceptions,
see [this file](https://github.com/WhiteMemory99/saucenaopie/tree/main/saucenaopie/exceptions.py).  
You should also know that some exceptions contain additional helpful data:

```python
from saucenaopie import SauceNao
from saucenaopie.exceptions import LimitReached


def main():
    client = SauceNao(api_key="api_key")

    try:
        client.search("...")
    except LimitReached as ex:
        # Free account has 8 requests per 30 sec and 200 per 24 hours
        print(f"Daily requests left: {ex.long_remaining}.")
        print(f"30 second requests left: {ex.short_remaining}.")
```