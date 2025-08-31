import io
from abc import abstractmethod
from typing import Protocol, Sequence, Any, Annotated, Callable, Awaitable

from aiogram.types import TelegramObject, Update, Message
from fastapi import FastAPI, Header
from opentelemetry.metrics import Meter
from opentelemetry.trace import Tracer

from internal.controller.http.webhook.model import *
from internal import model


class IMessageController(Protocol):
    @abstractmethod
    async def message_handler(self, message: Message, user_state: model.State): pass


class ICommandController(Protocol):
    @abstractmethod
    async def start_handler(self, message: Message): pass

    @abstractmethod
    async def estate_search_handler(self, message: Message, user_state: model.State): pass

    @abstractmethod
    async def finance_model_handler(self, message: Message, user_state: model.State): pass

    @abstractmethod
    async def news_handler(self, message: Message, user_state: model.State): pass

    @abstractmethod
    async def manager_handler(self, message: Message, user_state: model.State): pass


class IStatisticWorker(Protocol):
    @abstractmethod
    async def collect_daily_stats(self): pass

    @abstractmethod
    async def collect_monthly_stats(self): pass


class ITelegramMiddleware(Protocol):
    @abstractmethod
    async def trace_middleware01(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: dict[str, Any]
    ): pass

    @abstractmethod
    async def metric_middleware02(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: dict[str, Any]
    ): pass

    @abstractmethod
    async def logger_middleware03(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: dict[str, Any]
    ): pass

    @abstractmethod
    async def check_subscribe_middleware04(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: dict[str, Any]
    ): pass

    @abstractmethod
    async def get_state_middleware05(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: dict[str, Any]
    ): pass

    @abstractmethod
    async def count_message_middleware06(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: dict[str, Any]
    ): pass

    @abstractmethod
    async def send_contact_message_to_amocrm_middleware07(
            self,
            handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: dict[str, Any]
    ): pass


class ITelegramWebhookController(Protocol):
    @abstractmethod
    async def bot_webhook(
            self,
            update: dict,
            x_telegram_bot_api_secret_token: Annotated[str | None, Header()] = None
    ): pass

    @abstractmethod
    async def create_post_short_link(self, body: CreatePostShortLinkBody): pass

    @abstractmethod
    async def send_message_to_user(self, body: SendMessageWebhookBody): pass

    @abstractmethod
    async def delete_state(self, body: DeleteStateBody): pass

    @abstractmethod
    async def bot_set_webhook(self): pass


class IHttpMiddleware(Protocol):
    @abstractmethod
    def trace_middleware01(self, app: FastAPI): pass

    @abstractmethod
    def metrics_middleware02(self, app: FastAPI): pass

    @abstractmethod
    def logger_middleware03(self, app: FastAPI): pass


class IOtelLogger(Protocol):
    @abstractmethod
    def debug(self, message: str, fields: dict = None) -> None:
        pass

    @abstractmethod
    def info(self, message: str, fields: dict = None) -> None:
        pass

    @abstractmethod
    def warning(self, message: str, fields: dict = None) -> None:
        pass

    @abstractmethod
    def error(self, message: str, fields: dict = None) -> None:
        pass


class ITelemetry(Protocol):
    @abstractmethod
    def tracer(self) -> Tracer:
        pass

    @abstractmethod
    def meter(self) -> Meter:
        pass

    @abstractmethod
    def logger(self) -> IOtelLogger:
        pass


class IStorage(Protocol):
    @abstractmethod
    def delete(self, fid: str, name: str): pass

    @abstractmethod
    def download(self, fid: str, name: str) -> tuple[io.BytesIO, str]: pass

    @abstractmethod
    def upload(self, file: io.BytesIO, name: str): pass

    @abstractmethod
    def update(self, file: io.BytesIO, fid: str, name: str): pass


class IRedis(Protocol):
    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int = None) -> bool: pass

    @abstractmethod
    async def get(self, key: str, default: Any = None) -> Any: pass


class IDB(Protocol):
    @abstractmethod
    async def insert(self, query: str, query_params: dict) -> int: pass

    @abstractmethod
    async def delete(self, query: str, query_params: dict) -> None: pass

    @abstractmethod
    async def update(self, query: str, query_params: dict) -> None: pass

    @abstractmethod
    async def select(self, query: str, query_params: dict) -> Sequence[Any]: pass

    @abstractmethod
    async def multi_query(self, queries: list[str]) -> None: pass


class ILLMClient(Protocol):
    @abstractmethod
    async def generate(
            self,
            text: str,
            temperature: float,
            _model: str = "gpt-4o-mini"
    ) -> str: pass
