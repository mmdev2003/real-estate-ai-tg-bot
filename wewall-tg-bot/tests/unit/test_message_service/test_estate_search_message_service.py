import json
from unittest.mock import MagicMock, ANY, AsyncMock

import pytest
from aiogram.types import BufferedInputFile

from internal import common
from internal.service.estate_search.message_service import EstateSearchMessageService
from tests.unit import utils


class TestEstateSearchMessageService:

    @pytest.fixture
    def estate_search_message_service(self, mocks):
        return EstateSearchMessageService(
            tel=mocks["tel"],
            state_repo=mocks["state_repo"],
            estate_search_state_repo=mocks["estate_search_state_repo"],
            chat_client=mocks["chat_client"],
            estate_expert_client=mocks["estate_expert_client"],
            estate_search_client=mocks["estate_search_client"],
            estate_calculator_client=mocks["estate_calculator_client"],
            estate_search_inline_keyboard_generator=mocks["estate_search_inline_keyboard_generator"],
            wewall_expert_inline_keyboard_generator=mocks["wewall_expert_inline_keyboard_generator"],
            llm_client=mocks["llm_client"],
            amocrm_main_pipeline_id=1234,
            amocrm_appeal_pipeline_id=5353,
        )

    async def test_handler_simple_llm_response(
            self,
            mocks,
            estate_search_message_service,
    ):
        # Arrange
        message = utils.create_message("Расскажи про поиск недвижимости")
        state = utils.create_state(common.StateStatuses.estate_search)

        llm_response = "Вот информация о поиске недвижимости..."
        mocks["estate_expert_client"].send_message_to_estate_search_expert.return_value = llm_response

        # Act
        await estate_search_message_service.handler(message, state)

        # Assert
        mocks["estate_expert_client"].send_message_to_estate_search_expert.assert_awaited_once_with(
            message.chat.id,
            message.text
        )

        message.answer.assert_awaited_once_with(llm_response)

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            message.chat.id,
            llm_response
        )

        tracer = estate_search_message_service.tracer
        utils.assert_span(tracer, [{"name": "EstateSearchMessageService.handler"}])

    async def test_handler_simple_llm_response_err(
            self,
            mocks,
            estate_search_message_service,
    ):
        # Arrange
        message = utils.create_message("Расскажи про поиск недвижимости")
        state = utils.create_state(common.StateStatuses.estate_search)

        err = Exception("Estate search expert error")
        mocks["estate_expert_client"].send_message_to_estate_search_expert.side_effect = err

        # Act
        with pytest.raises(Exception, match="Estate search expert error"):
            await estate_search_message_service.handler(message, state)

        # Assert
        tracer = estate_search_message_service.tracer
        utils.assert_span_error(tracer, err, 1)

    async def test_handler_to_manager_llm_response(
            self,
            mocks,
            estate_search_message_service,
    ):
        # Arrange
        message = utils.create_message("Хочу поговорить с менеджером")
        state = utils.create_state(common.StateStatuses.estate_search)

        llm_response = "Подключаю менеджера. " + common.StateSwitchCommand.to_manager
        mocks["estate_expert_client"].send_message_to_estate_search_expert.return_value = llm_response

        # __to_manager
        chat_summary = "Клиент искал недвижимость и просит менеджера"
        mocks["estate_expert_client"].summary.return_value = chat_summary

        # Act
        await estate_search_message_service.handler(message, state)

        # Assert
        mocks["estate_expert_client"].send_message_to_estate_search_expert.assert_awaited_once_with(
            message.chat.id,
            message.text
        )

        # __to_manager
        mocks["chat_client"].edit_lead.assert_awaited_once_with(
            message.chat.id,
            estate_search_message_service.amocrm_appeal_pipeline_id,
            common.AmocrmPipelineStatus.chat_with_manager
        )

        mocks["estate_expert_client"].summary.assert_awaited_once_with(message.chat.id)

        mocks["estate_expert_client"].delete_all_message.assert_awaited_once_with(message.chat.id)

        message.answer.assert_awaited_once_with(common.manger_is_connecting_text)

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            message.chat.id,
            chat_summary
        )

        mocks["chat_client"].edit_lead.assert_awaited_once_with(
            message.chat.id,
            estate_search_message_service.amocrm_appeal_pipeline_id,
            common.AmocrmPipelineStatus.chat_with_manager
        )

        tracer = estate_search_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "EstateSearchMessageService.handler"},
            {"name": "EstateSearchMessageService.__to_manager"}
        ])

    async def test_handler_to_manager_llm_response_err(
            self,
            mocks,
            estate_search_message_service,
    ):
        # Arrange
        message = utils.create_message("Хочу поговорить с менеджером")
        state = utils.create_state(common.StateStatuses.estate_search)

        llm_response = "Подключаю менеджера. " + common.StateSwitchCommand.to_manager
        mocks["estate_expert_client"].send_message_to_estate_search_expert.return_value = llm_response

        err = Exception("Ошибка в summary")
        mocks["estate_expert_client"].summary.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка в summary"):
            await estate_search_message_service.handler(message, state)

        # Assert
        tracer = estate_search_message_service.tracer
        utils.assert_span_error(tracer, err, 2)

    async def test_handler_to_estate_finance_model_expert_llm_response(
            self,
            mocks,
            estate_search_message_service,
    ):
        # Arrange
        message = utils.create_message("Хочу рассчитать доходность")
        state = utils.create_state(common.StateStatuses.estate_search)

        llm_response = "Подключаю на расчет доходности. " + common.StateSwitchCommand.to_estate_finance_model_expert
        mocks["estate_expert_client"].send_message_to_estate_search_expert.return_value = llm_response

        # __to_estate_finance_model_expert
        estate_finance_model_expert_response = "Для расчета мне необходимо"
        mocks[
            "estate_expert_client"].send_message_to_estate_finance_model_expert.return_value = estate_finance_model_expert_response

        # Act
        await estate_search_message_service.handler(message, state)

        # Assert
        mocks["estate_expert_client"].send_message_to_estate_search_expert.assert_awaited_once_with(
            message.chat.id,
            message.text
        )

        # __to_estate_finance_model_expert
        mocks["estate_expert_client"].delete_all_message.assert_awaited_once_with(message.chat.id)

        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.assert_awaited_once_with(
            message.chat.id,
            "Помоги, мне рассчитать доходность недвижимости"
        )

        message.answer.assert_awaited_once_with(estate_finance_model_expert_response)

        mocks["state_repo"].change_status.assert_awaited_once_with(
            state.id,
            common.StateStatuses.estate_finance_model
        )

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            message.chat.id,
            estate_finance_model_expert_response
        )

        tracer = estate_search_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "EstateSearchMessageService.handler"},
            {"name": "EstateSearchMessageService.__to_estate_finance_model"},
        ])

    async def test_handler_to_estate_finance_model_expert_llm_response_err(
            self,
            mocks,
            estate_search_message_service
    ):
        # Arrange
        message = utils.create_message("Хочу рассчитать доходность")
        state = utils.create_state(common.StateStatuses.estate_search)

        llm_response = "Подключаю на расчет доходности. " + common.StateSwitchCommand.to_estate_finance_model_expert
        mocks["estate_expert_client"].send_message_to_estate_search_expert.return_value = llm_response

        err = Exception("Ошибка в __to_estate_finance_model")
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка в __to_estate_finance_model"):
            await estate_search_message_service.handler(message, state)

        # Assert
        tracer = estate_search_message_service.tracer
        utils.assert_span_error(tracer, err, 2)

    async def test_handler_to_wewall_expert_llm_response(
            self,
            mocks,
            estate_search_message_service,
    ):
        # Arrange
        message = utils.create_message("Хочу узнать про WEWALL")
        state = utils.create_state(common.StateStatuses.estate_search)

        llm_response = "Подключаю WEWALL. " + common.StateSwitchCommand.to_wewall_expert
        mocks["estate_expert_client"].send_message_to_estate_search_expert.return_value = llm_response

        # __to_wewall_expert
        wewall_expert_response = "Wewall это..."
        mocks["estate_expert_client"].send_message_to_wewall_expert.return_value = wewall_expert_response

        keyboard_mock = MagicMock()
        mocks["wewall_expert_inline_keyboard_generator"].start.return_value = keyboard_mock

        # Act
        await estate_search_message_service.handler(message, state)

        # Assert
        mocks["estate_expert_client"].send_message_to_estate_search_expert.assert_awaited_once_with(
            message.chat.id,
            message.text
        )

        # __to_wewall_expert
        mocks["estate_expert_client"].delete_all_message.assert_awaited_once_with(message.chat.id)

        mocks["estate_expert_client"].send_message_to_wewall_expert.assert_awaited_once_with(
            message.chat.id,
            "Расскажи мне про WEWALL"
        )

        message.answer.assert_awaited_once_with(wewall_expert_response, reply_markup=keyboard_mock)

        mocks["state_repo"].change_status.assert_awaited_once_with(
            state.id,
            common.StateStatuses.wewall_expert
        )

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            message.chat.id,
            wewall_expert_response
        )

        tracer = estate_search_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "EstateSearchMessageService.handler"},
            {"name": "EstateSearchMessageService.__to_wewall_expert"},
        ])

    async def test_handler_to_wewall_expert_llm_response_err(
            self,
            mocks,
            estate_search_message_service,
    ):
        # Arrange
        message = utils.create_message("Хочу узнать про WEWALL")
        state = utils.create_state(common.StateStatuses.estate_search)

        llm_response = "Подключаю WEWALL. " + common.StateSwitchCommand.to_wewall_expert
        mocks["estate_expert_client"].send_message_to_estate_search_expert.return_value = llm_response

        err = Exception("Ошибка в __to_wewall_expert")
        mocks["estate_expert_client"].send_message_to_wewall_expert.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка в __to_wewall_expert"):
            await estate_search_message_service.handler(message, state)

        # Assert
        tracer = estate_search_message_service.tracer
        utils.assert_span_error(tracer, err, 2)

    async def test_handler_to_estate_expert_llm_response(
            self,
            mocks,
            estate_search_message_service,
    ):
        # Arrange
        message = utils.create_message("Хочу узнать новости рынка")
        state = utils.create_state(common.StateStatuses.estate_search)

        llm_response = "Подключаю аналитика рынка. " + common.StateSwitchCommand.to_estate_expert
        mocks["estate_expert_client"].send_message_to_estate_search_expert.return_value = llm_response

        # __to_estate_expert
        estate_expert_response = "Ны рынке сейчас..."
        mocks["estate_expert_client"].send_message_to_estate_expert.return_value = estate_expert_response

        # Act
        await estate_search_message_service.handler(message, state)

        # Assert
        mocks["estate_expert_client"].send_message_to_estate_search_expert.assert_awaited_once_with(
            message.chat.id,
            message.text
        )

        # __to_estate_expert
        mocks["estate_expert_client"].delete_all_message.assert_awaited_once_with(message.chat.id)

        mocks["estate_expert_client"].send_message_to_estate_expert.assert_awaited_once_with(
            message.chat.id,
            "Расскажи мне последнюю аналитику по недвижимости в Москве"
        )

        message.answer.assert_awaited_once_with(estate_expert_response)

        mocks["state_repo"].change_status.assert_awaited_once_with(
            state.id,
            common.StateStatuses.estate_expert
        )

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            message.chat.id,
            estate_expert_response
        )

        tracer = estate_search_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "EstateSearchMessageService.handler"},
            {"name": "EstateSearchMessageService.__to_estate_expert"},
        ])

    async def test_handler_to_estate_expert_llm_response_err(
            self,
            mocks,
            estate_search_message_service,
    ):
        # Arrange
        message = utils.create_message("Хочу узнать новости рынка")
        state = utils.create_state(common.StateStatuses.estate_search)

        llm_response = "Подключаю аналитика рынка. " + common.StateSwitchCommand.to_estate_expert
        mocks["estate_expert_client"].send_message_to_estate_search_expert.return_value = llm_response

        err = Exception("Ошибка в __to_estate_expert")
        mocks["estate_expert_client"].send_message_to_estate_expert.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка в __to_estate_expert"):
            await estate_search_message_service.handler(message, state)

        # Assert
        tracer = estate_search_message_service.tracer
        utils.assert_span_error(tracer, err, 2)

    async def test_handler_to_contact_collector_llm_response(
            self,
            mocks,
            estate_search_message_service,
    ):
        # Arrange
        message = utils.create_message("Собери мои данные")
        state = utils.create_state(common.StateStatuses.estate_search)

        llm_response = "Подключаю сборщика контактов. " + common.StateSwitchCommand.to_contact_collector
        mocks["estate_expert_client"].send_message_to_estate_search_expert.return_value = llm_response

        # __to_contact_collector
        contact_collector_response = "Пришлите ваш номер телефона."
        mocks["estate_expert_client"].send_message_to_contact_collector.return_value = contact_collector_response

        # Act
        await estate_search_message_service.handler(message, state)

        # Assert
        mocks["estate_expert_client"].send_message_to_estate_search_expert.assert_awaited_once_with(
            message.chat.id,
            message.text
        )

        # __to_contact_collector
        mocks["estate_expert_client"].delete_all_message.assert_not_awaited()

        mocks["estate_expert_client"].send_message_to_contact_collector.assert_awaited_once_with(
            message.chat.id,
            "Собери мои контактные данные и назначим время встречи",
        )

        message.answer.assert_awaited_once_with(contact_collector_response)

        mocks["state_repo"].change_status.assert_awaited_once_with(
            state.id,
            common.StateStatuses.contact_collector
        )

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            message.chat.id,
            contact_collector_response
        )

        tracer = estate_search_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "EstateSearchMessageService.handler"},
            {"name": "EstateSearchMessageService.__to_contact_collector"},
        ])

    async def test_handler_to_contact_collector_llm_response_err(
            self,
            mocks,
            estate_search_message_service,
    ):
        # Arrange
        message = utils.create_message("Собери мои данные")
        state = utils.create_state(common.StateStatuses.estate_search)

        llm_response = "Подключаю сборщика контактов. " + common.StateSwitchCommand.to_contact_collector
        mocks["estate_expert_client"].send_message_to_estate_search_expert.return_value = llm_response

        err = Exception("Ошибка в __to_contact_collector")
        mocks["estate_expert_client"].send_message_to_contact_collector.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка в __to_contact_collector"):
            await estate_search_message_service.handler(message, state)

        # Assert
        tracer = estate_search_message_service.tracer
        utils.assert_span_error(tracer, err, 2)

    async def test_handler_start_search_rent_offers_many_offer(
            self,
            mocks,
            estate_search_message_service,
    ):
        # Arrange
        message = utils.create_message("Да, параметры верные")
        state = utils.create_state(common.StateStatuses.estate_search, count_estate_search=0)
        estate_search_params = utils.estate_search_params("Аренда", "Офис")

        llm_response = f"Начинаю поиск {common.FinishStateCommand.start_estate_search}[{json.dumps(estate_search_params)}]"
        mocks["estate_expert_client"].send_message_to_estate_search_expert.return_value = llm_response

        # __search_rent_offers
        rent_offers = [utils.create_rent_offer("Офис"), utils.create_rent_offer("Офис")]
        rent_offers_result = MagicMock()
        rent_offers_result.rent_offers = rent_offers
        mocks["estate_search_client"].find_rent_offer.return_value = rent_offers_result

        keyboard_mock = AsyncMock()
        mocks["estate_search_inline_keyboard_generator"].middle_offer.return_value = keyboard_mock

        # __generate_offer_text
        offer_text = "Отличный ритейл для инвестиций..."
        mocks["llm_client"].generate.return_value = offer_text

        # Act
        await estate_search_message_service.handler(message, state)

        # Assert
        mocks["state_repo"].increment_estate_search_count.assert_awaited_once_with(state.id)

        # __search_rent_offers
        mocks["estate_search_client"].find_rent_offer.assert_awaited_once_with(
            estate_search_params["type"],
            estate_search_params["budget"],
            estate_search_params["location"],
            estate_search_params["square"],
            estate_search_params["floor"],
        )

        mocks["estate_search_state_repo"].create_estate_search_state.assert_awaited_once_with(
            state.id,
            rent_offers_result.rent_offers,
            estate_search_params
        )

        mocks["estate_expert_client"].add_message_to_chat.assert_awaited_once_with(
            state.tg_chat_id,
            ANY,
            "assistant"
        )

        mocks["estate_search_inline_keyboard_generator"].middle_offer.assert_awaited_once_with(0)
        mocks["estate_search_inline_keyboard_generator"].last_offer.assert_not_awaited()

        message.answer.assert_awaited_once_with(offer_text, reply_markup=keyboard_mock)
        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once()

    async def test_handler_start_search_rent_offers_not_offer(
            self,
            mocks,
            estate_search_message_service,
    ):
        # Arrange
        message = utils.create_message("Да, параметры верные")
        state = utils.create_state(common.StateStatuses.estate_search, count_estate_search=0)
        estate_search_params = utils.estate_search_params("Аренда", "Офис")

        llm_response = f"Начинаю поиск {common.FinishStateCommand.start_estate_search}[{json.dumps(estate_search_params)}]"
        mocks["estate_expert_client"].send_message_to_estate_search_expert.return_value = llm_response

        # __search_rent_offers
        rent_offers = []
        rent_offers_result = MagicMock()
        rent_offers_result.rent_offers = rent_offers
        mocks["estate_search_client"].find_rent_offer.return_value = rent_offers_result

        keyboard_mock = AsyncMock()
        mocks["estate_search_inline_keyboard_generator"].last_offer.return_value = keyboard_mock

        # __generate_offer_text
        offer_text = "Отличный ритейл для инвестиций..."
        mocks["llm_client"].generate.return_value = offer_text

        # Act
        await estate_search_message_service.handler(message, state)

        # Assert
        mocks["state_repo"].increment_estate_search_count.assert_awaited_once_with(state.id)

        # __search_rent_offers
        mocks["estate_search_client"].find_rent_offer.assert_awaited_once_with(
            estate_search_params["type"],
            estate_search_params["budget"],
            estate_search_params["location"],
            estate_search_params["square"],
            estate_search_params["floor"],
        )

        message.answer.assert_awaited_once_with(common.no_offers_text)

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            message.chat.id,
            common.no_offers_text
        )

        mocks["estate_search_state_repo"].create_estate_search_state.assert_not_awaited()

    async def test_handler_start_search_rent_offers_single_offer(
            self,
            mocks,
            estate_search_message_service,
    ):
        # Arrange
        message = utils.create_message("Да, параметры верные")
        state = utils.create_state(common.StateStatuses.estate_search, count_estate_search=0)
        estate_search_params = utils.estate_search_params("Аренда", "Офис")

        llm_response = f"Начинаю поиск {common.FinishStateCommand.start_estate_search}[{json.dumps(estate_search_params)}]"
        mocks["estate_expert_client"].send_message_to_estate_search_expert.return_value = llm_response

        # __search_rent_offers
        rent_offers = [utils.create_rent_offer("Офис")]
        rent_offers_result = MagicMock()
        rent_offers_result.rent_offers = rent_offers
        mocks["estate_search_client"].find_rent_offer.return_value = rent_offers_result

        keyboard_mock = AsyncMock()
        mocks["estate_search_inline_keyboard_generator"].last_offer.return_value = keyboard_mock

        # __generate_offer_text
        offer_text = "Отличный ритейл для инвестиций..."
        mocks["llm_client"].generate.return_value = offer_text

        # Act
        await estate_search_message_service.handler(message, state)

        # Assert
        mocks["state_repo"].increment_estate_search_count.assert_awaited_once_with(state.id)

        # __search_rent_offers
        mocks["estate_search_client"].find_rent_offer.assert_awaited_once_with(
            estate_search_params["type"],
            estate_search_params["budget"],
            estate_search_params["location"],
            estate_search_params["square"],
            estate_search_params["floor"],
        )

        mocks["estate_search_state_repo"].create_estate_search_state.assert_awaited_once_with(
            state.id,
            rent_offers_result.rent_offers,
            estate_search_params
        )

        mocks["estate_expert_client"].add_message_to_chat.assert_awaited_once_with(
            state.tg_chat_id,
            ANY,
            "assistant"
        )

        mocks["estate_search_inline_keyboard_generator"].last_offer.assert_awaited_once_with(0)
        mocks["estate_search_inline_keyboard_generator"].middle_offer.assert_not_awaited()

        message.answer.assert_awaited_once_with(offer_text, reply_markup=keyboard_mock)
        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            message.chat.id,
            offer_text
        )

    async def test_handler_start_search_sale_offers_office(
            self,
            mocks,
            estate_search_message_service,
    ):
        # Arrange
        message = utils.create_message("Да, параметры верные")
        state = utils.create_state(common.StateStatuses.estate_search, count_estate_search=0)
        estate_search_params = utils.estate_search_params("Покупка", "Офис")

        llm_response = f"Начинаю поиск {common.FinishStateCommand.start_estate_search}[{json.dumps(estate_search_params)}]"
        mocks["estate_expert_client"].send_message_to_estate_search_expert.return_value = llm_response

        # __search_sale_offers
        sale_offers = [utils.create_sale_offer("Офис"), utils.create_sale_offer("Офис")]
        sale_offers_result = MagicMock()
        sale_offers_result.sale_offers = sale_offers
        mocks["estate_search_client"].find_sale_offer.return_value = sale_offers_result

        # __calc_sale_office_finance_model
        calc_resp = utils.calc_resp()
        mocks["estate_calculator_client"].calc_finance_model_finished_office.return_value = calc_resp

        pdf_file_mock = MagicMock(spec=BufferedInputFile)
        mocks["estate_calculator_client"].generate_pdf.return_value = pdf_file_mock

        xlsx_file_mock = MagicMock(spec=BufferedInputFile)
        mocks["estate_calculator_client"].calc_finance_model_finished_office_table.return_value = xlsx_file_mock

        # __generate_offer_text
        offer_text = "Отличный ритейл для инвестиций..."
        mocks["llm_client"].generate.return_value = offer_text

        keyboard_mock = MagicMock()
        mocks["estate_search_inline_keyboard_generator"].middle_offer.return_value = keyboard_mock

        # Act
        await estate_search_message_service.handler(message, state)

        # Assert
        mocks["state_repo"].increment_estate_search_count.assert_awaited_once_with(state.id)

        # __search_sale_offers
        mocks["estate_search_client"].find_sale_offer.assert_awaited_once_with(
            estate_search_params["type"],
            estate_search_params["budget"],
            estate_search_params["location"],
            estate_search_params["square"],
            estate_search_params["floor"],
            estate_search_params["irr"],
        )

        mocks["estate_search_state_repo"].create_estate_search_state.assert_awaited_once_with(
            state.id,
            sale_offers_result.sale_offers,
            estate_search_params
        )

        # __calc_sale_office_finance_model
        mocks["estate_calculator_client"].calc_finance_model_finished_office.assert_awaited_once_with(
            sale_offers[0].sale_offer_square,
            sale_offers[0].sale_offer_price_per_meter,
            sale_offers[0].sale_offer_design,
            sale_offers[0].estate_category.replace("+", "").replace("C", "B"),
            ANY,
            ANY,
            estate_search_params["nds"]
        )

        mocks["estate_calculator_client"].calc_finance_model_finished_office_table.assert_awaited_once_with(
            sale_offers[0].sale_offer_square,
            sale_offers[0].sale_offer_price_per_meter,
            sale_offers[0].sale_offer_design,
            sale_offers[0].estate_category.replace("+", "").replace("C", "B"),
            ANY,
            ANY,
            estate_search_params["nds"]
        )

        mocks["estate_calculator_client"].generate_pdf.assert_awaited_once_with(
            common.FinishStateCommand.estate_calculator_finished_office,
            calc_resp.buying_property,
            calc_resp.sale_property,
            calc_resp.sale_tax,
            calc_resp.rent_tax,
            calc_resp.price_of_finishing,
            calc_resp.rent_flow,
            calc_resp.terminal_value,
            calc_resp.sale_income,
            calc_resp.rent_income,
            calc_resp.added_value,
            calc_resp.rent_irr,
            calc_resp.sale_irr,
        )

        mocks["estate_expert_client"].add_message_to_chat.assert_awaited_once_with(
            state.tg_chat_id,
            ANY,
            "assistant"
        )

        mocks["estate_search_inline_keyboard_generator"].middle_offer.assert_awaited_once_with(0)
        mocks["estate_search_inline_keyboard_generator"].last_offer.assert_not_awaited()

        message.answer.assert_awaited_once_with(offer_text, reply_markup=keyboard_mock)
        message.answer_media_group.assert_awaited_once()
        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once()

        tracer = estate_search_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "EstateSearchMessageService.handler"},
            {"name": "EstateSearchMessageService.__search_sale_offers"},
            {"name": "EstateSearchMessageService.__calc_sale_office_finance_model"},
            {"name": "EstateSearchMessageService.__nearest_metro"},
            {"name": "EstateSearchMessageService.__generate_offer_text"},
        ])

    async def test_handler_start_search_sale_offers_many_offers(
            self,
            mocks,
            estate_search_message_service,
    ):
        # Arrange
        message = utils.create_message("Да, параметры верные")
        state = utils.create_state(common.StateStatuses.estate_search, count_estate_search=0)
        estate_search_params = utils.estate_search_params("Покупка", "Ритейл")

        llm_response = f"Начинаю поиск {common.FinishStateCommand.start_estate_search}[{json.dumps(estate_search_params)}]"
        mocks["estate_expert_client"].send_message_to_estate_search_expert.return_value = llm_response

        # __search_sale_offers
        sale_offers = [utils.create_sale_offer("Ритейл"), utils.create_sale_offer("Ритейл")]
        sale_offers_result = MagicMock()
        sale_offers_result.sale_offers = sale_offers
        mocks["estate_search_client"].find_sale_offer.return_value = sale_offers_result

        # __calc_sale_retail_finance_model
        calc_resp = utils.calc_resp()
        mocks["estate_calculator_client"].calc_finance_model_finished_retail.return_value = calc_resp

        pdf_file_mock = MagicMock(spec=BufferedInputFile)
        mocks["estate_calculator_client"].generate_pdf.return_value = pdf_file_mock

        xlsx_file_mock = MagicMock(spec=BufferedInputFile)
        mocks["estate_calculator_client"].calc_finance_model_finished_retail_table.return_value = xlsx_file_mock

        # __generate_offer_text
        offer_text = "Отличный ритейл для инвестиций..."
        mocks["llm_client"].generate.return_value = offer_text

        keyboard_mock = MagicMock()
        mocks["estate_search_inline_keyboard_generator"].middle_offer.return_value = keyboard_mock

        # Act
        await estate_search_message_service.handler(message, state)

        # Assert
        mocks["state_repo"].increment_estate_search_count.assert_awaited_once_with(state.id)

        # __search_sale_offers
        mocks["estate_search_client"].find_sale_offer.assert_awaited_once_with(
            estate_search_params["type"],
            estate_search_params["budget"],
            estate_search_params["location"],
            estate_search_params["square"],
            estate_search_params["floor"],
            estate_search_params["irr"],
        )

        mocks["estate_search_state_repo"].create_estate_search_state.assert_awaited_once_with(
            state.id,
            sale_offers_result.sale_offers,
            estate_search_params
        )

        # __calc_sale_retail_finance_model
        mocks["estate_calculator_client"].calc_finance_model_finished_retail.assert_awaited_once_with(
            sale_offers[0].sale_offer_square,
            sale_offers[0].sale_offer_price_per_meter,
            estate_search_params["m_a_p"],
            estate_search_params["nds"],
            sale_offers[0].sale_offer_design
        )

        mocks["estate_calculator_client"].calc_finance_model_finished_retail_table.assert_awaited_once_with(
            sale_offers[0].sale_offer_square,
            sale_offers[0].sale_offer_price_per_meter,
            estate_search_params["m_a_p"],
            estate_search_params["nds"],
            sale_offers[0].sale_offer_design
        )

        mocks["estate_calculator_client"].generate_pdf.assert_awaited_once_with(
            common.FinishStateCommand.estate_calculator_finished_retail,
            calc_resp.buying_property,
            calc_resp.sale_property,
            calc_resp.sale_tax,
            calc_resp.rent_tax,
            calc_resp.price_of_finishing,
            calc_resp.rent_flow,
            calc_resp.terminal_value,
            calc_resp.sale_income,
            calc_resp.rent_income,
            calc_resp.added_value,
            calc_resp.rent_irr,
            calc_resp.sale_irr,
        )

        mocks["estate_expert_client"].add_message_to_chat.assert_awaited_once()

        mocks["estate_search_inline_keyboard_generator"].middle_offer.assert_awaited_once_with(0)
        mocks["estate_search_inline_keyboard_generator"].last_offer.assert_not_awaited()

        message.answer.assert_awaited_once_with(offer_text, reply_markup=keyboard_mock)
        message.answer_media_group.assert_awaited_once()
        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once()

        tracer = estate_search_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "EstateSearchMessageService.handler"},
            {"name": "EstateSearchMessageService.__search_sale_offers"},
            {"name": "EstateSearchMessageService.__calc_sale_retail_finance_model"},
            {"name": "EstateSearchMessageService.__generate_offer_text"}
        ])

    async def test_handler_start_search_sale_offers_single_offers(
            self,
            mocks,
            estate_search_message_service,
    ):
        # Arrange
        message = utils.create_message("Да, параметры верные")
        state = utils.create_state(common.StateStatuses.estate_search, count_estate_search=0)
        estate_search_params = utils.estate_search_params("Покупка", "Ритейл")

        llm_response = f"Начинаю поиск {common.FinishStateCommand.start_estate_search}[{json.dumps(estate_search_params)}]"
        mocks["estate_expert_client"].send_message_to_estate_search_expert.return_value = llm_response

        # __search_sale_offers
        sale_offers = [utils.create_sale_offer("Ритейл")]
        sale_offers_result = MagicMock()
        sale_offers_result.sale_offers = sale_offers
        mocks["estate_search_client"].find_sale_offer.return_value = sale_offers_result

        # __calc_sale_retail_finance_model
        calc_resp = utils.calc_resp()
        mocks["estate_calculator_client"].calc_finance_model_finished_retail.return_value = calc_resp

        pdf_file_mock = MagicMock(spec=BufferedInputFile)
        mocks["estate_calculator_client"].generate_pdf.return_value = pdf_file_mock

        xlsx_file_mock = MagicMock(spec=BufferedInputFile)
        mocks["estate_calculator_client"].calc_finance_model_finished_retail_table.return_value = xlsx_file_mock

        # __generate_offer_text
        offer_text = "Отличный ритейл для инвестиций..."
        mocks["llm_client"].generate.return_value = offer_text

        keyboard_mock = MagicMock()
        mocks["estate_search_inline_keyboard_generator"].last_offer.return_value = keyboard_mock

        # Act
        await estate_search_message_service.handler(message, state)

        # Assert
        mocks["state_repo"].increment_estate_search_count.assert_awaited_once_with(state.id)

        # __search_sale_offers
        mocks["estate_search_client"].find_sale_offer.assert_awaited_once_with(
            estate_search_params["type"],
            estate_search_params["budget"],
            estate_search_params["location"],
            estate_search_params["square"],
            estate_search_params["floor"],
            estate_search_params["irr"],
        )

        mocks["estate_search_state_repo"].create_estate_search_state.assert_awaited_once_with(
            state.id,
            sale_offers_result.sale_offers,
            estate_search_params
        )

        # __calc_sale_retail_finance_model
        mocks["estate_calculator_client"].calc_finance_model_finished_retail.assert_awaited_once_with(
            sale_offers[0].sale_offer_square,
            sale_offers[0].sale_offer_price_per_meter,
            estate_search_params["m_a_p"],
            estate_search_params["nds"],
            sale_offers[0].sale_offer_design
        )

        mocks["estate_calculator_client"].calc_finance_model_finished_retail_table.assert_awaited_once_with(
            sale_offers[0].sale_offer_square,
            sale_offers[0].sale_offer_price_per_meter,
            estate_search_params["m_a_p"],
            estate_search_params["nds"],
            sale_offers[0].sale_offer_design
        )

        mocks["estate_calculator_client"].generate_pdf.assert_awaited_once_with(
            common.FinishStateCommand.estate_calculator_finished_retail,
            calc_resp.buying_property,
            calc_resp.sale_property,
            calc_resp.sale_tax,
            calc_resp.rent_tax,
            calc_resp.price_of_finishing,
            calc_resp.rent_flow,
            calc_resp.terminal_value,
            calc_resp.sale_income,
            calc_resp.rent_income,
            calc_resp.added_value,
            calc_resp.rent_irr,
            calc_resp.sale_irr,
        )

        mocks["estate_expert_client"].add_message_to_chat.assert_awaited_once()

        mocks["estate_search_inline_keyboard_generator"].last_offer.assert_awaited_once_with(0)
        mocks["estate_search_inline_keyboard_generator"].middle_offer.assert_not_awaited()

        message.answer.assert_awaited_once_with(offer_text, reply_markup=keyboard_mock)
        message.answer_media_group.assert_awaited_once()
        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once()

        tracer = estate_search_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "EstateSearchMessageService.handler"},
            {"name": "EstateSearchMessageService.__search_sale_offers"},
            {"name": "EstateSearchMessageService.__calc_sale_retail_finance_model"},
            {"name": "EstateSearchMessageService.__generate_offer_text"}
        ])

    async def test_handler_start_search_sale_offer_not_offer(
            self,
            mocks,
            estate_search_message_service,
    ):
        # Arrange
        message = utils.create_message("Да, параметры верные")
        state = utils.create_state(common.StateStatuses.estate_search, count_estate_search=0)
        estate_search_params = utils.estate_search_params("Покупка", "Ритейл")

        llm_response = f"Начинаю поиск {common.FinishStateCommand.start_estate_search}[{json.dumps(estate_search_params)}]"
        mocks["estate_expert_client"].send_message_to_estate_search_expert.return_value = llm_response

        # __search_sale_offers
        sale_offers = []
        sale_offers_result = MagicMock()
        sale_offers_result.sale_offers = sale_offers
        mocks["estate_search_client"].find_sale_offer.return_value = sale_offers_result

        # Act
        await estate_search_message_service.handler(message, state)

        # Assert
        mocks["state_repo"].increment_estate_search_count.assert_awaited_once_with(state.id)

        # __search_sale_offers
        mocks["estate_search_client"].find_sale_offer.assert_awaited_once_with(
            estate_search_params["type"],
            estate_search_params["budget"],
            estate_search_params["location"],
            estate_search_params["square"],
            estate_search_params["floor"],
            estate_search_params["irr"],
        )

        message.answer.assert_awaited_once_with(common.no_offers_text)

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            message.chat.id,
            common.no_offers_text
        )

        mocks["estate_search_state_repo"].create_estate_search_state.assert_not_awaited()

        tracer = estate_search_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "EstateSearchMessageService.handler"},
            {"name": "EstateSearchMessageService.__search_sale_offers"}
        ])
