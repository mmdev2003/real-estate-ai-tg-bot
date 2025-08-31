from abc import abstractmethod
from typing import Protocol

from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup

from internal import model


class IEstateSearchCallbackController(Protocol):
    @abstractmethod
    async def estate_search_callback(self, callback: CallbackQuery, user_state: model.State): pass


class IEstateSearchStateRepo(Protocol):
    @abstractmethod
    async def create_estate_search_state(self, state_id: int, offers: list[model.SaleOffer | model.RentOffer],
                                         estate_search_params: dict) -> int:
        pass

    @abstractmethod
    async def change_current_offer_by_state_id(self, state_id: int, current_offer_id: int) -> None:
        pass

    @abstractmethod
    async def change_current_estate_by_state_id(self, state_id: int, current_estate_id: int) -> None: pass

    @abstractmethod
    async def estate_search_state_by_state_id(self, state_id: int) -> list[model.EstateSearchState]:
        pass

    @abstractmethod
    async def delete_estate_search_state_by_state_id(self, state_id: int) -> None:
        pass


class IEstateSearchMessageService(Protocol):
    @abstractmethod
    async def handler(self, message: Message, state: model.State): pass


class IEstateSearchCallbackService(Protocol):
    @abstractmethod
    async def like_offer(self, callback: CallbackQuery, state: model.State, offer_id: int): pass

    @abstractmethod
    async def next_offer(self, callback: CallbackQuery, state: model.State): pass

    @abstractmethod
    async def next_estate(self, callback: CallbackQuery, state: model.State): pass


class IEstateSearchInlineKeyboardGenerator(Protocol):

    @abstractmethod
    async def middle_offer(self, current_offer_id: int) -> InlineKeyboardMarkup: pass

    @abstractmethod
    async def last_estate(self, current_offer_id: int) -> InlineKeyboardMarkup: pass

    @abstractmethod
    async def last_offer(self, current_offer_id: int) -> InlineKeyboardMarkup: pass
