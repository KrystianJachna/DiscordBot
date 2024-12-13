# main.py

import asyncio
import logging
from sys import stderr

import discord
from discord.ext import commands

from cogs.music_cog import MusicCog
from utils import load_token, setup_logging
from messages import *

intents = discord.Intents.default()
intents.message_content = True

bot: commands.Bot = commands.Bot(
    command_prefix="!",
    description="Relatively simple music bot with some extra features for gaming",
    intents=intents,
    help_command=HelpMessage()
)


@bot.event
async def on_ready() -> None:
    """
    Print a message to the console when the bot is ready

    :return: None
    """
    message = f"Logged in as {bot.user} (ID: {bot.user.id})"
    logging.info(message)
    logging.info("-" * len(message))


@bot.event
async def on_command_error(ctx: commands.Context, error: Exception) -> None:
    """
    Send a message to the channel if a command is not found

    :param ctx: Discord context
    :param error: The error that occurred
    :return:    None
    """
    if isinstance(error, commands.CommandNotFound):
        await ctx.send(embed=command_not_found())
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(embed=missing_argument(error.param.name, ctx.command.name))
    else:
        logging.error(error)


async def main() -> None:
    """
    Main function to start the bot

    :return: None
    """
    try:
        TOKEN = load_token()
        setup_logging(logging.INFO)
        async with bot:
            await bot.add_cog(MusicCog(bot))
            await bot.start(TOKEN)
    except discord.LoginFailure:
        print("Failed to login to discord, please check the token and try again.", file=stderr)
    except Exception as e:
        print(f"An error occurred: {e}", file=stderr)


if __name__ == '__main__':
    asyncio.run(main())
