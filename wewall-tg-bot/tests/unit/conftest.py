import sys
from pathlib import Path

import pytest
from unittest.mock import AsyncMock, MagicMock, ANY
from aiogram import Bot, Dispatcher

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from internal import interface, model


@pytest.fixture
def mock_tel():
    tel = AsyncMock(spec=interface.ITelemetry)
    tel.tracer.return_value = MagicMock()
    tel.meter.return_value = MagicMock()
    tel.logger.return_value = MagicMock()

    mock_span = MagicMock()
    mock_cm = MagicMock()
    mock_cm.__enter__.return_value = mock_span
    mock_cm.__exit__.return_value = None
    tel.tracer.start_as_current_span.return_value = mock_cm

    tel.meter().create_counter.return_value = MagicMock()
    tel.meter().create_histogram.return_value = MagicMock()
    tel.meter().create_up_down_counter.return_value = MagicMock()

    return tel


@pytest.fixture
def mock_bot():
    bot = AsyncMock(spec=Bot)
    bot.get_chat_member.return_value = MagicMock(status='member')
    return bot



@pytest.fixture
def mocks(mock_tel, mock_bot):
    return {
        "bot": mock_bot,
        "tel": mock_tel,
        "dp": Dispatcher(),
        "db": AsyncMock(spec=interface.IDB),
        'estate_expert_client': AsyncMock(spec=interface.IWewallEstateExpertClient),
        'chat_client': AsyncMock(spec=interface.IWewallChatClient),
        'wewall_expert_inline_keyboard_generator': AsyncMock(spec=interface.IWewallExpertInlineKeyboardGenerator),
        'state_service': AsyncMock(spec=interface.IStateService),
        'estate_search_callback_service': AsyncMock(spec=interface.IEstateSearchCallbackService),
        'amocrm_manager_message_service': AsyncMock(spec=interface.IAmoCrmManagerMessageService),
        'wewall_expert_message_service': AsyncMock(spec=interface.IWewallExpertMessageService),
        'wewall_expert_callback_service': AsyncMock(spec=interface.IWewallExpertCallbackService),
        'estate_expert_message_service': AsyncMock(spec=interface.IEstateExpertMessageService),
        'estate_search_message_service': AsyncMock(spec=interface.IEstateSearchMessageService),
        'estate_finance_model_message_service': AsyncMock(spec=interface.IEstateFinanceModelMessageService),
        'contact_collector_message_service': AsyncMock(spec=interface.IContactCollectorMessageService),
        "state_repo": AsyncMock(spec=interface.IStateRepo),
        "estate_calculator_client": AsyncMock(spec=interface.IWewallEstateCalculatorClient),
        "estate_search_state_repo": AsyncMock(spec=interface.IEstateSearchStateRepo),
        "estate_search_client": AsyncMock(spec=interface.IWewallEstateSearchClient),
        "estate_search_inline_keyboard_generator": AsyncMock(spec=interface.IEstateSearchInlineKeyboardGenerator),
        "llm_client": AsyncMock(spec=interface.ILLMClient),
    }
