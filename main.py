# main.py

import asyncio
import logging
from sys import stderr

import discord
from discord.ext import commands

from music import Music
from utils import load_token

intents: discord.Intents = discord.Intents.default()
intents.message_content = True

bot: commands.Bot = commands.Bot(
    command_prefix="!",
    description="Relatively simple music bot with some extra features for gaming",
    intents=intents,
    log_level=logging.DEBUG  # TODO: change this to logging.INFO after testing
)


@bot.event
async def on_ready() -> None:
    """
    Print a message to the console when the bot is ready

    :return: None
    """
    message = f"Logged in as {bot.user} (ID: {bot.user.id})"
    print(message)
    print("-" * len(message))


@bot.event
async def on_command_error(ctx, error) -> None:
    """
    Send a message to the channel if a command is not found

    :param ctx: Discord context
    :param error: The error that occurred
    :return:    None
    """
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found.")
    else:
        raise error


async def main():
    try:
        TOKEN = load_token()
        async with bot:
            await bot.add_cog(Music(bot))
            await bot.start(TOKEN)
    except discord.LoginFailure:
        print("Failed to login to discord, please check the token and try again.", file=stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=stderr)


if __name__ == '__main__':
    asyncio.run(main())
