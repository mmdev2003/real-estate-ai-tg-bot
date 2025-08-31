from abc import abstractmethod
from typing import Protocol


class IWewallTgBotClient(Protocol):

    @abstractmethod
    async def send_post_short_link(
            self,
            post_short_link_id: int,
            name: str,
            description: str,
            image_name: str,
            image_fid: str,
            file_name: str,
            file_fid: str,
    ) -> None: pass
