import json

import pytest

from internal import common
from internal.repo.estate_search_state.repo import EstateSearchStateRepo
from internal.repo.estate_search_state.query import *

from tests.unit import utils


class TestEstateSearchStateRepo:
    @pytest.fixture
    def estate_search_state_repo(self, mocks):
        return EstateSearchStateRepo(
            tel=mocks["tel"],
            db=mocks["db"]
        )

    async def test_create_estate_search_state(self, estate_search_state_repo, mocks):
        # Arrange
        state_id = 1
        offers = [utils.create_sale_offer("Офис"), utils.create_sale_offer("Ритейл")]
        estate_search_params = utils.estate_search_params("Покупка", "Офис")

        offer_id = 1
        mocks["db"].insert.return_value = offer_id

        # Act
        result = await estate_search_state_repo.create_estate_search_state(
            state_id,
            offers,
            estate_search_params
        )

        # Assert
        assert result == offer_id
        mocks["db"].insert.assert_called_once_with(
            create_estate_search_state_query,
            {
                'state_id': state_id,
                'offers': [json.dumps(offer.to_dict(), ensure_ascii=False) for offer in offers],
                'estate_search_params': json.dumps(estate_search_params, ensure_ascii=False)
            }
        )

        tracer = estate_search_state_repo.tracer
        utils.assert_span(tracer, [
            {"name": "EstateSearchStateRepo.create_estate_search_state",
             "attributes":
                 {
                     "state_id": state_id,
                     "offers": str(offers),
                     "estate_search_params": str(estate_search_params),
                 }
             }
        ])

    async def test_create_estate_search_state_err(self, estate_search_state_repo, mocks):
        # Arrange
        state_id = 1
        offers = [utils.create_sale_offer("Офис"), utils.create_sale_offer("Ритейл")]
        estate_search_params = utils.estate_search_params("Покупка", "Офис")

        err = Exception("Ошибка при create_estate_search_state")
        mocks["db"].insert.side_effect = err

        with pytest.raises(Exception, match="Ошибка при create_estate_search_state"):
            await estate_search_state_repo.create_estate_search_state(
                state_id,
                offers,
                estate_search_params
            )

        # Assert
        tracer = estate_search_state_repo.tracer
        utils.assert_span_error(tracer, err, 1)

    async def test_change_current_offer_by_state_id(self, estate_search_state_repo, mocks):
        # Arrange
        state_id = 1
        current_offer_id = 1

        # Act
        await estate_search_state_repo.change_current_offer_by_state_id(
            state_id,
            current_offer_id
        )

        # Assert
        mocks["db"].update.assert_called_once_with(
            change_current_offer_by_state_id_query,
            {
                "state_id": state_id, "current_offer_id": current_offer_id
            }
        )

        tracer = estate_search_state_repo.tracer
        utils.assert_span(tracer, [
            {"name": "EstateSearchStateRepo.change_current_offer_by_state_id",
             "attributes":
                 {
                     "state_id": state_id,
                     "current_offer_id": current_offer_id
                 }
             }
        ])

    async def test_change_current_offer_by_state_id_err(self, estate_search_state_repo, mocks):
        # Arrange
        state_id = 1
        current_offer_id = 1

        err = Exception("Ошибка при change_current_offer_by_state_id")
        mocks["db"].update.side_effect = err

        with pytest.raises(Exception, match="Ошибка при change_current_offer_by_state_id"):
            await estate_search_state_repo.change_current_offer_by_state_id(
                state_id,
                current_offer_id
            )

        # Assert
        tracer = estate_search_state_repo.tracer
        utils.assert_span_error(tracer, err, 1)

    async def test_estate_search_state_by_state_id(self, estate_search_state_repo, mocks):
        # Arrange
        state_id = 1

        # Act
        await estate_search_state_repo.estate_search_state_by_state_id(state_id)

        # Assert
        mocks["db"].select.assert_called_once_with(
            estate_search_state_by_state_id_query,
            {"state_id": state_id}
        )

        tracer = estate_search_state_repo.tracer
        utils.assert_span(tracer, [
            {"name": "EstateSearchStateRepo.estate_search_state_by_state_id",
             "attributes":
                 {
                     "state_id": state_id
                 }
             }
        ])

    async def test_estate_search_state_by_state_id_err(self, estate_search_state_repo, mocks):
        # Arrange
        state_id = 1

        err = Exception("Ошибка при estate_search_state_by_state_id")
        mocks["db"].select.side_effect = err

        with pytest.raises(Exception, match="Ошибка при estate_search_state_by_state_id"):
            await estate_search_state_repo.estate_search_state_by_state_id(
                state_id
            )

        # Assert
        tracer = estate_search_state_repo.tracer
        utils.assert_span_error(tracer, err, 1)

    async def test_delete_estate_search_state_by_state_id(self, estate_search_state_repo, mocks):
        # Arrange
        state_id = 1

        # Act
        await estate_search_state_repo.delete_estate_search_state_by_state_id(state_id)

        # Assert
        mocks["db"].delete.assert_called_once_with(
            delete_estate_search_state_by_state_id_query,
            {"state_id": state_id}
        )

        tracer = estate_search_state_repo.tracer
        utils.assert_span(tracer, [
            {"name": "EstateSearchStateRepo.delete_estate_search_state_by_state_id",
             "attributes":
                 {
                     "state_id": state_id
                 }
             }
        ])

    async def test_delete_estate_search_state_by_state_id_err(self, estate_search_state_repo, mocks):
        # Arrange
        state_id = 1

        err = Exception("Ошибка при delete_estate_search_state_by_state_id")
        mocks["db"].delete.side_effect = err

        with pytest.raises(Exception, match="Ошибка при delete_estate_search_state_by_state_id"):
            await estate_search_state_repo.delete_estate_search_state_by_state_id(
                state_id
            )

        # Assert
        tracer = estate_search_state_repo.tracer
        utils.assert_span_error(tracer, err, 1)