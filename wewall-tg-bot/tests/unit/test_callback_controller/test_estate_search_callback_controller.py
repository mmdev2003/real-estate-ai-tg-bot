import pytest

from internal import common
from internal.controller.tg.callback.estate_search.handler import EstateSearchCallbackController
from tests.unit import utils


class TestWewallExpertCallbackController:

    @pytest.fixture
    def estate_search_callback_controller(self, mocks):
        return EstateSearchCallbackController(
            tel=mocks["tel"],
            dp=mocks["dp"],
            estate_search_callback_service=mocks["estate_search_callback_service"],
        )

    async def test_like_offer(self, estate_search_callback_controller, mocks):
        # Arrange
        offer_id = 1
        user_state = utils.create_state(common.StateStatuses.estate_search)
        callback_query = utils.create_callback_query(
            common.EstateSearchKeyboardCallbackData.like_offer+f":{offer_id}",
            "Записаться на просмотр"
        )

        # Act
        await estate_search_callback_controller.estate_search_callback(callback_query, user_state)

        # Assert
        mocks["estate_search_callback_service"].like_offer.assert_awaited_once_with(
            callback_query,
            user_state,
            offer_id
        )

        tracer = mocks["tel"].tracer()
        utils.assert_span(tracer, [
            {
                "name": "EstateSearchCallbackController.estate_search_callback",
         }
        ])

    async def test_next_offer(self, estate_search_callback_controller, mocks):
        # Arrange
        offer_id = 1
        user_state = utils.create_state(common.StateStatuses.estate_search)
        callback_query = utils.create_callback_query(
            common.EstateSearchKeyboardCallbackData.next_offer+f":{offer_id}",
            "Следующее предложение"
        )

        # Act
        await estate_search_callback_controller.estate_search_callback(callback_query, user_state)

        # Assert
        mocks["estate_search_callback_service"].next_offer.assert_awaited_once_with(
            callback_query,
            user_state,
        )

        tracer = mocks["tel"].tracer()
        utils.assert_span(tracer, [
            {
                "name": "EstateSearchCallbackController.estate_search_callback",
         }
        ])

    async def test_estate_search_callback_err(self, estate_search_callback_controller, mocks):
        # Arrange
        offer_id = 1
        user_state = utils.create_state(common.StateStatuses.estate_search)
        callback_query = utils.create_callback_query(
            common.EstateSearchKeyboardCallbackData.next_offer+f":{offer_id}",
            "Следующее предложение"
        )

        err = Exception("Ошибка в estate_search_callback_controller")
        mocks["estate_search_callback_service"].next_offer.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка в estate_search_callback_controller"):
            await estate_search_callback_controller.estate_search_callback(callback_query, user_state)

        # Assert
        tracer = estate_search_callback_controller.tracer
        utils.assert_span_error(tracer, err, 1)