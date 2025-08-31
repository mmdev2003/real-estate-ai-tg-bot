import pytest
from unittest.mock import MagicMock, call

from opentelemetry.trace import SpanKind
from aiogram.types import BufferedInputFile, InputMediaDocument

from internal import common
from internal.service.estate_search.callback_service import EstateSearchCallbackService
from tests.unit import utils


class TestEstateSearchCallbackService:

    @pytest.fixture
    def estate_search_callback_service(self, mocks):
        return EstateSearchCallbackService(
            tel=mocks["tel"],
            state_repo=mocks["state_repo"],
            estate_search_state_repo=mocks["estate_search_state_repo"],
            chat_client=mocks["chat_client"],
            estate_expert_client=mocks["estate_expert_client"],
            estate_calculator_client=mocks["estate_calculator_client"],
            estate_search_inline_keyboard_generator=mocks["estate_search_inline_keyboard_generator"],
            llm_client=mocks["llm_client"],
        )

    async def test_handle_like_offer(
            self,
            estate_search_callback_service,
            mocks
    ):
        # Arrange
        offer_id = 1
        state = utils.create_state(common.StateStatuses.estate_search)
        callback_query = utils.create_callback_query(
            common.EstateSearchKeyboardCallbackData.like_offer + f":{offer_id}",
            "Записаться на просмотр"
        )

        estate_search_state = [utils.create_estate_search_state("Покупка", "Офис", 8)]
        mocks["estate_search_state_repo"].estate_search_state_by_state_id.return_value = estate_search_state

        offer_text = "Предложение на улице 123"
        mocks["llm_client"].generate.return_value = offer_text

        llm_response = "Здравствуйте! Ваше имя и тд"
        mocks["estate_expert_client"].send_message_to_contact_collector.return_value = llm_response

        # Act
        await estate_search_callback_service.like_offer(callback_query, state, offer_id)

        # Assert
        mocks["state_repo"].change_status.assert_awaited_once_with(state.id, common.StateStatuses.contact_collector)

        callback_query.message.answer.assert_awaited_once_with(llm_response)

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            callback_query.message.chat.id,
            llm_response
        )

        tracer = estate_search_callback_service.tracer
        utils.assert_span(tracer, [
            {
                "name": "EstateSearchCallbackService.like_offer",
                "attributes": {"offer_id": offer_id}
            }
        ])

    async def test_handle_like_offer_err(
            self,
            estate_search_callback_service,
            mocks
    ):
        # Arrange
        offer_id = 1
        state = utils.create_state(common.StateStatuses.estate_search)
        callback_query = utils.create_callback_query(
            common.EstateSearchKeyboardCallbackData.like_offer + f":{offer_id}",
            "Записаться на просмотр"
        )

        err = Exception("Ошибка при like_offer_callback")
        mocks["estate_search_state_repo"].estate_search_state_by_state_id.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка при like_offer_callback"):
            await estate_search_callback_service.like_offer(callback_query, state, offer_id)

        # Assert
        tracer = estate_search_callback_service.tracer
        utils.assert_span_error(tracer, err, 1)

    async def test_handler_next_last_sale_offer_office(
            self,
            estate_search_callback_service,
            mocks
    ):
        # Arrange
        offer_id = 1
        state = utils.create_state(common.StateStatuses.estate_search)
        callback_query = utils.create_callback_query(
            common.EstateSearchKeyboardCallbackData.next_offer + f":{offer_id}",
            "Следующее предложение"
        )

        estate_search_state = [utils.create_estate_search_state("Покупка", "Офис", 2)]
        mocks["estate_search_state_repo"].estate_search_state_by_state_id.return_value = estate_search_state

        keyboard_mock = MagicMock()
        mocks["estate_search_inline_keyboard_generator"].last_offer.return_value = keyboard_mock

        #  __calc_sale_office_finance_model
        calc_resp = utils.create_finance_model_response()
        mocks["estate_calculator_client"].calc_finance_model_finished_office.return_value = calc_resp

        xlsx_file_mock = MagicMock(spec=BufferedInputFile)
        mocks["estate_calculator_client"].calc_finance_model_finished_office_table.return_value = xlsx_file_mock

        pdf_file_mock = MagicMock(spec=BufferedInputFile)
        mocks["estate_calculator_client"].generate_pdf.return_value = pdf_file_mock

        document_media_group = [InputMediaDocument(media=pdf_file_mock), InputMediaDocument(media=xlsx_file_mock)]

        # __nearest_metro
        offer = estate_search_state[0].offers[estate_search_state[0].current_offer_id + 1]
        metro_distances = [metro.leg_distance for metro in offer.metro_stations]
        nearest_metro_distance = min(metro_distances)
        nearest_metro_idx = metro_distances.index(nearest_metro_distance)

        # __generate_offer_text
        offer_text = "Предложение на улице 123"
        offer_text_with_link = offer_text + '\n\nСсылка для саммари для менеджера, а не клиента: ' + offer.sale_offer_link
        mocks["llm_client"].generate.return_value = offer_text

        # Act
        await estate_search_callback_service.next_offer(callback_query, state)

        # Assert
        mocks["estate_search_state_repo"].change_current_offer_by_state_id.assert_awaited_once_with(
            state.id,
            estate_search_state[0].current_offer_id + 1,
        )

        mocks["estate_expert_client"].add_message_to_chat.assert_has_calls([
            call(state.tg_chat_id, "Следующее помещение", "user"),
            call(state.tg_chat_id, offer_text_with_link, "assistant")
        ])

        callback_query.message.answer.assert_awaited_once_with(offer_text, reply_markup=keyboard_mock)
        callback_query.message.answer_media_group.assert_awaited_once_with(document_media_group)

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            callback_query.message.chat.id,
            offer_text
        )

        tracer = estate_search_callback_service.tracer
        utils.assert_span(tracer, [
            {"name": "EstateSearchCallbackService.next_offer"},
            {"name": "EstateSearchCallbackService.__calc_sale_office_finance_model"},
            {"name": "EstateSearchCallbackService.__nearest_metro"},
            {"name": "EstateSearchCallbackService.__generate_offer_text"}
        ])

    async def test_handler_next_last_sale_offer_office_err(
            self,
            estate_search_callback_service,
            mocks
    ):
        # Arrange
        offer_id = 1
        state = utils.create_state(common.StateStatuses.estate_search)
        callback_query = utils.create_callback_query(
            common.EstateSearchKeyboardCallbackData.next_offer + f":{offer_id}",
            "Следующее предложение"
        )

        err = Exception("Ошибка при next_offer_callback")
        mocks["estate_search_state_repo"].estate_search_state_by_state_id.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка при next_offer_callback"):
            await estate_search_callback_service.next_offer(callback_query, state)

        # Assert
        tracer = estate_search_callback_service.tracer
        utils.assert_span_error(tracer, err, 1)

    async def test_handler_next_middle_sale_offer_office(
            self,
            estate_search_callback_service,
            mocks
    ):
        # Arrange
        offer_id = 1
        state = utils.create_state(common.StateStatuses.estate_search)
        callback_query = utils.create_callback_query(
            common.EstateSearchKeyboardCallbackData.next_offer + f":{offer_id}",
            "Следующее предложение"
        )

        estate_search_state = [utils.create_estate_search_state("Покупка", "Офис", 3)]
        mocks["estate_search_state_repo"].estate_search_state_by_state_id.return_value = estate_search_state

        keyboard_mock = MagicMock()
        mocks["estate_search_inline_keyboard_generator"].middle_offer.return_value = keyboard_mock

        #  __calc_sale_office_finance_model
        calc_resp = utils.create_finance_model_response()
        mocks["estate_calculator_client"].calc_finance_model_finished_office.return_value = calc_resp

        xlsx_file_mock = MagicMock(spec=BufferedInputFile)
        mocks["estate_calculator_client"].calc_finance_model_finished_office_table.return_value = xlsx_file_mock

        pdf_file_mock = MagicMock(spec=BufferedInputFile)
        mocks["estate_calculator_client"].generate_pdf.return_value = pdf_file_mock

        document_media_group = [InputMediaDocument(media=pdf_file_mock), InputMediaDocument(media=xlsx_file_mock)]

        # __nearest_metro
        offer = estate_search_state[0].offers[estate_search_state[0].current_offer_id + 1]
        metro_distances = [metro.leg_distance for metro in offer.metro_stations]
        nearest_metro_distance = min(metro_distances)
        nearest_metro_idx = metro_distances.index(nearest_metro_distance)

        # __generate_offer_text
        offer_text = "Предложение на улице 123"
        offer_text_with_link = offer_text + '\n\nСсылка для саммари для менеджера, а не клиента: ' + offer.sale_offer_link
        mocks["llm_client"].generate.return_value = offer_text

        # Act
        await estate_search_callback_service.next_offer(callback_query, state)

        # Assert
        mocks["estate_search_state_repo"].change_current_offer_by_state_id.assert_awaited_once_with(
            state.id,
            estate_search_state[0].current_offer_id + 1,
        )

        mocks["estate_expert_client"].add_message_to_chat.assert_has_calls([
            call(state.tg_chat_id, "Следующее помещение", "user"),
            call(state.tg_chat_id, offer_text_with_link, "assistant")
        ])

        callback_query.message.answer.assert_awaited_once_with(offer_text, reply_markup=keyboard_mock)
        callback_query.message.answer_media_group.assert_awaited_once_with(document_media_group)

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            callback_query.message.chat.id,
            offer_text
        )

    async def test_handler_next_middle_sale_offer_office_err(
            self,
            estate_search_callback_service,
            mocks
    ):
        # Arrange
        offer_id = 1
        state = utils.create_state(common.StateStatuses.estate_search)
        callback_query = utils.create_callback_query(
            common.EstateSearchKeyboardCallbackData.next_offer + f":{offer_id}",
            "Следующее предложение"
        )

        err = Exception("Ошибка при next_offer_callback")
        mocks["estate_search_state_repo"].estate_search_state_by_state_id.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка при next_offer_callback"):
            await estate_search_callback_service.next_offer(callback_query, state)

        # Assert
        tracer = estate_search_callback_service.tracer
        utils.assert_span_error(tracer, err, 1)

    async def test_handler_next_last_sale_offer_retail(
            self,
            estate_search_callback_service,
            mocks
    ):
        # Arrange
        offer_id = 1
        state = utils.create_state(common.StateStatuses.estate_search)
        callback_query = utils.create_callback_query(
            common.EstateSearchKeyboardCallbackData.next_offer + f":{offer_id}",
            "Следующее предложение"
        )

        estate_search_state = [utils.create_estate_search_state("Покупка", "Ритейл", 2)]
        mocks["estate_search_state_repo"].estate_search_state_by_state_id.return_value = estate_search_state

        keyboard_mock = MagicMock()
        mocks["estate_search_inline_keyboard_generator"].last_offer.return_value = keyboard_mock

        #  __calc_sale_office_finance_model
        calc_resp = utils.create_finance_model_response()
        mocks["estate_calculator_client"].calc_finance_model_finished_retail.return_value = calc_resp

        xlsx_file_mock = MagicMock(spec=BufferedInputFile)
        mocks["estate_calculator_client"].calc_finance_model_finished_retail_table.return_value = xlsx_file_mock

        pdf_file_mock = MagicMock(spec=BufferedInputFile)
        mocks["estate_calculator_client"].generate_pdf.return_value = pdf_file_mock

        document_media_group = [InputMediaDocument(media=pdf_file_mock), InputMediaDocument(media=xlsx_file_mock)]

        # __nearest_metro
        offer = estate_search_state[0].offers[estate_search_state[0].current_offer_id + 1]
        metro_distances = [metro.leg_distance for metro in offer.metro_stations]
        nearest_metro_distance = min(metro_distances)
        nearest_metro_idx = metro_distances.index(nearest_metro_distance)

        # __generate_offer_text
        offer_text = "Предложение на улице 123"
        offer_text_with_link = offer_text + '\n\nСсылка для саммари для менеджера, а не клиента: ' + offer.sale_offer_link
        mocks["llm_client"].generate.return_value = offer_text

        # Act
        await estate_search_callback_service.next_offer(callback_query, state)

        # Assert
        mocks["estate_search_state_repo"].change_current_offer_by_state_id.assert_awaited_once_with(
            state.id,
            estate_search_state[0].current_offer_id + 1,
        )

        mocks["estate_expert_client"].add_message_to_chat.assert_has_calls([
            call(state.tg_chat_id, "Следующее помещение", "user"),
            call(state.tg_chat_id, offer_text_with_link, "assistant")
        ])

        callback_query.message.answer.assert_awaited_once_with(offer_text, reply_markup=keyboard_mock)
        callback_query.message.answer_media_group.assert_awaited_once_with(document_media_group)

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            callback_query.message.chat.id,
            offer_text
        )

    async def test_handler_next_last_sale_offer_retail_err(
            self,
            estate_search_callback_service,
            mocks
    ):
        # Arrange
        offer_id = 1
        state = utils.create_state(common.StateStatuses.estate_search)
        callback_query = utils.create_callback_query(
            common.EstateSearchKeyboardCallbackData.next_offer + f":{offer_id}",
            "Следующее предложение"
        )

        err = Exception("Ошибка при next_offer_callback")
        mocks["estate_search_state_repo"].estate_search_state_by_state_id.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка при next_offer_callback"):
            await estate_search_callback_service.next_offer(callback_query, state)

        # Assert
        tracer = estate_search_callback_service.tracer
        utils.assert_span_error(tracer, err, 1)

    async def test_handler_next_middle_sale_offer_retail(
            self,
            estate_search_callback_service,
            mocks
    ):
        # Arrange
        offer_id = 1
        state = utils.create_state(common.StateStatuses.estate_search)
        callback_query = utils.create_callback_query(
            common.EstateSearchKeyboardCallbackData.next_offer + f":{offer_id}",
            "Следующее предложение"
        )

        estate_search_state = [utils.create_estate_search_state("Покупка", "Ритейл", 3)]
        mocks["estate_search_state_repo"].estate_search_state_by_state_id.return_value = estate_search_state

        keyboard_mock = MagicMock()
        mocks["estate_search_inline_keyboard_generator"].middle_offer.return_value = keyboard_mock

        #  __calc_sale_office_finance_model
        calc_resp = utils.create_finance_model_response()
        mocks["estate_calculator_client"].calc_finance_model_finished_retail.return_value = calc_resp

        xlsx_file_mock = MagicMock(spec=BufferedInputFile)
        mocks["estate_calculator_client"].calc_finance_model_finished_retail_table.return_value = xlsx_file_mock

        pdf_file_mock = MagicMock(spec=BufferedInputFile)
        mocks["estate_calculator_client"].generate_pdf.return_value = pdf_file_mock

        document_media_group = [InputMediaDocument(media=pdf_file_mock), InputMediaDocument(media=xlsx_file_mock)]

        # __nearest_metro
        offer = estate_search_state[0].offers[estate_search_state[0].current_offer_id + 1]
        metro_distances = [metro.leg_distance for metro in offer.metro_stations]
        nearest_metro_distance = min(metro_distances)
        nearest_metro_idx = metro_distances.index(nearest_metro_distance)

        # __generate_offer_text
        offer_text = "Предложение на улице 123"
        offer_text_with_link = offer_text + '\n\nСсылка для саммари для менеджера, а не клиента: ' + offer.sale_offer_link
        mocks["llm_client"].generate.return_value = offer_text

        # Act
        await estate_search_callback_service.next_offer(callback_query, state)

        # Assert
        mocks["estate_search_state_repo"].change_current_offer_by_state_id.assert_awaited_once_with(
            state.id,
            estate_search_state[0].current_offer_id + 1,
        )

        mocks["estate_expert_client"].add_message_to_chat.assert_has_calls([
            call(state.tg_chat_id, "Следующее помещение", "user"),
            call(state.tg_chat_id, offer_text_with_link, "assistant")
        ])

        callback_query.message.answer.assert_awaited_once_with(offer_text, reply_markup=keyboard_mock)
        callback_query.message.answer_media_group.assert_awaited_once_with(document_media_group)

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            callback_query.message.chat.id,
            offer_text
        )

    async def test_handler_next_middle_sale_offer_retail_err(
            self,
            estate_search_callback_service,
            mocks
    ):
        # Arrange
        offer_id = 1
        state = utils.create_state(common.StateStatuses.estate_search)
        callback_query = utils.create_callback_query(
            common.EstateSearchKeyboardCallbackData.next_offer + f":{offer_id}",
            "Следующее предложение"
        )

        err = Exception("Ошибка при next_offer_callback")
        mocks["estate_search_state_repo"].estate_search_state_by_state_id.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка при next_offer_callback"):
            await estate_search_callback_service.next_offer(callback_query, state)

        # Assert
        tracer = estate_search_callback_service.tracer
        utils.assert_span_error(tracer, err, 1)

    async def test_handler_next_last_rent_offer(
            self,
            estate_search_callback_service,
            mocks
    ):
        # Arrange
        offer_id = 1
        state = utils.create_state(common.StateStatuses.estate_search)
        callback_query = utils.create_callback_query(
            common.EstateSearchKeyboardCallbackData.next_offer + f":{offer_id}",
            "Следующее предложение"
        )

        estate_search_state = [utils.create_estate_search_state("Аренда", "Ритейл", 2)]
        mocks["estate_search_state_repo"].estate_search_state_by_state_id.return_value = estate_search_state

        keyboard_mock = MagicMock()
        mocks["estate_search_inline_keyboard_generator"].last_offer.return_value = keyboard_mock

        # __generate_offer_text
        offer = estate_search_state[0].offers[estate_search_state[0].current_offer_id + 1]

        offer_text = "Предложение на улице 123"
        offer_text_with_link = offer.rent_offer_link
        mocks["llm_client"].generate.return_value = offer_text

        # Act
        await estate_search_callback_service.next_offer(callback_query, state)

        # Assert
        mocks["estate_search_state_repo"].change_current_offer_by_state_id.assert_awaited_once_with(
            state.id,
            estate_search_state[0].current_offer_id + 1,
        )

        mocks["estate_expert_client"].add_message_to_chat.assert_has_calls([
            call(state.tg_chat_id, "Следующее помещение", "user"),
            call(state.tg_chat_id, offer_text_with_link, "assistant")
        ])

        callback_query.message.answer.assert_awaited_once_with(offer_text, reply_markup=keyboard_mock)

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            callback_query.message.chat.id,
            offer_text
        )

    async def test_handler_next_last_rent_offer_err(
            self,
            estate_search_callback_service,
            mocks
    ):
        # Arrange
        offer_id = 1
        state = utils.create_state(common.StateStatuses.estate_search)
        callback_query = utils.create_callback_query(
            common.EstateSearchKeyboardCallbackData.next_offer + f":{offer_id}",
            "Следующее предложение"
        )

        err = Exception("Ошибка при next_offer_callback")
        mocks["estate_search_state_repo"].estate_search_state_by_state_id.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка при next_offer_callback"):
            await estate_search_callback_service.next_offer(callback_query, state)

        # Assert
        tracer = estate_search_callback_service.tracer
        utils.assert_span_error(tracer, err, 1)

    async def test_handler_next_middle_rent_offer(
            self,
            estate_search_callback_service,
            mocks
    ):
        # Arrange
        offer_id = 1
        state = utils.create_state(common.StateStatuses.estate_search)
        callback_query = utils.create_callback_query(
            common.EstateSearchKeyboardCallbackData.next_offer + f":{offer_id}",
            "Следующее предложение"
        )

        estate_search_state = [utils.create_estate_search_state("Аренда", "Офис", 3)]
        mocks["estate_search_state_repo"].estate_search_state_by_state_id.return_value = estate_search_state

        keyboard_mock = MagicMock()
        mocks["estate_search_inline_keyboard_generator"].middle_offer.return_value = keyboard_mock

        # __generate_offer_text
        offer = estate_search_state[0].offers[estate_search_state[0].current_offer_id + 1]

        offer_text = "Предложение на улице 123"
        offer_text_with_link = offer.rent_offer_link
        mocks["llm_client"].generate.return_value = offer_text

        # Act
        await estate_search_callback_service.next_offer(callback_query, state)

        # Assert
        mocks["estate_search_state_repo"].change_current_offer_by_state_id.assert_awaited_once_with(
            state.id,
            estate_search_state[0].current_offer_id + 1,
        )

        mocks["estate_expert_client"].add_message_to_chat.assert_has_calls([
            call(state.tg_chat_id, "Следующее помещение", "user"),
            call(state.tg_chat_id, offer_text_with_link, "assistant")
        ])

        callback_query.message.answer.assert_awaited_once_with(offer_text, reply_markup=keyboard_mock)

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            callback_query.message.chat.id,
            offer_text
        )

    async def test_handler_next_middle_rent_offer_err(
            self,
            estate_search_callback_service,
            mocks
    ):
        # Arrange
        offer_id = 1
        state = utils.create_state(common.StateStatuses.estate_search)
        callback_query = utils.create_callback_query(
            common.EstateSearchKeyboardCallbackData.next_offer + f":{offer_id}",
            "Следующее предложение"
        )

        err = Exception("Ошибка при next_offer_callback")
        mocks["estate_search_state_repo"].estate_search_state_by_state_id.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка при next_offer_callback"):
            await estate_search_callback_service.next_offer(callback_query, state)

        # Assert
        tracer = estate_search_callback_service.tracer
        utils.assert_span_error(tracer, err, 1)