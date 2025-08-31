from unittest.mock import MagicMock, call, ANY

import pytest
from aiogram.types import ReplyKeyboardRemove

from internal import common
from internal.service.amocrm_manager.message_service import AmocrmManagerMessageService
from tests.unit import utils



class TestAmocrmManagerMessageService:

    @pytest.fixture
    def amocrm_manager_message_service(self, mocks):
        return AmocrmManagerMessageService(
            tel=mocks["tel"],
            state_repo=mocks["state_repo"],
            chat_client=mocks["chat_client"],
            estate_expert_client=mocks["estate_expert_client"],
            wewall_expert_inline_keyboard_generator=mocks["wewall_expert_inline_keyboard_generator"],
        )

    async def test_handler_close_chat_with_manager(
            self,
            mocks,
            amocrm_manager_message_service,
    ):
        # Arrange
        message = utils.create_message("Закрыть чат с менеджером")
        state = utils.create_state(common.StateStatuses.chat_with_amocrm_manager)

        llm_response = "Чат с менеджером закрыт. Я готов помочь вам с вопросами о WEWALL."
        mocks["estate_expert_client"].send_message_to_wewall_expert.return_value = llm_response

        keyboard_mock = MagicMock()
        mocks["wewall_expert_inline_keyboard_generator"].start.return_value = keyboard_mock

        # Act
        await amocrm_manager_message_service.handler(message, state)

        # Assert
        mocks["chat_client"].import_message_to_amocrm.assert_has_awaits([
            call(message.chat.id, "Клиент закрыл чат с менеджером"),
            call(state.tg_chat_id, llm_response)
        ])

        mocks["state_repo"].change_status.assert_awaited_once_with(
            state.id, common.StateStatuses.wewall_expert
        )

        mocks["estate_expert_client"].send_message_to_wewall_expert.assert_awaited_once_with(
            message.chat.id,
            "Чат с менеджером закрыт. Расскажи о своих возможностях и сообщи мне, что чат закрыт"
        )

        message.answer.assert_has_awaits([
            call("Чат с менеджером закрыт", reply_markup=ANY),
            call(llm_response, reply_markup=keyboard_mock)
        ])
        first_call_markup = message.answer.await_args_list[0].kwargs["reply_markup"]
        assert isinstance(first_call_markup, ReplyKeyboardRemove)

        tracer = amocrm_manager_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "AmocrmManagerMessageService.handler"}
        ])

    async def test_handler_close_chat_with_manager_err(
            self,
            mocks,
            amocrm_manager_message_service,
    ):
        # Arrange
        message = utils.create_message("Закрыть чат с менеджером")
        state = utils.create_state(common.StateStatuses.chat_with_amocrm_manager)

        err = Exception("Ошибка при закрытии чата")
        mocks["chat_client"].import_message_to_amocrm.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка при закрытии чата"):
            await amocrm_manager_message_service.handler(message, state)

        # Assert
        tracer = amocrm_manager_message_service.tracer
        utils.assert_span_error(tracer, err, 1)

    async def test_handler_message_to_manager(
            self,
            mocks,
            amocrm_manager_message_service,
    ):
        # Arrange
        message = utils.create_message("Обычное сообщение менеджеру")
        state = utils.create_state(common.StateStatuses.chat_with_amocrm_manager)

        # Act
        await amocrm_manager_message_service.handler(message, state)

        # Assert
        mocks["chat_client"].import_message_to_amocrm.assert_not_awaited()
        mocks["chat_client"].send_message_to_amocrm.assert_not_awaited()
        message.answer.assert_not_called()

        tracer = amocrm_manager_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "AmocrmManagerMessageService.handler"}
        ])