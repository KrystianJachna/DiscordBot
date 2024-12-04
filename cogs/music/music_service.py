import asyncio
import logging
from abc import ABC, abstractmethod

from discord import VoiceClient
from discord.ext import commands

from .music_downlaoder import MusicDownloader, Song


class MusicManager(ABC):
    class EndOfPlaylistException(Exception):
        def __init__(self):
            super().__init__("End of playlist reached.")

    @abstractmethod
    async def next(self) -> Song:
        pass


class MusicPlayer:
    """
    Class to play the songs in the queue

    :param music_manager: The music manager
    :param voice_client: The voice client (think of it as the voice channel)
    """

    def __init__(self, music_manager: MusicManager, voice_client: VoiceClient):
        self._is_playing = False
        self.music_manager = music_manager
        self.voice_client = voice_client
        self._singing: asyncio.Condition = asyncio.Condition()
        self.event_loop = asyncio.get_event_loop()

    async def play_loop(self) -> None:
        """
        Play the songs in the queue

        Try to play the next song in the queue until the end of the playlist is reached
        :return: None
        """
        self._is_playing = True
        while True:
            try:
                song = await self.music_manager.next()
            except MusicManager.EndOfPlaylistException:
                break
            async with self._singing:
                self.voice_client.play(
                    song.source,
                    after=lambda _: asyncio.run_coroutine_threadsafe(
                        self._notify_singing(), self.event_loop
                    )
                )
                await self._singing.wait()
        self._is_playing = False

    async def _notify_singing(self) -> None:
        """
        Notify the player that the song has finished playing

        :return: None
        """
        async with self._singing:
            self._singing.notify_all()

    @property
    def is_playing(self) -> bool:
        """
        Check if the player is currently playing a song

        :return: True if the player is playing a song, False otherwise
        """
        return self._is_playing


class MusicQueue(MusicManager):
    """
    Class to manage the music queue, and download the songs

    :param downloading_queue: The queue of songs to download
    :param currently_downloading: If any song is currently downloading
    :param music_queue: The queue of songs to play
    :param music_downloader: The music downloader
    """

    def __init__(self) -> None:
        self.downloading_queue: list[str] = []
        self.currently_downloading = False
        self.music_queue: asyncio.Queue[Song] = asyncio.Queue()
        self.music_downloader = MusicDownloader()

    async def add(self, query: str, ctx: commands.Context) -> None:
        """
        Add a song to the queue, and start downloading it if there are no songs currently downloading

        :param query: url or search query
        :param ctx: The discord context
        :return: None
        """
        self.downloading_queue.append(query)
        if not self.currently_downloading:
            await self._process_queue(ctx)

    async def _process_queue(self, ctx: commands.Context) -> None:
        """
        Process the downloading queue

        This method will download the songs in the queue if there are any
        url/query waiting to be downloaded

        :param ctx: The discord context
        :return: None
        """
        while self.downloading_queue:
            self.currently_downloading = True
            query = self.downloading_queue.pop(0)
            try:
                song = await self.music_downloader.download(query)
            except Exception as e:
                await ctx.send(f"An error occurred while downloading the song: {query}")
                logging.error(e)
                continue
            await self.music_queue.put(song)
            await ctx.send(f"Added `{song.title}` to the queue.")
            await ctx.send(f"{song.url}")
        self.currently_downloading = False

    async def next(self) -> Song:
        """
        Get the next song from the queue

        :return: The next song
        """
        if self.music_queue.empty() and not self.currently_downloading:
            raise MusicManager.EndOfPlaylistException
        return await self.music_queue.get()
