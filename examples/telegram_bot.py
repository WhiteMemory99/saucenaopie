"""This example uses aiogram 2.14.3"""

from io import BytesIO

from aiogram import Bot, Dispatcher, types, executor
from saucenaopie import AsyncSauceNao
from saucenaopie.exceptions import SauceNaoError, LimitReached, ImageInvalid

bot = Bot(token="bot_token", parse_mode="HTML")
dp = Dispatcher(bot)
sauce_nao = AsyncSauceNao(api_key="saucenao_key")


@dp.message_handler(commands="start")
async def start_handler(message: types.Message) -> None:
    await message.answer(f"Hey there!\nSend me a picture, and I'll tell you its source.")


@dp.message_handler(content_types="photo")
async def get_source(message: types.Message) -> None:
    bytes_io = await message.photo[-1].download(destination=BytesIO())
    try:
        sauce = await sauce_nao.search(bytes_io)
        results = sauce.get_likely_results()
        if results:
            await message.answer(
                "\n".join(f"<a href='{result.data.first_url}'>{result.index}</a>: {result.similarity:.1f}%" for result in results)
            )
        else:
            await message.answer("Couldn't find any sources of this picture.")
    except LimitReached as ex:
        if ex.long_remaining <= 0:
            await message.answer("Sorry, the bot has reached its daily search limit.")
        else:
            await message.answer("Sorry, the bot has reached its 30 second limit, try again in ~30 seconds.")
    except ImageInvalid:
        await message.answer("The image is bad, couldn't get its sources.")
    except SauceNaoError:
        await message.answer("Some unexpected error has occurred while processing this picture.")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
