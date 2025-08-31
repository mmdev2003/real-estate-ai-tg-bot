import pytest

from internal import common
from internal.controller.tg.callback.wewall_expert.handler import WewallExpertCallbackController
from tests.unit import utils


class TestWewallExpertCallbackController:

    @pytest.fixture
    def wewall_expert_callback_controller(self, mocks):
        return WewallExpertCallbackController(
            tel=mocks["tel"],
            dp=mocks["dp"],
            wewall_expert_callback_service=mocks["wewall_expert_callback_service"],
        )

    async def test_to_estate_search(self, wewall_expert_callback_controller, mocks):
        # Arrange
        user_state = utils.create_state(common.StateStatuses.wewall_expert)
        callback_query = utils.create_callback_query(
            common.WewallExpertKeyboardCallbackData.to_estate_search,
            "Подбор недвижимости"
        )

        # Act
        await wewall_expert_callback_controller.wewall_expert_callback(callback_query, user_state)

        # Assert
        mocks["wewall_expert_callback_service"].to_estate_search.assert_awaited_once_with(
            callback_query,
            user_state
        )

        tracer = mocks["tel"].tracer()
        utils.assert_span(tracer, [
            {
                "name": "WewallExpertCallbackController.wewall_expert_callback",
         }
        ])

    async def test_to_estate_finance_model(self, wewall_expert_callback_controller, mocks):
        # Arrange
        user_state = utils.create_state(common.StateStatuses.wewall_expert)
        callback_query = utils.create_callback_query(
            common.WewallExpertKeyboardCallbackData.to_estate_finance_model,
            "Оценка доходности"
        )

        # Act
        await wewall_expert_callback_controller.wewall_expert_callback(callback_query, user_state)

        # Assert
        mocks["wewall_expert_callback_service"].to_estate_finance_model.assert_awaited_once_with(
            callback_query,
            user_state
        )

        tracer = mocks["tel"].tracer()
        utils.assert_span(tracer, [
            {
                "name": "WewallExpertCallbackController.wewall_expert_callback",
         }
        ])

    async def test_to_estate_expert(self, wewall_expert_callback_controller, mocks):
        # Arrange
        user_state = utils.create_state(common.StateStatuses.wewall_expert)
        callback_query = utils.create_callback_query(
            common.WewallExpertKeyboardCallbackData.to_estate_expert,
            "Тренды и новости"
        )

        # Act
        await wewall_expert_callback_controller.wewall_expert_callback(callback_query, user_state)

        # Assert
        mocks["wewall_expert_callback_service"].to_estate_expert.assert_awaited_once_with(
            callback_query,
            user_state
        )

        tracer = mocks["tel"].tracer()
        utils.assert_span(tracer, [
            {
                "name": "WewallExpertCallbackController.wewall_expert_callback",
         }
        ])

    async def test_to_manager(self, wewall_expert_callback_controller, mocks):
        # Arrange
        user_state = utils.create_state(common.StateStatuses.wewall_expert)
        callback_query = utils.create_callback_query(
            common.WewallExpertKeyboardCallbackData.to_manager,
            "Связаться с менеджером"
        )

        # Act
        await wewall_expert_callback_controller.wewall_expert_callback(callback_query, user_state)

        # Assert
        mocks["wewall_expert_callback_service"].to_manager.assert_awaited_once_with(
            callback_query,
            user_state
        )

        tracer = mocks["tel"].tracer()
        utils.assert_span(tracer, [
            {
                "name": "WewallExpertCallbackController.wewall_expert_callback",
         }
        ])

    async def test_wewall_expert_callback_err(self, wewall_expert_callback_controller, mocks):
        # Arrange
        user_state = utils.create_state(common.StateStatuses.wewall_expert)
        callback_query = utils.create_callback_query(
            common.WewallExpertKeyboardCallbackData.to_estate_search,
            "Подбор недвижимости"
        )

        err = Exception("Ошибка при to_estate_search")
        mocks["wewall_expert_callback_service"].to_estate_search.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка при to_estate_search"):
            await wewall_expert_callback_controller.wewall_expert_callback(callback_query, user_state)

        # Assert
        tracer = wewall_expert_callback_controller.tracer
        utils.assert_span_error(tracer, err, 1)