import asyncio
import pytest_asyncio
import sys
from typing import Any, AsyncGenerator, cast

import pytest
from unittest.mock import AsyncMock, MagicMock
from testcontainers.postgres import PostgresContainer

from aiogram import Bot, Dispatcher
from aiogram.types import Update, Message, User, Chat

from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

sys.path.append("/home/mm/Projects/wewall/wewall-tg-bot")
print(sys.path)

from internal import model, interface, common


@pytest.fixture(scope="session")
def mock_bot() -> Bot:
    bot = cast(Bot, MagicMock())
    bot.get_chat_member.return_value = MagicMock(status='member')
    return bot


@pytest.fixture(scope="session")
def mock_tel() -> interface.ITelemetry:
    from opentelemetry.trace import TracerProvider, SpanContext, TraceFlags
    from opentelemetry.sdk.trace import TracerProvider as SDKTracerProvider
    from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
    from opentelemetry.sdk.metrics import MeterProvider
    from unittest.mock import MagicMock

    tracer_provider = SDKTracerProvider()


    tel = cast(interface.ITelemetry, MagicMock())
    tel.tracer.return_value = tracer_provider.get_tracer("test")
    tel.meter.return_value = MeterProvider().get_meter("test")
    tel.logger.return_value = MagicMock()

    return tel


@pytest.fixture(scope="session")
def mocks(mock_tel: interface.ITelemetry, mock_bot: Bot) -> dict[str, Any]:
    return {
        "bot": mock_bot,
        "tel": mock_tel,  # Здесь уже правильный тип
        'estate_expert_client': cast(interface.IWewallEstateExpertClient, MagicMock()),
        'chat_client': cast(interface.IWewallChatClient, MagicMock()),
        "state_repo": cast(interface.IStateRepo, MagicMock()),
        "estate_calculator_client": cast(interface.IWewallEstateCalculatorClient, MagicMock()),
        "estate_search_client": cast(interface.IWewallEstateSearchClient, MagicMock()),
        "llm_client": cast(interface.ILLMClient, MagicMock()),
    }


@pytest_asyncio.fixture(scope="session")
async def pg_container() -> AsyncGenerator[PostgresContainer, None]:
    with PostgresContainer("postgres:16-alpine") as postgres:
        await asyncio.sleep(4)
        yield postgres


@pytest_asyncio.fixture(scope="session")
async def db(pg_container: PostgresContainer, mocks: dict[str, Any]) -> interface.IDB:
    from infrastructure.pg.pg import PG

    db = PG(
        tel=mocks['tel'],
        db_user="test",
        db_pass="test",
        db_host=pg_container.get_container_host_ip(),
        db_port=pg_container.get_exposed_port(5432),
        db_name='test'
    )
    await db.multi_query(model.create_queries)
    return db


@pytest_asyncio.fixture
async def clear_db(db: interface.IDB):
    await db.multi_query([
        "TRUNCATE TABLE states CASCADE",
        "TRUNCATE TABLE estate_search_state CASCADE",
    ])



@pytest.fixture
def telegram_request_body_factory():
    real_tg_user_id = 5667467611

    def create_message_request_body(text: str, user_id: int = real_tg_user_id, chat_id: int = real_tg_user_id):
        return {
            "update_id": 123456789,
            "message": {
                "message_id": 1,
                "from": {
                    "id": user_id,
                    "is_bot": False,
                    "first_name": "Test",
                },
                "chat": {
                    "id": chat_id,
                    "type": "private",
                    "first_name": "Test",
                    "username": "testuser"
                },
                "date": 1640995200,
                "text": text
            }
        }

    def create_callback_update(data: str, user_id: int = real_tg_user_id, chat_id: int = real_tg_user_id):
        return {
            "update_id": 123456790,
            "callback_query": {
                "id": "test_callback_123",
                "from": {
                    "id": user_id,
                    "is_bot": False,
                    "first_name": "Test",
                    "username": "testuser",
                    "language_code": "en"
                },
                "message": {
                    "message_id": 1,
                    "from": {
                        "id": 987654321,  # Bot ID
                        "is_bot": True,
                        "first_name": "TestBot",
                        "username": "testbot"
                    },
                    "chat": {
                        "id": chat_id,
                        "type": "private",
                        "first_name": "Test",
                        "username": "testuser"
                    },
                    "date": 1640995200,
                    "text": "Choose an option:"
                },
                "chat_instance": "-3541754756648",
                "data": data
            }
        }

    return {
        "message": create_message_request_body,
        "callback": create_callback_update
    }

