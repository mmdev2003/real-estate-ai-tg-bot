from unittest.mock import call

import pytest
from opentelemetry.trace import SpanKind, StatusCode

from internal import common, model
from internal.service.state.service import StateService

from tests.unit import utils


class TestStateService:

    @pytest.fixture
    def state_service(self, mocks):
        return StateService(
            tel=mocks["tel"],
            state_repo=mocks["state_repo"],
        )

    async def test_create_state(self, mocks, state_service):
        # Arrange
        tg_chat_id = 123456789
        expected_state_id = 42

        mocks["state_repo"].create_state.return_value = expected_state_id

        # Act
        result = await state_service.create_state(tg_chat_id)

        # Assert
        assert result == expected_state_id

        mocks["state_repo"].create_state.assert_awaited_once_with(tg_chat_id)
        tracer = state_service.tracer
        utils.assert_span(tracer, [
            {"name": "StateService.create_state", "attributes": {"tg_chat_id": tg_chat_id}}
        ])

    async def test_create_state_err(self, mocks, state_service):
        # Arrange
        tg_chat_id = 123456789

        err = Exception("Ошибка при create_state")
        mocks["state_repo"].create_state.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка при create_state"):
            await state_service.create_state(tg_chat_id)

        # Assert
        tracer = state_service.tracer
        utils.assert_span_error(tracer, err, 1)

    async def test_state_by_id(self, mocks, state_service):
        # Arrange
        expected_state = utils.create_state(common.StateStatuses.wewall_expert)

        mocks["state_repo"].state_by_id.return_value = expected_state

        # Act
        result = await state_service.state_by_id(expected_state.tg_chat_id)

        # Assert
        assert result == expected_state

        mocks["state_repo"].state_by_id.assert_awaited_once_with(expected_state.tg_chat_id)
        tracer = state_service.tracer
        utils.assert_span(tracer, [
            {"name": "StateService.state_by_id", "attributes": {"tg_chat_id": expected_state.tg_chat_id}}
        ])

    async def test_state_by_id_err(self, mocks, state_service):
        expected_state = utils.create_state(common.StateStatuses.wewall_expert)

        err = Exception("Ошибка при state_by_id")
        mocks["state_repo"].state_by_id.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка при state_by_id"):
            await state_service.state_by_id(expected_state.tg_chat_id)

        # Assert
        tracer = state_service.tracer
        utils.assert_span_error(tracer, err, 1)

    async def test_increment_message_count(self, mocks, state_service):
        # Arrange
        state_id = 1

        # Act
        await state_service.increment_message_count(state_id)

        # Assert
        mocks["state_repo"].increment_message_count.assert_awaited_once_with(state_id)

        tracer = state_service.tracer
        utils.assert_span(tracer, [
            {"name": "StateService.increment_message_count", "attributes": {"state_id": state_id}}
        ])

    async def test_increment_message_count_err(self, mocks, state_service):
        # Arrange
        state_id = 1

        err = Exception("Ошибка при increment_message_count")
        mocks["state_repo"].increment_message_count.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка при increment_message_count"):
            await state_service.increment_message_count(state_id)

        # Assert
        tracer = state_service.tracer
        utils.assert_span_error(tracer, err, 1)

    async def test_change_status(self, mocks, state_service):
        # Arrange
        state_id = 1
        status = common.StateStatuses.wewall_expert

        # Act
        await state_service.change_status(state_id, status)

        # Assert
        mocks["state_repo"].change_status.assert_awaited_once_with(state_id, status)

        tracer = state_service.tracer
        utils.assert_span(tracer, [
            {"name": "StateService.change_status", "attributes": {"status": status, "state_id": state_id}}
        ])

    async def test_change_status_err(self, mocks, state_service):
        # Arrange
        state_id = 1
        status = common.StateStatuses.wewall_expert

        err = Exception("Ошибка при change_status")
        mocks["state_repo"].change_status.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка при change_status"):
            await state_service.change_status(state_id, status)

        # Assert
        tracer = state_service.tracer
        utils.assert_span_error(tracer, err, 1)

    async def test_delete_state_by_tg_chat_id(self, mocks, state_service):
        # Arrange
        tg_chat_id = 123456789

        # Act
        await state_service.delete_state_by_tg_chat_id(tg_chat_id)

        # Assert
        mocks["state_repo"].delete_state_by_tg_chat_id.assert_awaited_once_with(tg_chat_id)

        tracer = state_service.tracer
        utils.assert_span(tracer, [
            {"name": "StateService.delete_state_by_tg_chat_id", "attributes": {"tg_chat_id": tg_chat_id}}
        ])

    async def test_delete_state_by_tg_chat_id_err(self, mocks, state_service):
        # Arrange
        tg_chat_id = 123456789

        err = Exception("Ошибка при delete_state_by_tg_chat_id")
        mocks["state_repo"].delete_state_by_tg_chat_id.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка при delete_state_by_tg_chat_id"):
            await state_service.delete_state_by_tg_chat_id(tg_chat_id)

        # Assert
        tracer = state_service.tracer
        utils.assert_span_error(tracer, err, 1)
