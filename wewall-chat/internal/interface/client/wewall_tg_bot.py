from typing import Protocol
from abc import abstractmethod

class IWewallTgBotClient(Protocol):

    @abstractmethod
    async def send_message_to_user(self, tg_chat_id: int, text: str): pass

    @abstractmethod
    async def delete_state(self, tg_chat_id: int): pass