@pytest_asyncio.fixture(scope="session")
async def deps(db: interface.IDB, mocks: dict[str, Any]) -> dict[str, Any]:
    from internal.controller.tg.middleware.middleware import TgMiddleware
    from internal.controller.http.middlerware.middleware import HttpMiddleware
    from internal.controller.http.webhook.handler import TelegramWebhookController

    from internal.service.state.service import StateService
    from internal.service.estate_expert.message_service import EstateExpertMessageService
    from internal.service.estate_search.message_service import EstateSearchMessageService
    from internal.service.wewall_expert.message_service import WewallExpertMessageService
    from internal.service.amocrm_manager.message_service import AmocrmManagerMessageService
    from internal.service.contact_collector.message_service import ContactCollectorMessageService
    from internal.service.estate_finance_model.message_service import EstateFinanceModelMessageService

    from internal.service.estate_search.callback_service import EstateSearchCallbackService
    from internal.service.wewall_expert.callback_service import WewallExpertCallbackService

    from internal.keyboard.estate_search.inline import EstateSearchInlineKeyboardGenerator
    from internal.keyboard.wewall_expert.inline import WewallExpertInlineKeyboardGenerator

    from internal.repo.state.repo import StateRepo
    from internal.repo.estate_search_state.repo import EstateSearchStateRepo

    amocrm_appeal_pipeline_id = 33333
    amocrm_main_pipeline_id = 55555
    wewall_tg_channel_login = "@bngotest"
    dp = Dispatcher()
    domain = "http://localhost:8000"

    estate_search_inline_keyboard_generator = EstateSearchInlineKeyboardGenerator()
    wewall_expert_inline_keyboard_generator = WewallExpertInlineKeyboardGenerator()

    state_repo = StateRepo(mocks['tel'], db)
    estate_search_state = EstateSearchStateRepo(mocks['tel'], db)

    state_service = StateService(mocks['tel'], state_repo)
    amocrm_manager_message_service = AmocrmManagerMessageService(
        mocks['tel'],
        state_repo,
        mocks['chat_client'],
        mocks['estate_expert_client'],
        wewall_expert_inline_keyboard_generator
    )
    estate_expert_message_service = EstateExpertMessageService(
        mocks['tel'],
        state_repo,
        mocks['estate_expert_client'],
        mocks['chat_client'],
        wewall_expert_inline_keyboard_generator,
        amocrm_appeal_pipeline_id,
    )
    estate_search_message_service = EstateSearchMessageService(
        mocks['tel'],
        state_repo,
        estate_search_state,
        mocks['chat_client'],
        mocks['estate_expert_client'],
        mocks['estate_search_client'],
        mocks['estate_calculator_client'],
        estate_search_inline_keyboard_generator,
        wewall_expert_inline_keyboard_generator,
        mocks['llm_client'],
        amocrm_main_pipeline_id,
        amocrm_appeal_pipeline_id,
    )
    wewall_expert_message_service = WewallExpertMessageService(
        mocks['tel'],
        state_repo,
        mocks['estate_expert_client'],
        mocks['chat_client'],
        wewall_expert_inline_keyboard_generator,
        amocrm_main_pipeline_id,
        amocrm_appeal_pipeline_id,
    )
    contact_collector_message_service = ContactCollectorMessageService(
        mocks['tel'],
        state_repo,
        mocks['estate_expert_client'],
        mocks['chat_client'],
        wewall_expert_inline_keyboard_generator,
        amocrm_appeal_pipeline_id
    )
    estate_finance_model_message_service = EstateFinanceModelMessageService(
        mocks['tel'],
        state_repo,
        mocks['estate_expert_client'],
        mocks['estate_calculator_client'],
        mocks['chat_client'],
        wewall_expert_inline_keyboard_generator,
        amocrm_main_pipeline_id,
        amocrm_appeal_pipeline_id
    )

    estate_search_callback_service = EstateSearchCallbackService(
        mocks['tel'],
        state_repo,
        estate_search_state,
        mocks['estate_expert_client'],
        mocks['estate_calculator_client'],
        estate_search_inline_keyboard_generator,
        mocks['chat_client'],
        mocks['llm_client']
    )
    wewall_expert_callback_service = WewallExpertCallbackService(
        mocks['tel'],
        state_repo,
        mocks['estate_expert_client'],
        mocks['chat_client'],
        amocrm_appeal_pipeline_id
    )
    tg_middleware = TgMiddleware(
        mocks['tel'],
        mocks['bot'],
        state_service,
        mocks['estate_expert_client'],
        mocks['chat_client'],
        wewall_expert_inline_keyboard_generator,
        wewall_tg_channel_login,
        amocrm_main_pipeline_id,
        amocrm_appeal_pipeline_id
    )
    http_middleware = HttpMiddleware(
        mocks['tel'],
        common.PREFIX,
    )
    tg_webhook_controller = TelegramWebhookController(
        mocks['tel'],
        dp,
        mocks['bot'],
        state_service,
        domain,
        common.PREFIX,
    )

    return {
        "state_service": state_service,
        "amocrm_manager_message_service": amocrm_manager_message_service,
        "estate_expert_message_service": estate_expert_message_service,
        "estate_search_message_service": estate_search_message_service,
        "wewall_expert_message_service": wewall_expert_message_service,
        "contact_collector_message_service": contact_collector_message_service,
        "estate_finance_model_message_service": estate_finance_model_message_service,
        "estate_search_callback_service": estate_search_callback_service,
        "wewall_expert_callback_service": wewall_expert_callback_service,
        "tg_middleware": tg_middleware,
        "http_middleware": http_middleware,
        "tg_webhook_controller": tg_webhook_controller,
        "dp": Dispatcher()
    }


