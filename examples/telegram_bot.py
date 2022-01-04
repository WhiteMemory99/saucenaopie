"""This example uses aiogram 3.0"""

from aiogram import Bot, Dispatcher, html
from aiogram.types import Message

from saucenaopie import AsyncSauceNao
from saucenaopie.exceptions import ImageInvalid, LimitReached, SauceNaoError

BOT_TOKEN = "50:TOKEN"
SAUCENAO_API_KEY = "9201r9hhefh"

dp = Dispatcher()
sauce_nao = AsyncSauceNao(api_key=SAUCENAO_API_KEY)


@dp.message(commands="start")
async def start_handler(message: Message) -> None:
    await message.answer("Hey there!\nSend me a picture, and I'll tell you its source.")


@dp.message(content_types={"photo", "document"})
async def get_source(message: Message, bot: Bot) -> None:
    if message.photo:
        # Choose the biggest photo
        file_id = message.photo[-1].file_id
    else:
        file_id = message.document.file_id

    await bot.send_chat_action(message.from_user.id, "typing")
    bytes_io = await bot.download(file_id)
    try:
        sauce = await sauce_nao.search(bytes_io)
        results = sauce.get_likely_results()
        if results:
            await message.answer(
                "\n".join(
                    f"{html.link(r.index, r.data.first_url)}: {r.similarity:.1f}%" for r in results
                )
            )
        else:
            await message.answer("Couldn't find any sources of this picture.")
    except LimitReached as ex:
        if ex.long_remaining <= 0:
            await message.answer("Sorry, the bot has reached its daily search limit.")
        else:
            await message.answer(
                "Sorry, the bot has reached its short limit, try again in ~30 seconds."
            )
    except ImageInvalid:
        await message.answer("The image is bad, couldn't get its sources.")
    except SauceNaoError:
        await message.answer("Some unexpected error has occurred while processing this picture.")


def main() -> None:
    bot = Bot(BOT_TOKEN, parse_mode="HTML")
    dp.run_polling(bot)


if __name__ == "__main__":
    main()
