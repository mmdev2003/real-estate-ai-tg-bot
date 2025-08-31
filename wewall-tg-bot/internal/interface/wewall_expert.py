from abc import abstractmethod
from typing import Protocol

from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup

from internal import model


class IWewallExpertCallbackController(Protocol):
    @abstractmethod
    async def wewall_expert_callback(self, callback: CallbackQuery, user_state: model.State): pass


class IWewallExpertMessageService(Protocol):
    @abstractmethod
    async def handler(self, message: Message, state: model.State): pass


class IWewallExpertCallbackService(Protocol):
    @abstractmethod
    async def to_estate_search(self, callback: CallbackQuery, state: model.State): pass

    @abstractmethod
    async def to_estate_finance_model(self, callback: CallbackQuery, state: model.State): pass

    @abstractmethod
    async def to_estate_expert(self, callback: CallbackQuery, state: model.State): pass

    @abstractmethod
    async def to_manager(self, callback: CallbackQuery, state: model.State): pass

    @abstractmethod
    async def start(self, callback: CallbackQuery, state: model.State): pass


class IWewallExpertInlineKeyboardGenerator(Protocol):

    @abstractmethod
    async def start(self) -> InlineKeyboardMarkup: pass

    @abstractmethod
    async def check_subscribe(self) -> InlineKeyboardMarkup: pass
