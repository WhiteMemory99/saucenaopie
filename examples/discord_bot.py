"""This example uses discord.py 2.0 beta."""

from typing import Optional

from discord import Color, Embed, Intents
from discord.ext import commands
from discord.ext.commands import Context

from saucenaopie import AsyncSauceNao
from saucenaopie.exceptions import ImageInvalid, LongLimitReached, SauceNaoError, ShortLimitReached
from saucenaopie.types.response import SauceResponse

BOT_TOKEN = "50:TOKEN"
SAUCENAO_API_KEY = "9201r9hhefh"

intents = Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
sauce_nao = AsyncSauceNao(api_key=SAUCENAO_API_KEY)


async def search_saucenao(ctx: Context, image_url: str) -> Optional[SauceResponse]:
    """Send a search request to the SauceNao API and handle possible errors."""
    try:
        return await sauce_nao.search(image_url, from_url=True)
    except LongLimitReached:
        await ctx.reply("Your SauceNao profile reached its daily limit of **200 searches**.")
    except ShortLimitReached:
        await ctx.reply(
            "Your SauceNao profile reached its short limit, try again in a few seconds."
        )
    except ImageInvalid:
        await ctx.reply("The image is bad, couldn't get its sources.")
    except SauceNaoError:
        await ctx.reply("An unknown error occurred.")


@bot.command(name="sauce")
async def sauce_command(ctx: Context):
    if ctx.message.reference and ctx.message.reference.resolved:
        # The message is a reference to another message, so we use that message.
        message = ctx.message.reference.resolved
    else:
        # The message is not a reference, so we use the message itself.
        message = ctx.message

    if not message.attachments or "image" not in message.attachments[0].content_type:
        return await ctx.reply("You need to attach an image to this command.")

    file_url = message.attachments[0].url  # TODO: Support all the attachments.
    sauce = await search_saucenao(ctx, file_url)
    if sauce is None:
        return  # An error occurred

    results = sauce.get_likely_results(must_have_url=True)
    if not results:
        return await ctx.reply("Couldn't find any valid results on this image.")

    embed = Embed(
        title="SauceNao search", description="Here's what I found..", color=Color.random()
    )
    embed.set_footer(text=f"Requested by {ctx.author.name}", icon_url=ctx.author.avatar)
    embed.set_thumbnail(url=file_url)

    for result in results[:4]:  # Soft limit results to avoid too much text.
        embed.add_field(
            name=f"{result.index} - {result.similarity:.1f}%",
            value=result.data.first_url,
            inline=False,
        )

    await ctx.reply(embed=embed)


if __name__ == "__main__":
    bot.run(BOT_TOKEN)
