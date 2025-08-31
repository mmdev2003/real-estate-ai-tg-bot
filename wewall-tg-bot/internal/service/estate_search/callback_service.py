from aiogram.types import CallbackQuery, InputMediaDocument, InputMediaPhoto, InlineKeyboardMarkup
from opentelemetry.trace import SpanKind, StatusCode

from internal import model, common, interface


class EstateSearchCallbackService(interface.IEstateSearchCallbackService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            state_repo: interface.IStateRepo,
            estate_search_state_repo: interface.IEstateSearchStateRepo,
            estate_expert_client: interface.IWewallEstateExpertClient,
            estate_calculator_client: interface.IWewallEstateCalculatorClient,
            estate_search_inline_keyboard_generator: interface.IEstateSearchInlineKeyboardGenerator,
            chat_client: interface.IWewallChatClient,
            llm_client: interface.ILLMClient
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()

        self.state_repo = state_repo
        self.estate_search_state_repo = estate_search_state_repo
        self.estate_expert_client = estate_expert_client
        self.estate_calculator_client = estate_calculator_client
        self.estate_search_inline_keyboard_generator = estate_search_inline_keyboard_generator
        self.chat_client = chat_client
        self.llm_client = llm_client

    async def like_offer(self, callback: CallbackQuery, state: model.State, offer_id: int):
        with self.tracer.start_as_current_span(
                "EstateSearchCallbackService.like_offer",
                kind=SpanKind.INTERNAL,
                attributes={
                    "offer_id": offer_id
                }
        ) as span:
            try:
                await self.state_repo.change_status(state.id, common.StateStatuses.contact_collector)
                estate_search_state = (await self.estate_search_state_repo.estate_search_state_by_state_id(state.id))[0]
                offer = estate_search_state.offers[offer_id]

                text_for_llm = (
                        "Сделай мне из этого словаря красивый текст для менеджера, перечисли каждый параметр объекта\n\n"
                        + str(offer)
                )
                offer_text = await self.llm_client.generate(text_for_llm, 0.5)

                llm_response = await self.estate_expert_client.send_message_to_contact_collector(
                    state.tg_chat_id,
                    "Собери мою контактную информацию. Мне понравился этот объект\n\n\n" + offer_text
                )

                await callback.message.answer(llm_response)
                await self.chat_client.import_message_to_amocrm(callback.message.chat.id, llm_response)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise

    async def next_offer(self, callback: CallbackQuery, state: model.State):
        with self.tracer.start_as_current_span(
                "EstateSearchCallbackService.next_offer",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                await self.estate_expert_client.add_message_to_chat(state.tg_chat_id, "Следующее помещение", "user")

                state_estate_search = (await self.estate_search_state_repo.estate_search_state_by_state_id(state.id))[0]

                current_offer_id = state_estate_search.current_offer_id + 1
                span.set_attribute("current_offer_id", current_offer_id)
                await self.estate_search_state_repo.change_current_offer_by_state_id(state.id, current_offer_id)

                if current_offer_id >= len(state_estate_search.offers):
                    self.logger.info("Помещений больше нет")
                    await callback.message.answer(common.no_more_offers)
                    await self.chat_client.import_message_to_amocrm(callback.message.chat.id, common.no_more_offers)

                    return

                offer = state_estate_search.offers[current_offer_id]
                current_estate_id = state_estate_search.current_estate_id + 1
                if offer.estate_id == current_estate_id:
                    self.logger.info("Перешли на следующее здание")
                    await self.estate_search_state_repo.change_current_estate_by_state_id(
                        state.id,
                        current_estate_id
                    )

                document_media_group, calc_resp = await self.__get_finance_model(state_estate_search, offer)

                offer_text, offer_text_with_link = await self.__generate_offer_text(offer, calc_resp)
                keyboard = await self.__generate_offer_keyboard(state_estate_search, current_offer_id,
                                                                current_estate_id)
                photo_media_group = [
                    InputMediaPhoto(media=image_url)
                    for image_url in offer.image_urls
                ]
                # ANSWER
                try:
                    await callback.message.answer_media_group(photo_media_group[:10])
                except Exception:
                    self.logger.debug("Нет фотографий этого помещения")
                    await callback.message.answer("Нет фотографий этого помещения")
                await callback.message.answer(offer_text, reply_markup=keyboard)
                if document_media_group is not None:
                    await callback.message.answer_media_group(document_media_group)

                await self.estate_expert_client.add_message_to_chat(state.tg_chat_id, offer_text_with_link, "assistant")
                await self.chat_client.import_message_to_amocrm(callback.message.chat.id, offer_text)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def next_estate(self, callback: CallbackQuery, state: model.State):
        with self.tracer.start_as_current_span(
                "EstateSearchCallbackService.next_estate",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                await self.estate_expert_client.add_message_to_chat(state.tg_chat_id, "Следующий проект", "user")

                state_estate_search = (await self.estate_search_state_repo.estate_search_state_by_state_id(state.id))[0]

                current_estate_id = state_estate_search.current_estate_id + 1
                await self.estate_search_state_repo.change_current_estate_by_state_id(state.id, current_estate_id)
                if current_estate_id >= len({offer.estate_id for offer in state_estate_search.offers}):
                    self.logger.info("Зданий больше нет")
                    await callback.message.answer(common.no_more_estates)
                    await self.chat_client.import_message_to_amocrm(callback.message.chat.id, common.no_more_estates)

                    return
                for current_offer_id, offer in enumerate(state_estate_search.offers):
                    if offer.estate_id == current_estate_id:
                        await self.estate_search_state_repo.change_current_offer_by_state_id(state.id, current_offer_id)

                        document_media_group, calc_resp = await self.__get_finance_model(state_estate_search, offer)

                        offer_text, offer_text_with_link = await self.__generate_offer_text(offer, calc_resp)
                        keyboard = await self.__generate_offer_keyboard(state_estate_search, current_offer_id,
                                                                        current_estate_id)

                        photo_media_group = [
                            InputMediaPhoto(media=image_url)
                            for image_url in offer.image_urls
                        ]
                        try:
                            await callback.message.answer_media_group(photo_media_group[:10])
                        except Exception:
                            self.logger.debug("Нет фотографий этого помещения")
                            await callback.message.answer("Нет фотографий этого помещения")
                        await callback.message.answer(offer_text, reply_markup=keyboard)
                        if document_media_group is not None:
                            await callback.message.answer_media_group(document_media_group)

                        await self.estate_expert_client.add_message_to_chat(state.tg_chat_id, offer_text_with_link,
                                                                            "assistant")
                        await self.chat_client.import_message_to_amocrm(callback.message.chat.id, offer_text)

                        span.set_status(StatusCode.OK)
                        return

            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def __get_finance_model(
            self,
            state_estate_search: model.EstateSearchState,
            offer: model.SaleOffer | model.RentOffer
    ) -> tuple[list[InputMediaDocument], model.FinanceModelResponse]:
        with self.tracer.start_as_current_span(
                "EstateSearchCallbackService.__get_finance_model",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
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

                span.set_status(StatusCode.OK)
                return document_media_group, calc_resp
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def __generate_offer_keyboard(self, state_estate_search: model.EstateSearchState, current_offer_id: int,
                                        current_estate_id: int) -> InlineKeyboardMarkup:
        with self.tracer.start_as_current_span(
                "EstateSearchMessageService.__generate_offer_keyboard",
                kind=SpanKind.INTERNAL
        ) as span:
            try:
                if current_offer_id == len(state_estate_search.offers) - 1:
                    self.logger.debug("Показываем кнопку с оффером на последнем помещении")
                    keyboard = await self.estate_search_inline_keyboard_generator.last_offer(current_offer_id)
                elif current_estate_id >= len({offer.estate_id for offer in state_estate_search.offers}) - 1:
                    self.logger.debug("Показываем кнопку с оффером на последнем здании")
                    keyboard = await self.estate_search_inline_keyboard_generator.last_estate(current_offer_id)

                else:
                    keyboard = await self.estate_search_inline_keyboard_generator.middle_offer(current_offer_id)

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

    def __nearest_metro(self, metro_stations: list[model.MetroStation]) -> model.MetroStation:
        with self.tracer.start_as_current_span(
                "EstateSearchCallbackService.__nearest_metro",
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
                raise

    async def __generate_offer_text(
            self,
            offer: model.SaleOffer | model.RentOffer,
            calc_resp: model.FinanceModelResponse | None
    ) -> tuple[str, str]:
        with self.tracer.start_as_current_span(
                "EstateSearchCallbackService.__generate_offer_text",
                kind=SpanKind.INTERNAL,
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
                raise
