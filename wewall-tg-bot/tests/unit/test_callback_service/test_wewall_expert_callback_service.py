import pytest
from unittest.mock import MagicMock, call

from opentelemetry.trace import SpanKind
from aiogram.types import BufferedInputFile, InputMediaDocument

from internal import common
from internal.service.wewall_expert.callback_service import WewallExpertCallbackService
from tests.unit import utils


class TestWewallExpertCallbackService:

    @pytest.fixture
    def wewall_expert_callback_service(self, mocks):
        return WewallExpertCallbackService(
            tel=mocks["tel"],
            state_repo=mocks["state_repo"],
            chat_client=mocks["chat_client"],
            estate_expert_client=mocks["estate_expert_client"],
            wewall_expert_inline_keyboard_generator=mocks["wewall_expert_inline_keyboard_generator"],
            amocrm_appeal_pipeline_id=5353,
        )

    async def test_to_estate_search(
            self,
            wewall_expert_callback_service,
            mocks
    ):
        # Arrange
        state = utils.create_state(common.StateStatuses.wewall_expert)
        callback_query = utils.create_callback_query(
            common.WewallExpertKeyboardCallbackData.to_estate_search,
            "Подбор недвижимости"
        )

        llm_response = "Хорошо, помогу подобрать недвижимость" + common.StateSwitchCommand.to_estate_search_expert
        mocks["estate_expert_client"].send_message_to_estate_search_expert.return_value = llm_response

        # Act
        await wewall_expert_callback_service.to_estate_search(callback_query, state)

        # Assert
        mocks["estate_expert_client"].delete_all_message.assert_awaited_once_with(callback_query.message.chat.id)

        mocks["state_repo"].change_status.assert_awaited_once_with(state.id, common.StateStatuses.estate_search)

        callback_query.message.answer.assert_awaited_once_with(llm_response)

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            callback_query.message.chat.id,
            llm_response
        )

        tracer = wewall_expert_callback_service.tracer
        utils.assert_span(tracer, [
            {
                "name": "WewallExpertCallbackService.to_estate_search",
            }
        ])

    async def test_to_estate_search_err(
            self,
            wewall_expert_callback_service,
            mocks
    ):
        # Arrange
        state = utils.create_state(common.StateStatuses.wewall_expert)
        callback_query = utils.create_callback_query(
            common.WewallExpertKeyboardCallbackData.to_estate_search,
            "Подбор недвижимости"
        )

        err = Exception("Ошибка при to_estate_search")
        mocks["estate_expert_client"].delete_all_message.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка при to_estate_search"):
            await wewall_expert_callback_service.to_estate_search(callback_query, state)

        # Assert
        tracer = wewall_expert_callback_service.tracer
        utils.assert_span_error(tracer, err, 1)

    async def test_to_estate_finance_model(
            self,
            wewall_expert_callback_service,
            mocks
    ):
        # Arrange
        state = utils.create_state(common.StateStatuses.wewall_expert)
        callback_query = utils.create_callback_query(
            common.WewallExpertKeyboardCallbackData.to_estate_finance_model,
            "Оцени доходность"
        )

        llm_response = "Хорошо, оценю доходность" + common.StateSwitchCommand.to_estate_finance_model_expert
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.return_value = llm_response

        # Act
        await wewall_expert_callback_service.to_estate_finance_model(callback_query, state)

        # Assert
        mocks["estate_expert_client"].delete_all_message.assert_awaited_once_with(callback_query.message.chat.id)

        mocks["state_repo"].change_status.assert_awaited_once_with(state.id, common.StateStatuses.estate_finance_model)

        callback_query.message.answer.assert_awaited_once_with(llm_response)

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            callback_query.message.chat.id,
            llm_response
        )

        tracer = wewall_expert_callback_service.tracer
        utils.assert_span(tracer, [
            {
                "name": "WewallExpertCallbackService.to_estate_finance_model",
            }
        ])

    async def test_to_estate_finance_model_err(
            self,
            wewall_expert_callback_service,
            mocks
    ):
        # Arrange
        state = utils.create_state(common.StateStatuses.wewall_expert)
        callback_query = utils.create_callback_query(
            common.WewallExpertKeyboardCallbackData.to_estate_finance_model,
            "Оцени доходность"
        )

        err = Exception("Ошибка при to_estate_finance_model")
        mocks["estate_expert_client"].delete_all_message.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка при to_estate_finance_model"):
            await wewall_expert_callback_service.to_estate_search(callback_query, state)

        # Assert
        tracer = wewall_expert_callback_service.tracer
        utils.assert_span_error(tracer, err, 1)

    async def test_to_estate_expert(
            self,
            wewall_expert_callback_service,
            mocks
    ):
        # Arrange
        state = utils.create_state(common.StateStatuses.wewall_expert)
        callback_query = utils.create_callback_query(
            common.WewallExpertKeyboardCallbackData.to_estate_expert,
            "Расскажи о недвижимости"
        )

        llm_response = "Хорошо, расскажу о недвижимости" + common.StateSwitchCommand.to_estate_expert
        mocks["estate_expert_client"].send_message_to_estate_expert.return_value = llm_response

        # Act
        await wewall_expert_callback_service.to_estate_expert(callback_query, state)

        # Assert
        mocks["estate_expert_client"].delete_all_message.assert_awaited_once_with(callback_query.message.chat.id)

        mocks["state_repo"].change_status.assert_awaited_once_with(state.id, common.StateStatuses.estate_expert)

        callback_query.message.answer.assert_awaited_once_with(llm_response)

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            callback_query.message.chat.id,
            llm_response
        )

        tracer = wewall_expert_callback_service.tracer
        utils.assert_span(tracer, [
            {
                "name": "WewallExpertCallbackService.to_estate_expert",
            }
        ])

    async def test_to_estate_expert_err(
            self,
            wewall_expert_callback_service,
            mocks
    ):
        # Arrange
        state = utils.create_state(common.StateStatuses.wewall_expert)
        callback_query = utils.create_callback_query(
            common.WewallExpertKeyboardCallbackData.to_estate_expert,
            "Расскажи о недвижимости"
        )

        err = Exception("Ошибка при to_estate_expert")
        mocks["estate_expert_client"].delete_all_message.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка при to_estate_expert"):
            await wewall_expert_callback_service.to_estate_expert(callback_query, state)

        # Assert
        tracer = wewall_expert_callback_service.tracer
        utils.assert_span_error(tracer, err, 1)

    async def test_to_manager(
            self,
            wewall_expert_callback_service,
            mocks
    ):
        # Arrange
        state = utils.create_state(common.StateStatuses.wewall_expert)
        callback_query = utils.create_callback_query(
            common.WewallExpertKeyboardCallbackData.to_manager,
            "Менеджера в срочном порядке"
        )

        summary = "Хорошо, Сейчас подключу менеджера" + common.StateSwitchCommand.to_manager
        mocks["estate_expert_client"].summary.return_value = summary

        # Act
        await wewall_expert_callback_service.to_manager(callback_query, state)

        # Assert
        mocks["chat_client"].edit_lead.assert_awaited_once_with(
            callback_query.message.chat.id,
            wewall_expert_callback_service.amocrm_appeal_pipeline_id,
            common.AmocrmPipelineStatus.chat_with_manager
        )

        mocks["estate_expert_client"].delete_all_message.assert_awaited_once_with(callback_query.message.chat.id)

        callback_query.message.answer.assert_awaited_once_with(common.manger_is_connecting_text)

        mocks["chat_client"].import_message_to_amocrm.assert_has_calls([
            call(state.tg_chat_id, summary),
            call(callback_query.message.chat.id, common.manger_is_connecting_text)
        ])

        tracer = wewall_expert_callback_service.tracer
        utils.assert_span(tracer, [
            {
                "name": "WewallExpertCallbackService.to_manager",
            }
        ])

    async def test_to_manager_err(
            self,
            wewall_expert_callback_service,
            mocks
    ):
        # Arrange
        state = utils.create_state(common.StateStatuses.wewall_expert)
        callback_query = utils.create_callback_query(
            common.WewallExpertKeyboardCallbackData.to_manager,
            "Менеджера в срочном порядке"
        )

        err = Exception("Ошибка при to_manager")
        mocks["estate_expert_client"].summary.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка при to_manager"):
            await wewall_expert_callback_service.to_manager(callback_query, state)

        # Assert
        tracer = wewall_expert_callback_service.tracer
        utils.assert_span_error(tracer, err, 1)