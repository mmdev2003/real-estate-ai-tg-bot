import json
from unittest.mock import MagicMock, call

import pytest

from internal import common
from internal.service.estate_finance_model.message_service import EstateFinanceModelMessageService

from tests.unit import utils


class TestEstateFinanceModelMessageService:

    @pytest.fixture
    def estate_finance_model_message_service(self, mocks):
        return EstateFinanceModelMessageService(
            tel=mocks["tel"],
            state_repo=mocks["state_repo"],
            estate_expert_client=mocks["estate_expert_client"],
            estate_calculator_client=mocks["estate_calculator_client"],
            chat_client=mocks["chat_client"],
            wewall_expert_inline_keyboard_generator=mocks["wewall_expert_inline_keyboard_generator"],
            amocrm_main_pipeline_id=1234,
            amocrm_appeal_pipeline_id=5353,
        )

    async def test_handler_simple_llm_response(
            self,
            mocks,
            estate_finance_model_message_service,
    ):
        # Arrange
        message = utils.create_message("Расскажи как рассчитать доходность")
        state = utils.create_state(common.StateStatuses.estate_finance_model)

        llm_response = "Вот формула расчета доходности недвижимости..."
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.return_value = llm_response

        # Act
        await estate_finance_model_message_service.handler(message, state)

        # Assert
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.assert_awaited_once_with(
            message.chat.id,
            message.text
        )

        message.answer.assert_awaited_once_with(llm_response)

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            message.chat.id,
            llm_response
        )

        tracer = estate_finance_model_message_service.tracer
        utils.assert_span(tracer, [{"name": "EstateFinanceModelMessageService.handler"}])

    async def test_handler_simple_llm_response_err(
            self,
            mocks,
            estate_finance_model_message_service,
    ):
        # Arrange
        message = utils.create_message("Расскажи как рассчитать доходность")
        state = utils.create_state(common.StateStatuses.estate_finance_model)

        err = Exception("Finance model expert error")
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.side_effect = err

        # Act
        with pytest.raises(Exception, match="Finance model expert error"):
            await estate_finance_model_message_service.handler(message, state)

        # Assert
        tracer = estate_finance_model_message_service.tracer
        utils.assert_span_error(tracer, err, 1)

    async def test_handler_to_manager_llm_response(
            self,
            mocks,
            estate_finance_model_message_service,
    ):
        # Arrange
        message = utils.create_message("Хочу поговорить с менеджером")
        state = utils.create_state(common.StateStatuses.estate_finance_model)

        llm_response = "Подключаю менеджера. " + common.StateSwitchCommand.to_manager
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.return_value = llm_response

        # __to_manager
        chat_summary = "Клиент изучал финансовую модель и просит менеджера"
        mocks["estate_expert_client"].summary.return_value = chat_summary

        # Act
        await estate_finance_model_message_service.handler(message, state)

        # Assert
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.assert_awaited_once_with(
            message.chat.id,
            message.text
        )

        # __to_manager
        mocks["estate_expert_client"].summary.assert_awaited_once_with(message.chat.id)

        mocks["estate_expert_client"].delete_all_message.assert_awaited_once_with(message.chat.id)

        message.answer.assert_awaited_once_with(common.manger_is_connecting_text)

        mocks["chat_client"].edit_lead.assert_awaited_once_with(
            message.chat.id,
            estate_finance_model_message_service.amocrm_appeal_pipeline_id,
            common.AmocrmPipelineStatus.chat_with_manager
        )

        mocks["chat_client"].import_message_to_amocrm.assert_has_awaits([
            call(message.chat.id, chat_summary),
            call(message.chat.id, common.manger_is_connecting_text)
        ])

        tracer = estate_finance_model_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "EstateFinanceModelMessageService.handler"},
            {"name": "EstateFinanceModelMessageService.__to_manager"}
        ])

    async def test_handler_to_manager_err(
            self,
            mocks,
            estate_finance_model_message_service,
    ):
        # Arrange
        message = utils.create_message("Хочу поговорить с менеджером")
        state = utils.create_state(common.StateStatuses.estate_finance_model)

        llm_response = "Подключаю менеджера. " + common.StateSwitchCommand.to_manager
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.return_value = llm_response

        # __to_manager
        err = Exception("Ошибка в __to_manager")
        mocks["estate_expert_client"].summary.side_effect = err

        with pytest.raises(Exception, match="Ошибка в __to_manager"):
            await estate_finance_model_message_service.handler(message, state)

        # Assert
        tracer = estate_finance_model_message_service.tracer
        utils.assert_span_error(tracer, err, 2)


    async def test_handler_to_estate_expert_llm_response(
            self,
            mocks,
            estate_finance_model_message_service,
    ):
        # Arrange
        message = utils.create_message("Расскажи про рынок недвижимости")
        state = utils.create_state(common.StateStatuses.estate_finance_model)

        llm_response = "Переключаю на эксперта. " + common.StateSwitchCommand.to_estate_expert
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.return_value = llm_response

        # __to_estate_expert
        estate_expert_response = "Вот последняя аналитика по недвижимости..."
        mocks["estate_expert_client"].send_message_to_estate_expert.return_value = estate_expert_response

        # Act
        await estate_finance_model_message_service.handler(message, state)

        # Assert
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.assert_awaited_once_with(
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

        tracer = estate_finance_model_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "EstateFinanceModelMessageService.handler"},
            {"name": "EstateFinanceModelMessageService.__to_estate_expert"}
        ])

    async def test_handler_estate_expert_err(
            self,
            mocks,
            estate_finance_model_message_service,
    ):
        # Arrange
        message = utils.create_message("Расскажи про рынок недвижимости")
        state = utils.create_state(common.StateStatuses.estate_finance_model)

        llm_response = "Подключаю estate_expert. " + common.StateSwitchCommand.to_estate_expert
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.return_value = llm_response

        # __to_estate_expert
        err = Exception("Ошибка в __to_estate_expert")
        mocks["estate_expert_client"].send_message_to_estate_expert.side_effect = err

        with pytest.raises(Exception, match="Ошибка в __to_estate_expert"):
            await estate_finance_model_message_service.handler(message, state)

        # Assert
        tracer = estate_finance_model_message_service.tracer
        utils.assert_span_error(tracer, err, 2)

    async def test_handler_to_wewall_expert_llm_response(
            self,
            mocks,
            estate_finance_model_message_service,
    ):
        # Arrange
        message = utils.create_message("Расскажи про WEWALL")
        state = utils.create_state(common.StateStatuses.estate_finance_model)

        llm_response = "Переключаю на WEWALL. " + common.StateSwitchCommand.to_wewall_expert
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.return_value = llm_response

        # __to_wewall_expert
        wewall_expert_response = "Расскажу про WEWALL..."
        mocks["estate_expert_client"].send_message_to_wewall_expert.return_value = wewall_expert_response

        keyboard_mock = MagicMock()
        mocks["wewall_expert_inline_keyboard_generator"].start.return_value = keyboard_mock

        # Act
        await estate_finance_model_message_service.handler(message, state)

        # Assert
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.assert_awaited_once_with(
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

        tracer = estate_finance_model_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "EstateFinanceModelMessageService.handler"},
            {"name": "EstateFinanceModelMessageService.__to_wewall_expert"}
        ])

    async def test_handler_wewall_expert_err(
            self,
            mocks,
            estate_finance_model_message_service,
    ):
        # Arrange
        message = utils.create_message("Расскажи про WEWALL")
        state = utils.create_state(common.StateStatuses.estate_finance_model)

        llm_response = "Подключаю __to_wewall_expert. " + common.StateSwitchCommand.to_wewall_expert
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.return_value = llm_response

        # __to_wewall_expert
        err = Exception("Ошибка в __to_wewall_expert")
        mocks["estate_expert_client"].send_message_to_wewall_expert.side_effect = err

        with pytest.raises(Exception, match="Ошибка в __to_wewall_expert"):
            await estate_finance_model_message_service.handler(message, state)

        # Assert
        tracer = estate_finance_model_message_service.tracer
        utils.assert_span_error(tracer, err, 2)

    async def test_handler_to_estate_search_expert_llm_response(
            self,
            mocks,
            estate_finance_model_message_service,
    ):
        # Arrange
        message = utils.create_message("Помоги найти недвижимость")
        state = utils.create_state(common.StateStatuses.estate_finance_model)

        llm_response = "Переключаю на поиск. " + common.StateSwitchCommand.to_estate_search_expert
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.return_value = llm_response

        # __to_estate_search_expert
        search_expert_response = "Помогу подобрать недвижимость..."
        mocks["estate_expert_client"].send_message_to_estate_search_expert.return_value = search_expert_response

        # Act
        await estate_finance_model_message_service.handler(message, state)

        # Assert
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.assert_awaited_once_with(
            message.chat.id,
            message.text
        )

        # __to_estate_search_expert
        mocks["estate_expert_client"].delete_all_message.assert_awaited_once_with(message.chat.id)

        mocks["estate_expert_client"].send_message_to_estate_search_expert.assert_awaited_once_with(
            message.chat.id,
            "Помоги мне подобрать недвижимость из вашего ассортимента"
        )

        message.answer.assert_awaited_once_with(search_expert_response)

        mocks["state_repo"].change_status.assert_awaited_once_with(
            state.id,
            common.StateStatuses.estate_search
        )

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            message.chat.id,
            search_expert_response
        )

        tracer = estate_finance_model_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "EstateFinanceModelMessageService.handler"},
            {"name": "EstateFinanceModelMessageService.__to_estate_search_expert"}
        ])

    async def test_handler_estate_search_expert_err(
            self,
            mocks,
            estate_finance_model_message_service,
    ):
        # Arrange
        message = utils.create_message("Помоги найти недвижимость")
        state = utils.create_state(common.StateStatuses.estate_finance_model)

        llm_response = "Подключаю __estate_search_expert. " + common.StateSwitchCommand.to_estate_search_expert
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.return_value = llm_response

        # __estate_search_expert
        err = Exception("Ошибка в __estate_search_expert")
        mocks["estate_expert_client"].send_message_to_estate_search_expert.side_effect = err

        with pytest.raises(Exception, match="Ошибка в __estate_search_expert"):
            await estate_finance_model_message_service.handler(message, state)

        # Assert
        tracer = estate_finance_model_message_service.tracer
        utils.assert_span_error(tracer, err, 2)

    async def test_calc_finished_office_finance_model(
            self,
            mocks,
            estate_finance_model_message_service,
    ):
        # Arrange
        message = utils.create_message("Рассчитай офис")
        state = utils.create_state(common.StateStatuses.estate_finance_model, count_estate_calculator=0)
        calc_params = utils.calc_params_finished_office()

        llm_response = f"Рассчитываю офис {common.FinishStateCommand.estate_calculator_finished_office}[{json.dumps(calc_params)}]"
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.return_value = llm_response

        # __calc_finished_office_finance_model
        calc_resp = utils.calc_resp()
        mocks["estate_calculator_client"].calc_finance_model_finished_office.return_value = calc_resp

        pdf_file_mock = MagicMock()
        mocks["estate_calculator_client"].generate_pdf.return_value = pdf_file_mock

        xlsx_file_mock = MagicMock()
        mocks["estate_calculator_client"].calc_finance_model_finished_office_table.return_value = xlsx_file_mock

        # Act
        await estate_finance_model_message_service.handler(message, state)

        # Assert
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.assert_awaited_once_with(
            message.chat.id,
            message.text
        )

        # __calc_finished_office_finance_model
        mocks["estate_calculator_client"].calc_finance_model_finished_office.assert_awaited_once_with(
            calc_params["square"],
            calc_params["price_per_meter"],
            calc_params["need_repairs"],
            calc_params["estate_category"],
            calc_params["metro_station_name"],
            calc_params["distance_to_metro"],
            calc_params["nds_rate"]
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

        mocks["estate_calculator_client"].calc_finance_model_finished_office_table.assert_awaited_once_with(
            calc_params["square"],
            calc_params["price_per_meter"],
            calc_params["need_repairs"],
            calc_params["estate_category"],
            calc_params["metro_station_name"],
            calc_params["distance_to_metro"],
            calc_params["nds_rate"],
        )

        # __process_count_estate_calculator
        mocks["state_repo"].increment_estate_calculator_count.assert_awaited_once_with(state.id)

        mocks["chat_client"].edit_lead.assert_not_awaited()

        # __calc_finished_office_finance_model
        message.answer_document.assert_has_awaits([
            call(xlsx_file_mock),
            call(pdf_file_mock)
        ])

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            message.chat.id,
            "Прислали параметры расчета"
        )

        tracer = estate_finance_model_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "EstateFinanceModelMessageService.handler"},
            {"name": "EstateFinanceModelMessageService.__calc_finished_office_finance_model"}
        ])

    async def test_calc_finished_office_finance_model_high_engagement(
            self,
            mocks,
            estate_finance_model_message_service,
    ):
        # Arrange
        message = utils.create_message("Рассчитай офис")
        state = utils.create_state(common.StateStatuses.estate_finance_model, count_estate_calculator=1)
        calc_params = utils.calc_params_finished_office()

        llm_response = f"Рассчитываю офис {common.FinishStateCommand.estate_calculator_finished_office}[{json.dumps(calc_params)}]"
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.return_value = llm_response

        # Act
        await estate_finance_model_message_service.handler(message, state)

        # Assert
        # __calc_finished_office_finance_model
        # __process_count_estate_calculator
        mocks["state_repo"].increment_estate_calculator_count.assert_awaited_once_with(state.id)

        mocks["chat_client"].edit_lead.assert_awaited_once_with(
            state.tg_chat_id,
            estate_finance_model_message_service.amocrm_main_pipeline_id,
            common.AmocrmPipelineStatus.high_engagement
        )
        tracer = estate_finance_model_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "EstateFinanceModelMessageService.handler"},
            {"name": "EstateFinanceModelMessageService.__calc_finished_office_finance_model"}
        ])

    async def test_calc_finished_office_finance_model_err(
            self,
            mocks,
            estate_finance_model_message_service,
    ):
        # Arrange
        message = utils.create_message("Рассчитай офис")
        state = utils.create_state(common.StateStatuses.estate_finance_model, count_estate_calculator=1)
        calc_params = utils.calc_params_finished_office()

        llm_response = f"Рассчитываю офис {common.FinishStateCommand.estate_calculator_finished_office}[{json.dumps(calc_params)}]"
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.return_value = llm_response

        # __calc_finished_office_finance_model
        err = Exception("Ошибка в __calc_finance_model_finished_office")
        mocks["estate_calculator_client"].calc_finance_model_finished_office.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка в __calc_finance_model_finished_office"):
            await estate_finance_model_message_service.handler(message, state)

        # Assert
        tracer = estate_finance_model_message_service.tracer
        utils.assert_span_error(tracer, err, 2)


    async def test_calc_finished_retail_finance_model(
            self,
            mocks,
            estate_finance_model_message_service,
    ):
        # Arrange
        message = utils.create_message("Рассчитай ритейл")
        state = utils.create_state(common.StateStatuses.estate_finance_model, count_estate_calculator=0)
        calc_params = utils.calc_params_finished_retail()

        llm_response = f"Рассчитываю ритейл {common.FinishStateCommand.estate_calculator_finished_retail}[{json.dumps(calc_params)}]"
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.return_value = llm_response

        # __calc_finished_retail_finance_model
        calc_resp = utils.calc_resp()
        mocks["estate_calculator_client"].calc_finance_model_finished_retail.return_value = calc_resp

        pdf_file_mock = MagicMock()
        mocks["estate_calculator_client"].generate_pdf.return_value = pdf_file_mock

        xlsx_file_mock = MagicMock()
        mocks["estate_calculator_client"].calc_finance_model_finished_retail_table.return_value = xlsx_file_mock

        # Act
        await estate_finance_model_message_service.handler(message, state)

        # Assert
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.assert_awaited_once_with(
            message.chat.id,
            message.text
        )

        # __calc_finished_retail_finance_model
        mocks["estate_calculator_client"].calc_finance_model_finished_retail.assert_awaited_once_with(
            calc_params["square"],
            calc_params["price_per_meter"],
            calc_params["m_a_p"],
            calc_params["nds_rate"],
            calc_params["need_repairs"],
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

        mocks["estate_calculator_client"].calc_finance_model_finished_retail_table.assert_awaited_once_with(
            calc_params["square"],
            calc_params["price_per_meter"],
            calc_params["m_a_p"],
            calc_params["nds_rate"],
            calc_params["need_repairs"],
        )

        # __process_count_estate_calculator
        mocks["state_repo"].increment_estate_calculator_count.assert_awaited_once_with(state.id)

        mocks["chat_client"].edit_lead.assert_not_awaited()

        # __calc_finished_retail_finance_model
        message.answer_document.assert_has_awaits([
            call(xlsx_file_mock),
            call(pdf_file_mock)
        ])

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            message.chat.id,
            "Прислали параметры расчета"
        )

        tracer = estate_finance_model_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "EstateFinanceModelMessageService.handler"},
            {"name": "EstateFinanceModelMessageService.__calc_finished_retail_finance_model"}
        ])

    async def test_calc_finished_retail_finance_model_high_engagement(
            self,
            mocks,
            estate_finance_model_message_service,
    ):
        # Arrange
        message = utils.create_message("Рассчитай офис")
        state = utils.create_state(common.StateStatuses.estate_finance_model, count_estate_calculator=1)
        calc_params = utils.calc_params_finished_retail()

        llm_response = f"Рассчитываю офис {common.FinishStateCommand.estate_calculator_finished_retail}[{json.dumps(calc_params)}]"
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.return_value = llm_response

        # Act
        await estate_finance_model_message_service.handler(message, state)

        # Assert
        # __calc_finished_retail_finance_model
        # __process_count_estate_calculator
        mocks["state_repo"].increment_estate_calculator_count.assert_awaited_once_with(state.id)

        mocks["chat_client"].edit_lead.assert_awaited_once_with(
            state.tg_chat_id,
            estate_finance_model_message_service.amocrm_main_pipeline_id,
            common.AmocrmPipelineStatus.high_engagement
        )
        tracer = estate_finance_model_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "EstateFinanceModelMessageService.handler"},
            {"name": "EstateFinanceModelMessageService.__calc_finished_retail_finance_model"}
        ])

    async def test_calc_finished_retail_finance_model_err(
            self,
            mocks,
            estate_finance_model_message_service,
    ):
        # Arrange
        message = utils.create_message("Рассчитай офис")
        state = utils.create_state(common.StateStatuses.estate_finance_model, count_estate_calculator=1)
        calc_params = utils.calc_params_finished_retail()

        llm_response = f"Рассчитываю офис {common.FinishStateCommand.estate_calculator_finished_retail}[{json.dumps(calc_params)}]"
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.return_value = llm_response

        # __calc_finished_retail_finance_model
        err = Exception("Ошибка в __calc_finance_model_finished_retail")
        mocks["estate_calculator_client"].calc_finance_model_finished_retail.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка в __calc_finance_model_finished_retail"):
            await estate_finance_model_message_service.handler(message, state)

        # Assert
        tracer = estate_finance_model_message_service.tracer
        utils.assert_span_error(tracer, err, 2)

    async def test_calc_building_office_finance_model(
            self,
            mocks,
            estate_finance_model_message_service,
    ):
        # Arrange
        message = utils.create_message("Рассчитай строящийся офис")
        state = utils.create_state(common.StateStatuses.estate_finance_model, count_estate_calculator=0)
        calc_params = utils.calc_params_building_office()

        llm_response = f"Рассчитываю строящийся офис {common.FinishStateCommand.estate_calculator_building_office}[{json.dumps(calc_params)}]"
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.return_value = llm_response

        # __calc_building_office_finance_model
        calc_resp = utils.calc_resp()
        mocks["estate_calculator_client"].calc_finance_model_building_office.return_value = calc_resp

        pdf_file_mock = MagicMock()
        mocks["estate_calculator_client"].generate_pdf.return_value = pdf_file_mock

        xlsx_file_mock = MagicMock()
        mocks["estate_calculator_client"].calc_finance_model_building_office_table.return_value = xlsx_file_mock

        # Act
        await estate_finance_model_message_service.handler(message, state)

        # Assert
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.assert_awaited_once_with(
            message.chat.id,
            message.text
        )

        # __calc_building_office_finance_model
        mocks["estate_calculator_client"].calc_finance_model_building_office.assert_awaited_once_with(
            calc_params["project_readiness"],
            calc_params["square"],
            calc_params["metro_station_name"],
            calc_params["distance_to_metro"],
            calc_params["estate_category"],
            calc_params["price_per_meter"],
            calc_params["nds_rate"],
            calc_params["transaction_dict"],
        )

        mocks["estate_calculator_client"].generate_pdf.assert_awaited_once_with(
            common.FinishStateCommand.estate_calculator_building_office,
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

        mocks["estate_calculator_client"].calc_finance_model_building_office_table.assert_awaited_once_with(
            calc_params["project_readiness"],
            calc_params["square"],
            calc_params["metro_station_name"],
            calc_params["distance_to_metro"],
            calc_params["estate_category"],
            calc_params["price_per_meter"],
            calc_params["nds_rate"],
            calc_params["transaction_dict"],
        )

        # __process_count_estate_calculator
        mocks["state_repo"].increment_estate_calculator_count.assert_awaited_once_with(state.id)

        mocks["chat_client"].edit_lead.assert_not_awaited()

        # __calc_building_office_finance_model
        message.answer_document.assert_has_awaits([
            call(xlsx_file_mock),
            call(pdf_file_mock)
        ])

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            message.chat.id,
            "Прислали параметры расчета"
        )

        tracer = estate_finance_model_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "EstateFinanceModelMessageService.handler"},
            {"name": "EstateFinanceModelMessageService.__calc_building_office_finance_model"}
        ])

    async def test_calc_building_office_finance_model_high_engagement(
            self,
            mocks,
            estate_finance_model_message_service,
    ):
        # Arrange
        message = utils.create_message("Рассчитай строящийся офис")
        state = utils.create_state(common.StateStatuses.estate_finance_model, count_estate_calculator=1)
        calc_params = utils.calc_params_building_office()

        llm_response = f"Рассчитываю строящийся офис {common.FinishStateCommand.estate_calculator_building_office}[{json.dumps(calc_params)}]"
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.return_value = llm_response

        # Act
        await estate_finance_model_message_service.handler(message, state)

        # Assert
        # __calc_building_office_finance_model
        # __process_count_estate_calculator
        mocks["state_repo"].increment_estate_calculator_count.assert_awaited_once_with(state.id)

        mocks["chat_client"].edit_lead.assert_awaited_once_with(
            state.tg_chat_id,
            estate_finance_model_message_service.amocrm_main_pipeline_id,
            common.AmocrmPipelineStatus.high_engagement
        )
        tracer = estate_finance_model_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "EstateFinanceModelMessageService.handler"},
            {"name": "EstateFinanceModelMessageService.__calc_building_office_finance_model"}
        ])

    async def test_calc_building_office_finance_model_err(
            self,
            mocks,
            estate_finance_model_message_service,
    ):
        # Arrange
        message = utils.create_message("Рассчитай офис")
        state = utils.create_state(common.StateStatuses.estate_finance_model, count_estate_calculator=1)
        calc_params = utils.calc_params_building_office()

        llm_response = f"Рассчитываю офис {common.FinishStateCommand.estate_calculator_building_office}[{json.dumps(calc_params)}]"
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.return_value = llm_response

        # __calc_building_office_finance_model
        err = Exception("Ошибка в __calc_finance_model_building_office")
        mocks["estate_calculator_client"].calc_finance_model_building_office.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка в __calc_finance_model_building_office"):
            await estate_finance_model_message_service.handler(message, state)

        # Assert
        tracer = estate_finance_model_message_service.tracer
        utils.assert_span_error(tracer, err, 2)

    async def test_calc_building_retail_finance_model(
            self,
            mocks,
            estate_finance_model_message_service,
    ):
        # Arrange
        message = utils.create_message("Рассчитай строящийся ритейл")
        state = utils.create_state(common.StateStatuses.estate_finance_model, count_estate_calculator=0)
        calc_params = utils.calc_params_building_retail()

        llm_response = f"Рассчитываю строящийся ритейл {common.FinishStateCommand.estate_calculator_building_retail}[{json.dumps(calc_params)}]"
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.return_value = llm_response

        # __calc_building_retail_finance_model
        calc_resp = utils.calc_resp()
        mocks["estate_calculator_client"].calc_finance_model_building_retail.return_value = calc_resp

        pdf_file_mock = MagicMock()
        mocks["estate_calculator_client"].generate_pdf.return_value = pdf_file_mock

        xlsx_file_mock = MagicMock()
        mocks["estate_calculator_client"].calc_finance_model_building_retail_table.return_value = xlsx_file_mock

        # Act
        await estate_finance_model_message_service.handler(message, state)

        # Assert
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.assert_awaited_once_with(
            message.chat.id,
            message.text
        )

        # __calc_building_retail_finance_model
        mocks["estate_calculator_client"].calc_finance_model_building_retail.assert_awaited_once_with(
            calc_params["project_readiness"],
            calc_params["square"],
            calc_params["price_rva"],
            calc_params["m_a_p"],
            calc_params["price_per_meter"],
            calc_params["nds_rate"],
            calc_params["need_repairs"],
            calc_params["transaction_dict"],
        )

        mocks["estate_calculator_client"].generate_pdf.assert_awaited_once_with(
            common.FinishStateCommand.estate_calculator_building_retail,
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

        mocks["estate_calculator_client"].calc_finance_model_building_retail_table.assert_awaited_once_with(
            calc_params["project_readiness"],
            calc_params["square"],
            calc_params["price_rva"],
            calc_params["m_a_p"],
            calc_params["price_per_meter"],
            calc_params["nds_rate"],
            calc_params["need_repairs"],
            calc_params["transaction_dict"],
        )

        # __process_count_estate_calculator
        mocks["state_repo"].increment_estate_calculator_count.assert_awaited_once_with(state.id)

        mocks["chat_client"].edit_lead.assert_not_awaited()

        # __calc_building_retail_finance_model
        message.answer_document.assert_has_awaits([
            call(xlsx_file_mock),
            call(pdf_file_mock)
        ])

        mocks["chat_client"].import_message_to_amocrm.assert_awaited_once_with(
            message.chat.id,
            "Прислали параметры расчета"
        )

        tracer = estate_finance_model_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "EstateFinanceModelMessageService.handler"},
            {"name": "EstateFinanceModelMessageService.__calc_building_retail_finance_model"}
        ])

    async def test_calc_building_retail_finance_model_high_engagement(
            self,
            mocks,
            estate_finance_model_message_service,
    ):
        # Arrange
        message = utils.create_message("Рассчитай строящийся ритейл")
        state = utils.create_state(common.StateStatuses.estate_finance_model, count_estate_calculator=1)
        calc_params = utils.calc_params_building_retail()

        llm_response = f"Рассчитываю строящийся ритейл {common.FinishStateCommand.estate_calculator_building_retail}[{json.dumps(calc_params)}]"
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.return_value = llm_response

        # Act
        await estate_finance_model_message_service.handler(message, state)

        # Assert
        # __calc_building_retail_finance_model
        # __process_count_estate_calculator
        mocks["state_repo"].increment_estate_calculator_count.assert_awaited_once_with(state.id)

        mocks["chat_client"].edit_lead.assert_awaited_once_with(
            state.tg_chat_id,
            estate_finance_model_message_service.amocrm_main_pipeline_id,
            common.AmocrmPipelineStatus.high_engagement
        )
        tracer = estate_finance_model_message_service.tracer
        utils.assert_span(tracer, [
            {"name": "EstateFinanceModelMessageService.handler"},
            {"name": "EstateFinanceModelMessageService.__calc_building_retail_finance_model"}
        ])

    async def test_calc_building_retail_finance_model_err(
            self,
            mocks,
            estate_finance_model_message_service,
    ):
        # Arrange
        message = utils.create_message("Рассчитай офис")
        state = utils.create_state(common.StateStatuses.estate_finance_model, count_estate_calculator=1)
        calc_params = utils.calc_params_building_retail()

        llm_response = f"Рассчитываю офис {common.FinishStateCommand.estate_calculator_building_retail}[{json.dumps(calc_params)}]"
        mocks["estate_expert_client"].send_message_to_estate_finance_model_expert.return_value = llm_response

        # __calc_building_retail_finance_model
        err = Exception("Ошибка в __calc_finance_model_building_retail")
        mocks["estate_calculator_client"].calc_finance_model_building_retail.side_effect = err

        # Act
        with pytest.raises(Exception, match="Ошибка в __calc_finance_model_building_retail"):
            await estate_finance_model_message_service.handler(message, state)

        # Assert
        tracer = estate_finance_model_message_service.tracer
        utils.assert_span_error(tracer, err, 2)



