import json
from aiogram.types import Message, InputMediaDocument, InputMediaPhoto, InlineKeyboardMarkup
from opentelemetry.trace import StatusCode, SpanKind

from internal import model, interface, common


class EstateSearchMessageService(interface.IEstateSearchMessageService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            state_repo: interface.IStateRepo,
            estate_search_state_repo: interface.IEstateSearchStateRepo,
            chat_client: interface.IWewallChatClient,
            estate_expert_client: interface.IWewallEstateExpertClient,
            estate_search_client: interface.IWewallEstateSearchClient,
            estate_calculator_client: interface.IWewallEstateCalculatorClient,
            estate_search_inline_keyboard_generator: interface.IEstateSearchInlineKeyboardGenerator,
            wewall_expert_inline_keyboard_generator: interface.IWewallExpertInlineKeyboardGenerator,
            llm_client: interface.ILLMClient,
            amocrm_main_pipeline_id: int,
            amocrm_appeal_pipeline_id: int,
            amocrm_pipeline_status_chat_with_manager: int,
            amocrm_pipeline_status_high_engagement: int,
            amocrm_pipeline_status_active_user: int,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()

        self.state_repo = state_repo
        self.estate_search_state_repo = estate_search_state_repo
        self.chat_client = chat_client
        self.estate_expert_client = estate_expert_client
        self.estate_search_client = estate_search_client
        self.estate_calculator_client = estate_calculator_client
        self.estate_search_inline_keyboard_generator = estate_search_inline_keyboard_generator
        self.wewall_expert_inline_keyboard_generator = wewall_expert_inline_keyboard_generator
        self.llm_client = llm_client
        self.amocrm_main_pipeline_id = amocrm_main_pipeline_id
        self.amocrm_appeal_pipeline_id = amocrm_appeal_pipeline_id
        self.amocrm_pipeline_status_chat_with_manager = amocrm_pipeline_status_chat_with_manager
        self.amocrm_pipeline_status_high_engagement = amocrm_pipeline_status_high_engagement
        self.amocrm_pipeline_status_active_user = amocrm_pipeline_status_active_user

    async def handler(self, message: Message, state: model.State):
        with self.tracer.start_as_current_span(
                "EstateSearchMessageService.handler",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                llm_response = await self.estate_expert_client.send_message_to_estate_search_expert(
                    message.chat.id,
                    message.text
                )

                if common.StateSwitchCommand.to_manager in llm_response:
                    self.logger.info("Получена команда перехода на менеджера")
                    await self.__to_manager(message, state)

                elif common.StateSwitchCommand.to_estate_finance_model_expert in llm_response:
                    self.logger.info("Получена команда переключения на расчет доходности недвижимости")
                    await self.__to_estate_finance_model(message, state)

                elif common.StateSwitchCommand.to_wewall_expert in llm_response:
                    self.logger.info("Получена команда перехода на эксперт по wewall")
                    await self.__to_wewall_expert(message, state)

                elif common.StateSwitchCommand.to_estate_expert in llm_response:
                    self.logger.info("Получена команда перехода на эксперт по недвижимости")
                    await self.__to_estate_expert(message, state)

                elif common.StateSwitchCommand.to_contact_collector in llm_response:
                    self.logger.info("Получена команда перехода на сбор контактных данных")
                    await self.__to_contact_collector(message, state)

                else:
                    if common.FinishStateCommand.start_estate_search in llm_response:
                        self.logger.info("Получена команда начала поиска недвижимости")
                        await self.__process_count_estate_search(state)

                        estate_search_params = self.__extract_json_from_llm_response(llm_response)
                        await self.estate_search_state_repo.delete_estate_search_state_by_state_id(state.id)

                        if estate_search_params["strategy"] == 2:
                            self.logger.debug("Ищем оффер на аренду")
                            await self.__search_rent_offers(message, state, estate_search_params)
                        else:
                            self.logger.debug("Ищем оффер на продажу")
                            await self.__search_sale_offers(message, state, estate_search_params)

                    elif common.FinishStateCommand.next_offer_estate_search in llm_response:
                        self.logger.info("Получена команда перехода к следующему офферу")
                        await self.__next_offer(message, state)

                    else:
                        await message.answer(llm_response, parse_mode="HTML")
                        await self.chat_client.import_message_to_amocrm(message.chat.id, llm_response)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def __next_offer(self, message: Message, state: model.State):
        with self.tracer.start_as_current_span(
                "EstateSearchMessageService.__next_offer",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                await self.estate_expert_client.add_message_to_chat(state.tg_chat_id, "Следующее помещение", "user")

                state_estate_search = (await self.estate_search_state_repo.estate_search_state_by_state_id(state.id))[0]
                current_offer_id = state_estate_search.current_offer_id + 1
                await self.estate_search_state_repo.change_current_offer_by_state_id(state.id, current_offer_id)

                span.set_attribute("current_offer_id", current_offer_id)

                if current_offer_id >= len(state_estate_search.offers):
                    self.logger.info("Помещений больше нет")
                    await message.answer(common.no_more_offers)
                    await self.chat_client.import_message_to_amocrm(message.chat.id, common.no_more_offers)

                    return

                offer = state_estate_search.offers[current_offer_id]

                document_media_group = None
                calc_resp = None
                if state_estate_search.estate_search_params["motivation"] == 1:
                    self.logger.debug("Показываем оффер на продажу офиса")
                    if offer.offer_readiness == 1:
                        self.logger.info("Расчет доходности готового офиса")
                        document_media_group, calc_resp = await self.__calc_sale_finished_office_finance_model(
                            offer
                        )
                    else:
                        self.logger.info("Расчет доходности офиса на стадии строительства")
                        document_media_group, calc_resp = await self.__calc_sale_building_office_finance_model(
                            offer
                        )

                offer_text, offer_text_with_link = await self.__generate_offer_text(offer, calc_resp)
                await self.estate_expert_client.add_message_to_chat(state.tg_chat_id, offer_text_with_link, "assistant")

                if current_offer_id == len(state_estate_search.offers) - 1:
                    self.logger.debug("Показываем кнопку с оффером на последнем помещении")
                    keyboard = await self.estate_search_inline_keyboard_generator.last_offer(current_offer_id)
                else:
                    keyboard = await self.estate_search_inline_keyboard_generator.middle_offer(current_offer_id)

                photo_media_group = [
                    InputMediaPhoto(media=image_url)
                    for image_url in offer.image_urls
                ]
                if photo_media_group:
                    await message.answer_media_group(photo_media_group[:10])
                else:
                    self.logger.debug("Нет фотографий этого помещения")
                    await message.answer("Нет фотографий этого помещения")

                await message.answer(offer_text, reply_markup=keyboard)
                if document_media_group is not None:
                    await message.answer_media_group(document_media_group)
                await self.chat_client.import_message_to_amocrm(message.chat.id, offer_text)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def __search_rent_offers(self, message: Message, state: model.State, estate_search_params: dict):
        with self.tracer.start_as_current_span(
                "EstateSearchMessageService.__search_rent_offers",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                rent_offers_result = await self.estate_search_client.find_rent_offer(
                    estate_search_params["type"],
                    estate_search_params["budget"],
                    estate_search_params["location"],
                    estate_search_params["square"],
                    estate_search_params["estate_class"],
                    estate_search_params["distance_to_metro"],
                    estate_search_params["design"],
                    estate_search_params["readiness"],
                    estate_search_params["irr"],
                )

                if not rent_offers_result.rent_offers:
                    self.logger.info("Нет подходящих помещений")
                    await message.answer(common.no_offers_text)
                    await self.chat_client.import_message_to_amocrm(message.chat.id, common.no_offers_text)

                    llm_response = await self.estate_expert_client.send_message_to_estate_search_expert(
                        message.chat.id,
                        common.compromise_no_offers_text
                    )
                    await message.answer(llm_response)
                    await self.chat_client.import_message_to_amocrm(message.chat.id, llm_response)

                    span.set_status(StatusCode.OK)
                    return

                await self.estate_search_state_repo.create_estate_search_state(
                    state.id,
                    rent_offers_result.rent_offers,
                    estate_search_params
                )
                rent_offer = rent_offers_result.rent_offers[0]

                rent_offer_text, rent_offer_text_with_link = await self.__generate_offer_text(rent_offer, None)
                await self.estate_expert_client.add_message_to_chat(state.tg_chat_id, rent_offer_text_with_link,
                                                                    "assistant")

                photo_media_group = [
                    InputMediaPhoto(media=image_url)
                    for image_url in rent_offer.image_urls
                ]

                try:
                    await message.answer_media_group(photo_media_group[:10])
                except Exception:
                    self.logger.debug("Нет фотографий этого помещения")
                    await message.answer("Нет фотографий этого помещения")

                state_estate_search = (await self.estate_search_state_repo.estate_search_state_by_state_id(state.id))[0]
                keyboard = await self.__generate_offer_keyboard(state_estate_search)

                await message.answer(rent_offer_text, reply_markup=keyboard)
                await self.chat_client.import_message_to_amocrm(message.chat.id, rent_offer_text)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def __search_sale_offers(self, message: Message, state: model.State, estate_search_params: dict):
        with self.tracer.start_as_current_span(
                "EstateSearchMessageService.__search_sale_offers",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                sale_offers_result = await self.estate_search_client.find_sale_offer(
                    estate_search_params["type"],
                    estate_search_params["budget"],
                    estate_search_params["location"],
                    estate_search_params["square"],
                    estate_search_params["estate_class"],
                    estate_search_params["distance_to_metro"],
                    estate_search_params["design"],
                    estate_search_params["readiness"],
                    estate_search_params["irr"],
                )

                if not sale_offers_result.sale_offers:
                    self.logger.info("Нет подходящих помещений")
                    await message.answer(common.no_offers_text)
                    await self.chat_client.import_message_to_amocrm(message.chat.id, common.no_offers_text)

                    llm_response = await self.estate_expert_client.send_message_to_estate_search_expert(
                        message.chat.id,
                        common.compromise_no_offers_text
                    )
                    await message.answer(llm_response)
                    await self.chat_client.import_message_to_amocrm(message.chat.id, llm_response)

                    span.set_status(StatusCode.OK)
                    return

                await self.estate_search_state_repo.create_estate_search_state(
                    state.id,
                    sale_offers_result.sale_offers,
                    estate_search_params
                )
                sale_offer = sale_offers_result.sale_offers[0]

                if estate_search_params["motivation"] == 1 and estate_search_params["type"] == 1:
                    if estate_search_params["readiness"] == 1:
                        self.logger.info("Расчет доходности готового офиса")
                        document_media_group, calc_resp = await self.__calc_sale_finished_office_finance_model(
                            sale_offer
                        )
                    else:
                        self.logger.info("Расчет доходности офиса на стадии строительства")
                        document_media_group, calc_resp = await self.__calc_sale_building_office_finance_model(
                            sale_offer
                        )
                else:
                    calc_resp = None
                    document_media_group = None

                sale_offer_text, sale_offer_text_with_link = await self.__generate_offer_text(sale_offer, calc_resp)
                await self.estate_expert_client.add_message_to_chat(state.tg_chat_id, sale_offer_text_with_link,
                                                                    "assistant")

                photo_media_group = [
                    InputMediaPhoto(media=image_url)
                    for image_url in sale_offer.image_urls
                ]

                try:
                    await message.answer_media_group(photo_media_group[:10])
                except Exception:
                    self.logger.debug("Нет фотографий этого помещения")
                    await message.answer("Нет фотографий этого помещения")

                state_estate_search = (await self.estate_search_state_repo.estate_search_state_by_state_id(state.id))[0]
                keyboard = await self.__generate_offer_keyboard(state_estate_search)
                await message.answer(sale_offer_text, reply_markup=keyboard)
                await self.chat_client.import_message_to_amocrm(message.chat.id, sale_offer_text)

                if document_media_group is not None:
                    await message.answer_media_group(media=document_media_group)
                    await self.chat_client.import_message_to_amocrm(message.chat.id, "Расчет доходности недвижимости")

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def __generate_offer_keyboard(self, state_estate_search: model.EstateSearchState) -> InlineKeyboardMarkup:
        with self.tracer.start_as_current_span(
                "EstateSearchMessageService.__generate_offer_keyboard",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                if state_estate_search.current_offer_id == len(state_estate_search.offers) - 1:
                    self.logger.debug("Показываем кнопку с оффером на последнем помещении")
                    keyboard = await self.estate_search_inline_keyboard_generator.last_offer(state_estate_search.current_offer_id)
                elif state_estate_search.current_estate_id >= len({offer.estate_id for offer in state_estate_search.offers}) - 1:
                    self.logger.debug("Показываем кнопку с оффером на последнем здании")
                    keyboard = await self.estate_search_inline_keyboard_generator.last_estate(state_estate_search.current_offer_id)
                else:
                    keyboard = await self.estate_search_inline_keyboard_generator.middle_offer(state_estate_search.current_offer_id)

                span.set_status(StatusCode.OK)
                return keyboard
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err
    async def __calc_sale_finished_office_finance_model(
            self,
            sale_offer: model.SaleOffer,
    ) -> tuple[list[InputMediaDocument], model.FinanceModelResponse]:
        with self.tracer.start_as_current_span(
                "EstateSearchMessageService.__calc_sale_finished_office_finance_model",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                nearest_metro = self.__nearest_metro(sale_offer.metro_stations)

                calculator_resp = await self.estate_calculator_client.calc_finance_model_finished_office(
                    sale_offer.square,
                    sale_offer.price_per_meter,
                    sale_offer.design,
                    sale_offer.estate_category.replace("+", "").replace("C", "B"),
                    nearest_metro.name,
                    nearest_metro.leg_distance,
                    0,
                )

                calc_xlsx = await self.estate_calculator_client.calc_finance_model_finished_office_table(
                    sale_offer.square,
                    sale_offer.price_per_meter,
                    sale_offer.design,
                    sale_offer.estate_category.replace("+", "").replace("C", "B"),
                    nearest_metro.name,
                    nearest_metro.leg_distance,
                    0,
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

                document_media_group = [InputMediaDocument(media=pdf_file), InputMediaDocument(media=calc_xlsx)]

                span.set_status(StatusCode.OK)
                return document_media_group, calculator_resp
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def __calc_sale_building_office_finance_model(
            self,
            sale_offer: model.SaleOffer
    ) -> tuple[list[InputMediaDocument], model.FinanceModelResponse]:
        with self.tracer.start_as_current_span(
                "EstateSearchMessageService.__calc_sale_finished_office_finance_model",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                nearest_metro = self.__nearest_metro(sale_offer.metro_stations)

                calculator_resp = await self.estate_calculator_client.calc_finance_model_building_office(
                    sale_offer.readiness_date,
                    sale_offer.square,
                    nearest_metro.name,
                    nearest_metro.leg_distance,
                    sale_offer.estate_category,
                    sale_offer.price_per_meter,
                    0,
                    {"1Q2025": 100}
                )

                calc_xlsx = await self.estate_calculator_client.calc_finance_model_building_office_table(
                    sale_offer.readiness_date,
                    sale_offer.square,
                    nearest_metro.name,
                    nearest_metro.leg_distance,
                    sale_offer.estate_category,
                    sale_offer.price_per_meter,
                    0,
                    {"1Q2025": 100}
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

                document_media_group = [InputMediaDocument(media=pdf_file), InputMediaDocument(media=calc_xlsx)]

                span.set_status(StatusCode.OK)
                return document_media_group, calculator_resp
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def __to_manager(self, message: Message, state: model.State):
        with self.tracer.start_as_current_span(
                "EstateSearchMessageService.__to_manager",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                chat_summary = await self.estate_expert_client.summary(message.chat.id)
                await self.estate_expert_client.delete_all_message(message.chat.id)

                await message.answer(common.manger_is_connecting_text)

                await self.chat_client.edit_lead(message.chat.id, self.amocrm_appeal_pipeline_id,
                                                 self.amocrm_pipeline_status_chat_with_manager)
                await self.state_repo.set_is_transferred_to_manager(state.id, True)

                await self.chat_client.import_message_to_amocrm(message.chat.id, chat_summary)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def __to_estate_finance_model(self, message: Message, state: model.State):
        with self.tracer.start_as_current_span(
                "EstateSearchMessageService.__to_estate_finance_model",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                await self.estate_expert_client.delete_all_message(message.chat.id)
                llm_response = await self.estate_expert_client.send_message_to_estate_finance_model_expert(
                    message.chat.id,
                    "Помоги, мне рассчитать доходность недвижимости"
                )
                await message.answer(llm_response)

                await self.state_repo.change_status(state.id, common.StateStatuses.estate_finance_model)
                await self.chat_client.import_message_to_amocrm(message.chat.id, llm_response)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def __to_wewall_expert(self, message: Message, state: model.State):
        with self.tracer.start_as_current_span(
                "EstateSearchMessageService.__to_wewall_expert",
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

    async def __to_estate_expert(self, message: Message, state: model.State):
        with self.tracer.start_as_current_span(
                "EstateSearchMessageService.__to_estate_expert",
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

    async def __to_contact_collector(self, message: Message, state: model.State):
        with self.tracer.start_as_current_span(
                "EstateSearchMessageService.__to_contact_collector",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                llm_response = await self.estate_expert_client.send_message_to_contact_collector(
                    message.chat.id,
                    "Собери мои контактные данные и назначим время встречи",
                )

                await message.answer(llm_response)

                await self.state_repo.change_status(state.id, common.StateStatuses.contact_collector)
                await self.chat_client.import_message_to_amocrm(message.chat.id, llm_response)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def __generate_offer_text(
            self,
            offer: model.SaleOffer | model.RentOffer,
            calc_resp: model.FinanceModelResponse | None
    ) -> tuple[str, str]:
        with self.tracer.start_as_current_span(
                "EstateSearchMessageService.__generate_offer_text",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                if calc_resp is not None:
                    calc_resp_text = f"""
                           "А это расчет финансовой модели для этого объекта\n\n"
                               {calc_resp.rent_irr} - IRR аренды\n
                               {calc_resp.rent_flow} - Выручка аренды в млн/руб\n
                               {calc_resp.price_of_finishing} - Цена отделки в млн/руб\n
                               {calc_resp.terminal_value} - Расчетная цена объекта в конце инвестиционного цикла в млн/руб\n
                               {calc_resp.rent_tax} - Налог на аренду в млн/руб\n
                               {calc_resp.rent_income} - Прибыль от аренды в млн/руб\n
                           """
                else:
                    calc_resp_text = ""

                prompt = (
                        "Сделай мне из этого объекта текст для клиента."
                        "Каждый параметр на новой строке с подходящим смайликом"
                        "И небольшой абзац, который описывает параметры"
                        "Время до метро указано в секундах. Переводи их в минуты. (1 минут = 60 секунд)"
                        "Не обращайся к клиенту, а лишь расскажи про объект. "
                        "НЕ УКАЗЫВАЙ ССЫЛКИ И ФОТОГРАФИИ, ОНИ ДЛЯ МЕНЕДЖЕРА!!\n\n"
                        + str(offer) + "\n\n"
                        + calc_resp_text
                )
                offer_text = await self.llm_client.generate(prompt, 0.5)
                offer_text_with_link = (
                    offer_text +
                    "\n\nСсылка для саммари для менеджера, а не клиента: " +
                    offer.link
                )

                span.set_status(StatusCode.OK)
                return offer_text, offer_text_with_link
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    def __nearest_metro(self, metro_stations: list[model.MetroStation]) -> model.MetroStation:
        with self.tracer.start_as_current_span(
                "EstateSearchMessageService.__nearest_metro",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                metro_distances = [metro.leg_distance for metro in metro_stations]
                nearest_metro_distance = min(metro_distances)
                span.set_attribute("nearest_metro_distance", nearest_metro_distance)
                nearest_metro_idx = metro_distances.index(nearest_metro_distance)
                span.set_attribute("nearest_metro_idx", nearest_metro_idx)
                nearest_metro = metro_stations[nearest_metro_idx]

                span.set_status(StatusCode.OK)
                return nearest_metro
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def __process_count_estate_search(self, state: model.State) -> None:
        await self.state_repo.increment_estate_search_count(state.id)
        self.logger.debug("Инкрементировали счетчик подбора недвижимости")

        if not state.is_transferred_to_manager:
            if state.count_estate_search == 2 - 1:
                self.logger.info("Счетчик расчета подбора недвижимости сигнализирует о 'Высокой вовлеченности'")
                await self.chat_client.edit_lead(
                    state.tg_chat_id,
                    self.amocrm_main_pipeline_id,
                    self.amocrm_pipeline_status_high_engagement
                )
            elif state.count_estate_search == 7 - 1:
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
