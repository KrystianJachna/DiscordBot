# music.py
import asyncio
import random
from random import random
from typing import Optional

from discord.ext import commands, tasks
from discord import VoiceChannel, VoiceClient
from .music.messages import *

from .music.music_service import MusicQueue, MusicPlayer


class MusicCog(commands.Cog):
    """
    Music commands for the bot

    :param bot: The bot instance
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.music_queue = MusicQueue()
        self.music_player: Optional[MusicPlayer] = None

    @commands.command(description="Play a song in the voice channel")
    async def play(self, ctx: commands.Context, *, arg: str) -> None:
        """
        Play a song in the voice channel

        :param ctx: The discord context
        :param arg: The song to play passed as a url or search query by the user
        :return:
        """
        await self.music_queue.add(arg, ctx)
        if not self.music_player.is_playing:
            await self.music_player.play_loop()


    @commands.command()
    async def skip(self, ctx: commands.Context) -> None:
        """
        Skip the current song

        :param ctx: The discord context
        :return: None
        """
        if not self.music_player.is_playing:
            await ctx.send(embed=skip_error())
            return
        await self.music_player.skip()
        await ctx.send(embed=skipped(self.music_queue.queue_length))

    @commands.command()
    async def stop(self, ctx: commands.Context) -> None:
        pass

    @commands.command()
    async def pause(self, ctx: commands.Context) -> None:
        ...

    @commands.command()
    async def resume(self, ctx: commands.Context) -> None:
        await self.music_player.resume()

    @commands.command()
    async def loop(self, ctx: commands.Context) -> None:
        ...

    @commands.command()
    async def join(self, ctx: commands.Context) -> None:
        ...

    @commands.command()
    async def queue(self, ctx: commands.Context) -> None:
        ...

    @commands.command()
    async def clear(self, ctx: commands.Context) -> None:
        ...

    @tasks.loop()
    async def check_listeners(self):
        ...

    @play.before_invoke
    async def ensure_voice(self, ctx):
        if ctx.voice_client is None:
            if ctx.author.voice:
                voice_client = await ctx.author.voice.channel.connect()
                self.music_player = MusicPlayer(self.music_queue, voice_client)
            else:
                await ctx.send("You are not connected to a voice channel.")
                raise commands.CommandError("Author not connected to a voice channel.")