@pytest.fixture(scope="session")
async def app(
        db: interface.IDB,
        mocks: dict[str, Any],
        deps: dict[str, Any]
) -> FastAPI:
    from internal.app.tg.app import NewTg
    _app = NewTg(
        tel=mocks['tel'],
        db=db,
        bot=mocks['bot'],
        dp=deps["dp"],
        http_middleware=deps['http_middleware'],
        tg_middleware=deps['tg_middleware'],
        tg_webhook_controller=deps["tg_webhook_controller"],
        state_service=deps["state_service"],
        amocrm_manager_message_service=deps["amocrm_manager_message_service"],
        wewall_expert_message_service=deps["wewall_expert_message_service"],
        estate_expert_message_service=deps["estate_expert_message_service"],
        estate_search_message_service=deps["estate_search_message_service"],
        estate_finance_model_message_service=deps["estate_finance_model_message_service"],
        contact_collector_message_service=deps["contact_collector_message_service"],
        estate_search_callback_service=deps["estate_search_callback_service"],
        wewall_expert_callback_service=deps["wewall_expert_callback_service"],
        estate_expert_client=mocks['estate_expert_client'],
        chat_client=mocks['chat_client'],
        amocrm_appeal_pipeline_id=33333
    )

    return _app


@pytest.fixture(scope="session")
async def async_client(app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url=f"http://testserver{common.PREFIX}"
    ) as client:
        yield client