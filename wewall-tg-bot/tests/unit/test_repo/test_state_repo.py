import pytest

from internal import common
from internal.repo.state.repo import StateRepo
from internal.repo.state.query import *

from tests.unit import utils


class TestStateRepo:
    @pytest.fixture
    def state_repo(self, mocks):
        return StateRepo(tel=mocks["tel"], db=mocks["db"])

    async def test_create_state(self, state_repo, mocks):
        # Arrange
        tg_chat_id = 12345
        expected_state_id = 1

        mocks["db"].insert.return_value = expected_state_id

        # Act
        result = await state_repo.create_state(tg_chat_id)

        # Assert
        assert result == expected_state_id
        mocks["db"].insert.assert_called_once_with(create_state, {'tg_chat_id': tg_chat_id})

        tracer = state_repo.tracer
        utils.assert_span(tracer, [
            {"name": "StateRepo.create_state", "attributes": {"tg_chat_id": tg_chat_id}}
        ])

    async def test_create_state_err(self, state_repo, mocks):
        # Arrange
        tg_chat_id = 12345

        err = Exception("Ошибка при create_state")
        mocks["db"].insert.side_effect = err

        with pytest.raises(Exception, match="Ошибка при create_state"):
            await state_repo.create_state(tg_chat_id)

        # Assert
        tracer = state_repo.tracer
        utils.assert_span_error(tracer, err, 1)

    async def test_state_by_id(self, state_repo, mocks):
        # Arrange
        expected_state = utils.create_state(common.StateStatuses.wewall_expert)

        mocks["db"].select.return_value = [expected_state]

        # Act
        result = await state_repo.state_by_id(expected_state.tg_chat_id)

        # Assert
        assert result == [expected_state]

        mocks["db"].select.assert_called_once_with(state_by_id, {'tg_chat_id': expected_state.tg_chat_id})

        tracer = state_repo.tracer
        utils.assert_span(tracer, [
            {"name": "StateRepo.state_by_id", "attributes": {"tg_chat_id": expected_state.tg_chat_id}}
        ])

    async def test_state_by_id_err(self, state_repo, mocks):
        # Arrange
        tg_chat_id = 12345

        err = Exception("Ошибка при state_by_id")
        mocks["db"].select.side_effect = err

        with pytest.raises(Exception, match="Ошибка при state_by_id"):
            await state_repo.state_by_id(tg_chat_id)

        # Assert
        tracer = state_repo.tracer
        utils.assert_span_error(tracer, err, 1)

    async def test_increment_message_count(self, state_repo, mocks):
        # Arrange
        state_id = 1

        # Act
        await state_repo.increment_message_count(state_id)

        # Assert
        mocks["db"].update.assert_called_once_with(increment_message_count, {'state_id': state_id})

        tracer = state_repo.tracer
        utils.assert_span(tracer, [
            {"name": "StateRepo.increment_message_count", "attributes": {"state_id": state_id}}
        ])

    async def test_increment_message_count_err(self, state_repo, mocks):
        # Arrange
        state_id = 1

        err = Exception("Ошибка при increment_message_count")
        mocks["db"].update.side_effect = err

        with pytest.raises(Exception, match="Ошибка при increment_message_count"):
            await state_repo.increment_message_count(state_id)

        # Assert
        tracer = state_repo.tracer
        utils.assert_span_error(tracer, err, 1)

    async def test_increment_estate_search_count(self, state_repo, mocks):
        # Arrange
        state_id = 1

        # Act
        await state_repo.increment_estate_search_count(state_id)

        # Assert
        mocks["db"].update.assert_called_once_with(increment_estate_search_count, {'state_id': state_id})

        tracer = state_repo.tracer
        utils.assert_span(tracer, [
            {"name": "StateRepo.increment_estate_search_count", "attributes": {"state_id": state_id}}
        ])

    async def test_increment_estate_search_count_err(self, state_repo, mocks):
        # Arrange
        state_id = 1

        err = Exception("Ошибка при increment_estate_search_count")
        mocks["db"].update.side_effect = err

        with pytest.raises(Exception, match="Ошибка при increment_estate_search_count"):
            await state_repo.increment_estate_search_count(state_id)

        # Assert
        tracer = state_repo.tracer
        utils.assert_span_error(tracer, err, 1)

    async def test_increment_estate_calculator_count(self, state_repo, mocks):
        # Arrange
        state_id = 1

        # Act
        await state_repo.increment_estate_calculator_count(state_id)

        # Assert
        mocks["db"].update.assert_called_once_with(increment_estate_calculator_count, {'state_id': state_id})

        tracer = state_repo.tracer
        utils.assert_span(tracer, [
            {"name": "StateRepo.increment_estate_calculator_count", "attributes": {"state_id": state_id}}
        ])

    async def test_increment_estate_calculator_count_err(self, state_repo, mocks):
        # Arrange
        state_id = 1

        err = Exception("Ошибка при increment_estate_calculator_count")
        mocks["db"].update.side_effect = err

        with pytest.raises(Exception, match="Ошибка при increment_estate_calculator_count"):
            await state_repo.increment_estate_calculator_count(state_id)

        # Assert
        tracer = state_repo.tracer
        utils.assert_span_error(tracer, err, 1)

    async def test_change_status(self, state_repo, mocks):
        # Arrange
        state_id = 1
        status = common.StateStatuses.wewall_expert

        # Act
        await state_repo.change_status(state_id, status)

        # Assert
        mocks["db"].update.assert_called_once_with(update_state_status, {'state_id': state_id, 'status': status})

        tracer = state_repo.tracer
        utils.assert_span(tracer, [
            {"name": "StateRepo.change_status", "attributes": {"state_id": state_id, "status": status}}
        ])

    async def test_change_status_err(self, state_repo, mocks):
        # Arrange
        state_id = 1

        err = Exception("Ошибка при change_status")
        mocks["db"].update.side_effect = err

        with pytest.raises(Exception, match="Ошибка при change_status"):
            await state_repo.change_status(state_id, common.StateStatuses.wewall_expert)

        # Assert
        tracer = state_repo.tracer
        utils.assert_span_error(tracer, err, 1)

    async def test_delete_state_by_tg_chat_id(self, state_repo, mocks):
        # Arrange
        tg_chat_id = 12345

        # Act
        await state_repo.delete_state_by_tg_chat_id(tg_chat_id)

        # Assert
        mocks["db"].delete.assert_called_once_with(delete_state_by_tg_chat_id, {'tg_chat_id': tg_chat_id})

        tracer = state_repo.tracer
        utils.assert_span(tracer, [
            {"name": "StateRepo.delete_state_by_tg_chat_id", "attributes": {"tg_chat_id": tg_chat_id}}
        ])

    async def test_delete_state_by_tg_chat_id_err(self, state_repo, mocks):
        # Arrange
        state_id = 1

        err = Exception("Ошибка при change_status")
        mocks["db"].update.side_effect = err

        with pytest.raises(Exception, match="Ошибка при change_status"):
            await state_repo.change_status(state_id, common.StateStatuses.wewall_expert)

        # Assert
        tracer = state_repo.tracer
        utils.assert_span_error(tracer, err, 1)
