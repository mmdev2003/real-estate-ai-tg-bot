import json

from aiogram.types import Message
from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import model, interface, common


class EstateFinanceModelMessageService(interface.IEstateFinanceModelMessageService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            state_repo: interface.IStateRepo,
            estate_expert_client: interface.IWewallEstateExpertClient,
            estate_calculator_client: interface.IWewallEstateCalculatorClient,
            chat_client: interface.IWewallChatClient,
            wewall_expert_inline_keyboard_generator: interface.IWewallExpertInlineKeyboardGenerator,
            amocrm_main_pipeline_id: int,
            amocrm_appeal_pipeline_id: int,
            amocrm_pipeline_status_chat_with_manager: int,
            amocrm_pipeline_status_high_engagement: int,
            amocrm_pipeline_status_active_user: int,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()

        self.state_repo = state_repo
        self.estate_expert_client = estate_expert_client
        self.estate_calculator_client = estate_calculator_client
        self.chat_client = chat_client
        self.wewall_expert_inline_keyboard_generator = wewall_expert_inline_keyboard_generator
        self.amocrm_main_pipeline_id = amocrm_main_pipeline_id
        self.amocrm_appeal_pipeline_id = amocrm_appeal_pipeline_id
        self.amocrm_pipeline_status_chat_with_manager = amocrm_pipeline_status_chat_with_manager
        self.amocrm_pipeline_status_high_engagement = amocrm_pipeline_status_high_engagement
        self.amocrm_pipeline_status_active_user = amocrm_pipeline_status_active_user

    async def handler(self, message: Message, state: model.State):
        with self.tracer.start_as_current_span(
                "EstateFinanceModelMessageService.handler",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                llm_response = await self.estate_expert_client.send_message_to_estate_finance_model_expert(
                    message.chat.id,
                    message.text
                )

                if common.StateSwitchCommand.to_manager in llm_response:
                    self.logger.info("Получена команда перехода на менеджера")
                    await self.__to_manager(message, state)

                elif common.StateSwitchCommand.to_estate_expert in llm_response:
                    self.logger.info("Получена команда перехода на эксперт по недвижимости")
                    await self.__to_estate_expert(message, state)

                elif common.StateSwitchCommand.to_wewall_expert in llm_response:
                    self.logger.info("Получена команда перехода на эксперт по wewall")
                    await self.__to_wewall_expert(message, state)

                elif common.StateSwitchCommand.to_estate_search_expert in llm_response:
                    self.logger.info("Получена команда перехода на эксперт по поиску недвижимости")
                    await self.__to_estate_search_expert(message, state)

                else:
                    if common.FinishStateCommand.estate_calculator_finished_office in llm_response:
                        self.logger.info("Расчет построенного офиса")
                        await self.__calc_finished_office_finance_model(message, state, llm_response)

                    elif common.FinishStateCommand.estate_calculator_finished_retail in llm_response:
                        self.logger.info("Расчет построенного ритейла")
                        await self.__calc_finished_retail_finance_model(message, state, llm_response)

                    elif common.FinishStateCommand.estate_calculator_building_office in llm_response:
                        self.logger.info("Расчет строящегося офиса")
                        await self.__calc_building_office_finance_model(message, state, llm_response)

                    elif common.FinishStateCommand.estate_calculator_building_retail in llm_response:
                        self.logger.info("Расчет строящегося ритейла")
                        await self.__calc_building_retail_finance_model(message, state, llm_response)
                    else:
                        await message.answer(llm_response, parse_mode="HTML")
                        await self.chat_client.import_message_to_amocrm(message.chat.id, llm_response)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def __calc_finished_office_finance_model(self, message: Message, state: model.State, llm_response: str):
        with self.tracer.start_as_current_span(
                "EstateFinanceModelMessageService.__calc_finished_office_finance_model",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                calc_params = self.__extract_json_from_llm_response(llm_response)
                span.set_attribute("calc_params", str(calc_params))

                calculator_resp = await self.estate_calculator_client.calc_finance_model_finished_office(
                    calc_params["square"],
                    calc_params["price_per_meter"],
                    calc_params["need_repairs"],
                    calc_params["estate_category"],
                    calc_params["metro_station_name"],
                    calc_params["distance_to_metro"],
                    calc_params["nds_rate"],
                )

                pdf_file = await self.estate_calculator_client.generate_pdf(
                    common.FinishStateCommand.estate_calculator_finished_office,
                    calculator_resp.buying_property,
                    calculator_resp.sale_property,
                    calculator_resp.sale_tax,
                    calculator_resp.rent_tax,
                    calculator_resp.price_of_finishing,
                    calculator_resp.rent_flow,
                    calculator_resp.terminal_value,
                    calculator_resp.sale_income,
                    calculator_resp.rent_income,
                    calculator_resp.added_value,
                    calculator_resp.rent_irr,
                    calculator_resp.sale_irr,
                )

                xlsx_file = await self.estate_calculator_client.calc_finance_model_finished_office_table(
                    calc_params["square"],
                    calc_params["price_per_meter"],
                    calc_params["need_repairs"],
                    calc_params["estate_category"],
                    calc_params["metro_station_name"],
                    calc_params["distance_to_metro"],
                    calc_params["nds_rate"],
                )

                await self.__process_count_estate_calculator(state)

                await message.answer_document(xlsx_file)
                await message.answer_document(pdf_file)
                await self.chat_client.import_message_to_amocrm(message.chat.id, "Прислали параметры расчета")

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def __calc_finished_retail_finance_model(self, message: Message, state: model.State, llm_response: str):
        with self.tracer.start_as_current_span(
                "EstateFinanceModelMessageService.__calc_finished_retail_finance_model",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                calc_params = self.__extract_json_from_llm_response(llm_response)
                span.set_attribute("calc_params", str(calc_params))

                calculator_resp = await self.estate_calculator_client.calc_finance_model_finished_retail(
                    calc_params["square"],
                    calc_params["price_per_meter"],
                    calc_params["m_a_p"],
                    calc_params["nds_rate"],
                    calc_params["need_repairs"],
                )

                pdf_file = await self.estate_calculator_client.generate_pdf(
                    common.FinishStateCommand.estate_calculator_finished_retail,
                    calculator_resp.buying_property,
                    calculator_resp.sale_property,
                    calculator_resp.sale_tax,
                    calculator_resp.rent_tax,
                    calculator_resp.price_of_finishing,
                    calculator_resp.rent_flow,
                    calculator_resp.terminal_value,
                    calculator_resp.sale_income,
                    calculator_resp.rent_income,
                    calculator_resp.added_value,
                    calculator_resp.rent_irr,
                    calculator_resp.sale_irr,
                )

                xlsx_file = await self.estate_calculator_client.calc_finance_model_finished_retail_table(
                    calc_params["square"],
                    calc_params["price_per_meter"],
                    calc_params["m_a_p"],
                    calc_params["nds_rate"],
                    calc_params["need_repairs"],
                )

                await self.__process_count_estate_calculator(state)

                await message.answer_document(xlsx_file)
                await message.answer_document(pdf_file)
                await self.chat_client.import_message_to_amocrm(message.chat.id, "Прислали параметры расчета")

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def __calc_building_office_finance_model(self, message: Message, state: model.State, llm_response: str):
        with self.tracer.start_as_current_span(
                "EstateFinanceModelMessageService.__calc_building_office_finance_model",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                calc_params = self.__extract_json_from_llm_response(llm_response)
                span.set_attribute("calc_params", str(calc_params))

                calculator_resp = await self.estate_calculator_client.calc_finance_model_building_office(
                    calc_params["project_readiness"],
                    calc_params["square"],
                    calc_params["metro_station_name"],
                    calc_params["distance_to_metro"],
                    calc_params["estate_category"],
                    calc_params["price_per_meter"],
                    calc_params["nds_rate"],
                    calc_params["transaction_dict"],
                )

                pdf_file = await self.estate_calculator_client.generate_pdf(
                    common.FinishStateCommand.estate_calculator_building_office,
                    calculator_resp.buying_property,
                    calculator_resp.sale_property,
                    calculator_resp.sale_tax,
                    calculator_resp.rent_tax,
                    calculator_resp.price_of_finishing,
                    calculator_resp.rent_flow,
                    calculator_resp.terminal_value,
                    calculator_resp.sale_income,
                    calculator_resp.rent_income,
                    calculator_resp.added_value,
                    calculator_resp.rent_irr,
                    calculator_resp.sale_irr,
                )

                xlsx_file = await self.estate_calculator_client.calc_finance_model_building_office_table(
                    calc_params["project_readiness"],
                    calc_params["square"],
                    calc_params["metro_station_name"],
                    calc_params["distance_to_metro"],
                    calc_params["estate_category"],
                    calc_params["price_per_meter"],
                    calc_params["nds_rate"],
                    calc_params["transaction_dict"],
                )

                await self.__process_count_estate_calculator(state)

                await message.answer_document(xlsx_file)
                await message.answer_document(pdf_file)
                await self.chat_client.import_message_to_amocrm(message.chat.id, "Прислали параметры расчета")

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def __calc_building_retail_finance_model(self, message: Message, state: model.State, llm_response: str):
        with self.tracer.start_as_current_span(
                "EstateFinanceModelMessageService.__calc_building_retail_finance_model",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                calc_params = self.__extract_json_from_llm_response(llm_response)
                span.set_attribute("calc_params", str(calc_params))

                calculator_resp = await self.estate_calculator_client.calc_finance_model_building_retail(
                    calc_params["project_readiness"],
                    calc_params["square"],
                    calc_params["price_rva"],
                    calc_params["m_a_p"],
                    calc_params["price_per_meter"],
                    calc_params["nds_rate"],
                    calc_params["need_repairs"],
                    calc_params["transaction_dict"],
                )

                pdf_file = await self.estate_calculator_client.generate_pdf(
                    common.FinishStateCommand.estate_calculator_building_retail,
                    calculator_resp.buying_property,
                    calculator_resp.sale_property,
                    calculator_resp.sale_tax,
                    calculator_resp.rent_tax,
                    calculator_resp.price_of_finishing,
                    calculator_resp.rent_flow,
                    calculator_resp.terminal_value,
                    calculator_resp.sale_income,
                    calculator_resp.rent_income,
                    calculator_resp.added_value,
                    calculator_resp.rent_irr,
                    calculator_resp.sale_irr,
                )

                xlsx_file = await self.estate_calculator_client.calc_finance_model_building_retail_table(
                    calc_params["project_readiness"],
                    calc_params["square"],
                    calc_params["price_rva"],
                    calc_params["m_a_p"],
                    calc_params["price_per_meter"],
                    calc_params["nds_rate"],
                    calc_params["need_repairs"],
                    calc_params["transaction_dict"],
                )

                await self.__process_count_estate_calculator(state)

                await message.answer_document(xlsx_file)
                await message.answer_document(pdf_file)
                await self.chat_client.import_message_to_amocrm(message.chat.id, "Прислали параметры расчета")

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def __to_manager(self, message: Message, state: model.State):
        with self.tracer.start_as_current_span(
                "EstateFinanceModelMessageService.__to_manager",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                chat_summary = await self.estate_expert_client.summary(message.chat.id)
                await self.estate_expert_client.delete_all_message(message.chat.id)

                await message.answer(common.manger_is_connecting_text)

                await self.chat_client.edit_lead(message.chat.id, self.amocrm_appeal_pipeline_id, self.amocrm_pipeline_status_chat_with_manager)
                await self.state_repo.set_is_transferred_to_manager(state.id, True)

                await self.chat_client.import_message_to_amocrm(message.chat.id, chat_summary)
                await self.chat_client.import_message_to_amocrm(message.chat.id, common.manger_is_connecting_text)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def __to_estate_expert(self, message: Message, state: model.State):
        with self.tracer.start_as_current_span(
                "EstateFinanceModelMessageService.__to_estate_expert",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                await self.estate_expert_client.delete_all_message(message.chat.id)
                llm_response = await self.estate_expert_client.send_message_to_estate_expert(
                    message.chat.id,
                    "Расскажи мне последнюю аналитику по недвижимости в Москве"
                )
                await message.answer(llm_response)

                await self.state_repo.change_status(state.id, common.StateStatuses.estate_expert)
                await self.chat_client.import_message_to_amocrm(message.chat.id, llm_response)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def __to_wewall_expert(self, message: Message, state: model.State):
        with self.tracer.start_as_current_span(
                "EstateFinanceModelMessageService.__to_wewall_expert",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                await self.estate_expert_client.delete_all_message(message.chat.id)
                llm_response = await self.estate_expert_client.send_message_to_wewall_expert(
                    message.chat.id,
                    "Расскажи мне про WEWALL"
                )
                keyboard = await self.wewall_expert_inline_keyboard_generator.start()
                await message.answer(llm_response, reply_markup=keyboard)

                await self.state_repo.change_status(state.id, common.StateStatuses.wewall_expert)
                await self.chat_client.import_message_to_amocrm(message.chat.id, llm_response)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def __to_estate_search_expert(self, message: Message, state: model.State):
        with self.tracer.start_as_current_span(
                "EstateFinanceModelMessageService.__to_estate_search_expert",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                await self.estate_expert_client.delete_all_message(message.chat.id)

                llm_response = await self.estate_expert_client.send_message_to_estate_search_expert(
                    message.chat.id,
                    "Помоги мне подобрать недвижимость из вашего ассортимента"
                )

                await message.answer(llm_response)

                await self.state_repo.change_status(state.id, common.StateStatuses.estate_search)
                await self.chat_client.import_message_to_amocrm(message.chat.id, llm_response)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def __process_count_estate_calculator(self, state: model.State) -> None:
        await self.state_repo.increment_estate_calculator_count(state.id)
        self.logger.debug("Инкрементировали счетчик расчета доходности")

        if not state.is_transferred_to_manager:
            if state.count_estate_calculator == 2-1:
                self.logger.info("Счетчик расчета доходности сигнализирует о 'Высокой вовлеченности'")
                await self.chat_client.edit_lead(
                    state.tg_chat_id,
                    self.amocrm_main_pipeline_id,
                    self.amocrm_pipeline_status_high_engagement
                )
            elif state.count_estate_calculator == 7-1:
                self.logger.info("Счетчик сообщений сигнализирует о 'Активном пользователе'")
                await self.chat_client.edit_lead(
                    state.tg_chat_id,
                    self.amocrm_main_pipeline_id,
                    self.amocrm_pipeline_status_active_user
                )

    @staticmethod
    def __extract_json_from_llm_response(llm_response: str) -> dict:
        _, _, _json = llm_response.partition("[")
        _json, _, _ = _json.partition("]")
        _json = json.loads(_json)
        return _json
