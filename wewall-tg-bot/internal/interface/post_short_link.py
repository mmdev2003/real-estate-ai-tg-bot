import io
from typing import Protocol
from abc import abstractmethod

from aiogram.types import BufferedInputFile, InlineKeyboardMarkup

from internal import model


class IPostShortLinkService(Protocol):
    @abstractmethod
    async def create_post_short_link(
            self,
            post_short_link_id: int,
            name: str,
            description: str,
            image_name: str,
            image_fid: str,
            file_name: str,
            file_fid: str
    ): pass

    @abstractmethod
    async def trigger(self, post_short_link_id: int) -> tuple[str, BufferedInputFile | None, BufferedInputFile | None, InlineKeyboardMarkup]: pass

class IPostShortLinkRepo(Protocol):

    @abstractmethod
    async def post_short_link_by_id(self, post_short_link_id: int) -> list[model.PostShortLink]: pass

    @abstractmethod
    async def create_post_short_link(
            self,
            post_short_link_id: int,
            name: str,
            description: str,
            image_name: str,
            image_fid: str,
            file_name: str,
            file_fid: str
    ): pass

    @abstractmethod
    async def delete_post_short_link(self, tg_chat_id: int): pass

class IPostShortLinkInlineKeyboardGenerator(Protocol):

    @abstractmethod
    async def start(self) -> InlineKeyboardMarkup: pass

