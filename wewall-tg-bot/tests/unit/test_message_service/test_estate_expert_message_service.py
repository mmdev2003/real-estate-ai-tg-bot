from unittest.mock import MagicMock, call

import pytest

from internal import common
from internal.service.estate_expert.message_service import EstateExpertMessageService

from tests.unit import utils


class TestEstateExpertMessageService:

    @pytest.fixture
    def estate_expert_message_service(self, mocks):
        return EstateExpertMessageService(
            tel=mocks["tel"],
            state_repo=mocks["state_repo"],
            estate_expert_client=mocks["estate_expert_client"],
            chat_client=mocks["chat_client"],
            wewall_expert_inline_keyboard_generator=mocks["wewall_expert_inline_keyboard_generator"],
            amocrm_appeal_pipeline_id=5353,
        )

    async def test_handler_simple_llm_response(
            self,
            mocks,
            estate_expert_message_service,
    ):
        # Arrange
        message = utils.create_message("Расскажи про рынок недвижимости")
        state = utils.create_state(common.StateStatuses.estate_expert)

        llm_response = "Рынок недвижимости в Москве показывает стабильный рост..."
        mocks["estate_expert_client"].send_message_to_estate_expert.return_value = llm_response

        # Act
        await estate_expert_message_service.handler(message, state)

        # Assert
        mocks["estate_expert_client"].send_message_to_estate_expert.assert_awaited_once_with(
            message.chat.id,
            message.text
        )

        message.answer.assert_awaited_once_with(llm_response)

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            message.chat.id,
            llm_response
        )

        tracer = estate_expert_message_service.tracer
        utils.assert_span(tracer, [{"name": "EstateExpertMessageService.handler"}])

    async def test_handler_simple_llm_response_error(
            self,
            mocks,
            estate_expert_message_service,
    ):
        # Arrange
        message = utils.create_message("Расскажи про рынок недвижимости")
        state = utils.create_state(common.StateStatuses.estate_expert)

        err = Exception("Ошибка при отправке сообщения estate_expert_client")
        mocks["estate_expert_client"].send_message_to_estate_expert.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка при отправке сообщения estate_expert_client"):
            await estate_expert_message_service.handler(message, state)

        # Assert
        tracer = estate_expert_message_service.tracer
        utils.assert_span_error(tracer, err, 1)

    async def test_handler_to_manager_llm_response(
            self,
            mocks,
            estate_expert_message_service,
    ):
        # Arrange
        message = utils.create_message("Хочу поговорить с менеджером")
        state = utils.create_state(common.StateStatuses.estate_expert)

        llm_response = "Здравствуйте! хорошо." + common.StateSwitchCommand.to_manager
        mocks["estate_expert_client"].send_message_to_estate_expert.return_value = llm_response

        # __to_manager
        chat_summary = "Краткое резюме диалога с клиентом о недвижимости"
        mocks["estate_expert_client"].summary.return_value = chat_summary

        wewall_expert_response = "Добро пожаловать! Расскажу вам про WEWALL"
        mocks["estate_expert_client"].send_message_to_wewall_expert.return_value = wewall_expert_response

        keyboard_mock = MagicMock()
        mocks["wewall_expert_inline_keyboard_generator"].start.return_value = keyboard_mock

        # Act
        await estate_expert_message_service.handler(message, state)

        # Assert
        mocks["estate_expert_client"].send_message_to_estate_expert.assert_awaited_once_with(
            message.chat.id,
            message.text
        )

        # __to_manager
        mocks["estate_expert_client"].summary.assert_awaited_once_with(message.chat.id)

        mocks["estate_expert_client"].delete_all_message.assert_awaited_once_with(message.chat.id)

        mocks["estate_expert_client"].send_message_to_wewall_expert.assert_awaited_once_with(
            message.chat.id,
            "Расскажи мне про WEWALL"
        )

        mocks["wewall_expert_inline_keyboard_generator"].start.assert_awaited_once()

        mocks["chat_client"].edit_lead.assert_awaited_once_with(
            message.chat.id,
            estate_expert_message_service.amocrm_appeal_pipeline_id,
            common.AmocrmPipelineStatus.chat_with_manager
        )

        mocks["chat_client"].import_message_to_amocrm.assert_has_awaits([
            call(message.chat.id, chat_summary),
            call(message.chat.id, wewall_expert_response)
        ])

        message.answer.assert_has_awaits([
            call(common.manger_is_connecting_text),
            call(wewall_expert_response, reply_markup=keyboard_mock)
        ])

        mocks["state_repo"].change_status.assert_awaited_once_with(
            state.id,
            common.StateStatuses.wewall_expert
        )

        tracer = estate_expert_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "EstateExpertMessageService.handler"},
            {"name": "EstateExpertMessageService.__to_manager"}
        ])

    async def test_handler_to_manager_llm_response_err(
            self,
            mocks,
            estate_expert_message_service,
    ):
        # Arrange
        message = utils.create_message("Хочу поговорить с менеджером")
        state = utils.create_state(common.StateStatuses.estate_expert)

        llm_response = "Хорошо, подключаю менеджера. " + common.StateSwitchCommand.to_manager
        mocks["estate_expert_client"].send_message_to_estate_expert.return_value = llm_response

        # __to_manager
        err = Exception("Ошибка __to_manager")
        mocks["estate_expert_client"].summary.side_effect = err

        with pytest.raises(Exception, match="Ошибка __to_manager"):
            await estate_expert_message_service.handler(message, state)

        # Assert
        tracer = estate_expert_message_service.tracer
        utils.assert_span_error(tracer, err, 2)

    async def test_handler_to_estate_finance_model_expert_llm_response(
            self,
            mocks,
            estate_expert_message_service,
    ):
        # Arrange
        message = utils.create_message("Помоги рассчитать доходность")
        state = utils.create_state(common.StateStatuses.estate_expert)

        llm_response = "Переключаю на расчет доходности. " + common.StateSwitchCommand.to_estate_finance_model_expert
        mocks["estate_expert_client"].send_message_to_estate_expert.return_value = llm_response

        # __to_estate_finance_model_expert
        finance_model_response = "Помогу рассчитать доходность недвижимости..."
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.return_value = finance_model_response

        # Act
        await estate_expert_message_service.handler(message, state)

        # Assert
        mocks["estate_expert_client"].send_message_to_estate_expert.assert_awaited_once_with(
            message.chat.id,
            message.text
        )

        # __to_estate_finance_model_expert
        mocks["estate_expert_client"].delete_all_message.assert_awaited_once_with(message.chat.id)
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.assert_awaited_once_with(
            message.chat.id,
            "Помоги, мне рассчитать доходность недвижимости"
        )

        message.answer.assert_awaited_once_with(finance_model_response)

        mocks["state_repo"].change_status.assert_awaited_once_with(
            state.id,
            common.StateStatuses.estate_finance_model
        )

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            message.chat.id,
            finance_model_response
        )

        tracer = estate_expert_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "EstateExpertMessageService.handler"},
            {"name": "EstateExpertMessageService.__to_estate_finance_model_expert"}
        ])

    async def test_handler_to_estate_finance_model_expert_err(
            self,
            mocks,
            estate_expert_message_service,
    ):
        # Arrange
        message = utils.create_message("Помоги рассчитать доходность")
        state = utils.create_state(common.StateStatuses.estate_expert)

        llm_response = "Переключаю на расчет доходности. " + common.StateSwitchCommand.to_estate_finance_model_expert
        mocks["estate_expert_client"].send_message_to_estate_expert.return_value = llm_response

        # __to_estate_finance_model_expert
        err = Exception("Ошибка __to_estate_finance_model_expert")
        mocks["estate_expert_client"].delete_all_message.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка __to_estate_finance_model_expert"):
            await estate_expert_message_service.handler(message, state)

        # Assert
        tracer = estate_expert_message_service.tracer
        utils.assert_span_error(tracer, err, 2)

    async def test_handler_to_wewall_expert_llm_response(
            self,
            mocks,
            estate_expert_message_service
    ):
        # Arrange
        message = utils.create_message("Расскажи про WEWALL")
        state = utils.create_state(common.StateStatuses.estate_expert)

        llm_response = "Переключаю на WEWALL эксперта. " + common.StateSwitchCommand.to_wewall_expert
        mocks["estate_expert_client"].send_message_to_estate_expert.return_value = llm_response

        # __to_wewall_expert
        wewall_expert_response = "Расскажу вам про WEWALL..."
        mocks["estate_expert_client"].send_message_to_wewall_expert.return_value = wewall_expert_response

        keyboard_mock = MagicMock()
        mocks["wewall_expert_inline_keyboard_generator"].start.return_value = keyboard_mock

        # Act
        await estate_expert_message_service.handler(message, state)

        mocks["estate_expert_client"].send_message_to_estate_expert.assert_awaited_once_with(
            message.chat.id,
            message.text
        )

        # __to_wewall_expert
        mocks["estate_expert_client"].delete_all_message.assert_awaited_once_with(message.chat.id)

        mocks["estate_expert_client"].send_message_to_wewall_expert.assert_awaited_once_with(
            message.chat.id,
            "Расскажи мне про WEWALL"
        )

        mocks["state_repo"].change_status.assert_awaited_once_with(
            state.id, common.StateStatuses.wewall_expert
        )

        mocks["wewall_expert_inline_keyboard_generator"].start.assert_awaited_once()
        message.answer.assert_awaited_once_with(wewall_expert_response, reply_markup=keyboard_mock)

        mocks["state_repo"].change_status.assert_awaited_once_with(
            state.id,
            common.StateStatuses.wewall_expert
        )

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(message.chat.id, wewall_expert_response)

        tracer = estate_expert_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "EstateExpertMessageService.handler"},
            {"name": "EstateExpertMessageService.__to_wewall_expert"}
        ])

    async def test_handler_to_wewall_expert_err(
            self,
            mocks,
            estate_expert_message_service,
    ):
        # Arrange
        message = utils.create_message("Расскажи про WEWALL")
        state = utils.create_state(common.StateStatuses.estate_expert)

        llm_response = "Переключаю на WEWALL эксперта. " + common.StateSwitchCommand.to_wewall_expert
        mocks["estate_expert_client"].send_message_to_estate_expert.return_value = llm_response

        # __to_wewall_expert
        err = Exception("Ошибка __to_wewall_expert")
        mocks["estate_expert_client"].delete_all_message.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка __to_wewall_expert"):
            await estate_expert_message_service.handler(message, state)

        # Assert
        tracer = estate_expert_message_service.tracer
        utils.assert_span_error(tracer, err, 2)

    async def test_handler_to_estate_search_expert_llm_response(
            self,
            mocks,
            estate_expert_message_service
    ):
        # Arrange
        message = utils.create_message("Помоги найти недвижимость")
        state = utils.create_state(common.StateStatuses.estate_expert)

        llm_response = "Переключаю на поиск недвижимости. " + common.StateSwitchCommand.to_estate_search_expert
        mocks["estate_expert_client"].send_message_to_estate_expert.return_value = llm_response

        # __to_estate_search_expert
        estate_search_response = "Помогу подобрать недвижимость из ассортимента..."
        mocks["estate_expert_client"].send_message_to_estate_search_expert.return_value = estate_search_response

        # Act
        await estate_expert_message_service.handler(message, state)

        # Assert
        mocks["estate_expert_client"].send_message_to_estate_expert.assert_awaited_once_with(
            message.chat.id,
            message.text
        )

        # __to_estate_search_expert
        mocks["estate_expert_client"].delete_all_message.assert_awaited_once_with(message.chat.id)
        mocks["estate_expert_client"].send_message_to_estate_search_expert.assert_awaited_once_with(
            message.chat.id,
            "Помоги мне подобрать недвижимость из вашего ассортимента"
        )

        message.answer.assert_awaited_once_with(estate_search_response)

        mocks["state_repo"].change_status.assert_awaited_once_with(
            state.id,
            common.StateStatuses.estate_search
        )

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(message.chat.id, estate_search_response)

        tracer = estate_expert_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "EstateExpertMessageService.handler"},
             {"name": "EstateExpertMessageService.__to_estate_search_expert"}
        ])

    async def test_handler_to_estate_search_expert_error(
            self,
            mocks,
            estate_expert_message_service
    ):
        # Arrange
        message = utils.create_message("Помоги найти недвижимость")
        state = utils.create_state(common.StateStatuses.estate_expert)

        llm_response = "Переключаю на поиск недвижимости. " + common.StateSwitchCommand.to_estate_search_expert
        mocks["estate_expert_client"].send_message_to_estate_expert.return_value = llm_response

        # __to_estate_search_expert
        err = Exception("Ошибка __to_estate_search_expert")
        mocks["state_repo"].change_status.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка __to_estate_search_expert"):
            await estate_expert_message_service.handler(message, state)

        # Assert
        tracer = estate_expert_message_service.tracer
        utils.assert_span_error(tracer, err, 2)