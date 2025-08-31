import uuid
from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import model, interface, common


class AmocrmChatService(interface.IAmocrmChatService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            amocrm_client: interface.IAmocrmClient,
            amocrm_chat_repo: interface.IAmocrmChatRepo,
            wewall_tg_bot_client: interface.IWewallTgBotClient,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.amocrm_client = amocrm_client
        self.amocrm_chat_repo = amocrm_chat_repo
        self.wewall_tg_bot_client = wewall_tg_bot_client

    async def create_chat_with_amocrm_manager_from_tg(
            self,
            amocrm_pipeline_id: int,
            tg_chat_id: int,
            tg_username: str,
            first_name: str,
            last_name: str
    ):
        with self.tracer.start_as_current_span(
                "AmocrmChatService.create_chat_with_amocrm_manager_from_tg",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_pipeline_id": amocrm_pipeline_id,
                    "tg_chat_id": tg_chat_id,
                    "tg_username": tg_username,
                    "first_name": first_name,
                    "last_name": last_name,
                }
        ) as span:
            try:
                contact = await self.amocrm_chat_repo.contact_by_tg_chat_id(tg_chat_id)
                if not contact:
                    contact = await self.__create_contact(tg_chat_id, first_name, last_name, tg_username)
                contact = contact[0]

                lead = await self.amocrm_chat_repo.lead_by_amocrm_contact_id(contact.amocrm_contact_id)
                if not lead:
                    lead = await self.__create_lead(contact.amocrm_contact_id, amocrm_pipeline_id)
                lead = lead[0]

                chat = await self.amocrm_chat_repo.chat_by_amocrm_lead_id(lead.amocrm_lead_id)
                if not chat:
                    chat = await self.__create_chat(contact.amocrm_contact_id, lead.amocrm_lead_id, first_name,
                                                    last_name)
                chat = chat[0]

                await self.amocrm_client.assign_chat_to_contact(chat.amocrm_chat_id, contact.amocrm_contact_id)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def edit_lead(
            self,
            tg_chat_id: int,
            amocrm_pipeline_id: int,
            amocrm_pipeline_status_id: int
    ) -> None:
        with self.tracer.start_as_current_span(
                "AmocrmChatService.edit_lead",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id,
                    "amocrm_pipeline_id": amocrm_pipeline_id,
                    "amocrm_pipeline_status_id": amocrm_pipeline_status_id
                }
        ) as span:
            try:
                contact = (await self.amocrm_chat_repo.contact_by_tg_chat_id(tg_chat_id))[0]
                lead = (await self.amocrm_chat_repo.lead_by_amocrm_contact_id(contact.amocrm_contact_id))[0]

                await self.amocrm_client.edit_lead(lead.amocrm_lead_id, amocrm_pipeline_id, amocrm_pipeline_status_id)
                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def send_message_from_tg_to_amocrm(
            self,
            tg_chat_id: int,
            text: str,
    ):
        with self.tracer.start_as_current_span(
                "AmocrmChatService.send_message_from_tg_to_amocrm",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id,
                    "text": text
                }
        ) as span:
            try:
                contact = (await self.amocrm_chat_repo.contact_by_tg_chat_id(tg_chat_id))[0]
                lead = (await self.amocrm_chat_repo.lead_by_amocrm_contact_id(contact.amocrm_contact_id))[0]
                chat = (await self.amocrm_chat_repo.chat_by_amocrm_lead_id(lead.amocrm_lead_id))[0]

                amocrm_message_id = await self.amocrm_client.send_message_from_contact(
                    contact.amocrm_contact_id,
                    chat.amocrm_conversation_id,
                    chat.amocrm_chat_id,
                    contact.name,
                    text,
                )
                span.set_attribute("amocrm_message_id", amocrm_message_id)

                await self.amocrm_chat_repo.create_amocrm_message(amocrm_message_id, chat.amocrm_chat_id, "contact",
                                                                  text)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def import_message_from_bot_to_amocrm(
            self,
            tg_chat_id: int,
            text: str,
    ):
        with self.tracer.start_as_current_span(
                "AmocrmChatService.import_message_from_bot_to_amocrm",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id,
                    "text": text,
                }
        ) as span:
            try:
                contact = (await self.amocrm_chat_repo.contact_by_tg_chat_id(tg_chat_id))[0]
                lead = (await self.amocrm_chat_repo.lead_by_amocrm_contact_id(contact.amocrm_contact_id))[0]
                chat = (await self.amocrm_chat_repo.chat_by_amocrm_lead_id(lead.amocrm_lead_id))[0]

                amocrm_message_id = await self.amocrm_client.import_message_from_bot_to_amocrm(
                    chat.amocrm_conversation_id,
                    chat.amocrm_chat_id,
                    contact.amocrm_contact_id,
                    contact.name,
                    text,
                )
                span.set_attribute("amocrm_message_id", amocrm_message_id)

                await self.amocrm_chat_repo.create_amocrm_message(amocrm_message_id, chat.amocrm_chat_id, "contact",
                                                                  text)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def send_message_from_amocrm_to_tg(
            self,
            amocrm_chat_id: str,
            amocrm_message_id: str,
            text: str
    ):
        with self.tracer.start_as_current_span(
                "AmocrmChatService.send_message_from_amocrm_to_tg",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_chat_id": amocrm_chat_id,
                    "amocrm_message_id": amocrm_message_id,
                    "text": text,
                }
        ) as span:
            try:
                chat = (await self.amocrm_chat_repo.chat_by_id(amocrm_chat_id))[0]
                lead = (await self.amocrm_chat_repo.lead_by_id(chat.amocrm_lead_id))[0]
                contact = (await self.amocrm_chat_repo.contact_by_id(lead.amocrm_contact_id))[0]

                await self.amocrm_chat_repo.create_amocrm_message(amocrm_message_id, amocrm_chat_id, "contact", text)

                await self.wewall_tg_bot_client.send_message_to_user(contact.tg_chat_id, text)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def connect_channel_to_account(self) -> str:
        with self.tracer.start_as_current_span(
                "AmocrmChatService.connect_channel_to_account",
                kind=SpanKind.INTERNAL,
        ) as span:
            try:
                resp = await self.amocrm_client.connect_channel_to_account()

                span.set_status(Status(StatusCode.OK))
                return resp
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def subscribe_to_event_webhook(self, webhook_url: str, event_name: str) -> None:
        with self.tracer.start_as_current_span(
                "AmocrmChatService.subscribe_to_event_webhook",
                kind=SpanKind.INTERNAL,
                attributes={
                    "webhook_url": webhook_url,
                    "event_name": event_name,
                }
        ) as span:
            try:
                await self.amocrm_client.subscribe_to_event_webhook(webhook_url, event_name)
                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def delete_contact(self, amocrm_contact_id: int) -> None:
        with self.tracer.start_as_current_span(
                "AmocrmChatService.delete_contact",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_contact_id": amocrm_contact_id
                }
        ) as span:
            try:
                contact = await self.amocrm_chat_repo.contact_by_id(amocrm_contact_id)
                if not contact:
                    self.logger.info("Контакта нет в БД")
                else:
                    await self.amocrm_chat_repo.delete_amocrm_contact_by_id(amocrm_contact_id)
                    await self.wewall_tg_bot_client.delete_state(contact[0].tg_chat_id)

                lead = await self.amocrm_chat_repo.lead_by_amocrm_contact_id(amocrm_contact_id)
                if not lead:
                    self.logger.info("Сделки нет в БД")
                else:
                    await self.amocrm_chat_repo.delete_amocrm_lead_by_id(lead[0].amocrm_lead_id)

                    chat = await self.amocrm_chat_repo.chat_by_amocrm_lead_id(lead[0].amocrm_lead_id)
                    if not chat:
                        self.logger.info("Чата нет в БД")
                    else:
                        await self.amocrm_chat_repo.delete_amocrm_chat_by_id(chat[0].amocrm_chat_id)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def delete_lead(self, amocrm_lead_id: int) -> None:
        with self.tracer.start_as_current_span(
                "AmocrmChatService.delete_lead",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_lead_id": amocrm_lead_id
                }
        ) as span:
            try:
                lead = await self.amocrm_chat_repo.lead_by_id(amocrm_lead_id)
                if not lead:
                    self.logger.info("Сделки нет в БД")
                else:
                    await self.amocrm_chat_repo.delete_amocrm_lead_by_id(amocrm_lead_id)

                    contact = await self.amocrm_chat_repo.contact_by_id(lead[0].amocrm_contact_id)
                    if not contact:
                        self.logger.info("Контакта нет в БД")
                    else:
                        await self.wewall_tg_bot_client.delete_state(contact[0].tg_chat_id)

                chat = await self.amocrm_chat_repo.chat_by_amocrm_lead_id(amocrm_lead_id)
                if not chat:
                    self.logger.info("Чата нет в БД")
                else:
                    await self.amocrm_chat_repo.delete_amocrm_chat_by_id(chat[0].amocrm_chat_id)

                span.set_status(StatusCode.OK)
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def __create_contact(self, tg_chat_id: int, first_name: str, last_name: str, tg_username: str) -> list[model.AmocrmContact]:
        with self.tracer.start_as_current_span(
                "AmocrmChatService.__create_contact",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id,
                    "first_name": first_name,
                    "last_name": last_name,
                    "tg_username": tg_username,
                }
        ) as span:
            try:
                self.logger.info("Создаем новый контакт в Amocrm")
                contact_name = first_name + " " + last_name
                amocrm_contact_id = await self.amocrm_client.create_contact(contact_name, first_name, last_name, tg_username)
                span.set_attribute("amocrm_contact_id", amocrm_contact_id)

                await self.amocrm_chat_repo.create_amocrm_contact(amocrm_contact_id, contact_name, tg_chat_id)
                contact = await self.amocrm_chat_repo.contact_by_id(amocrm_contact_id)

                span.set_status(StatusCode.OK)
                return contact
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def __create_lead(self, amocrm_contact_id: int, amocrm_pipeline_id: int) -> list[model.AmocrmLead]:
        with self.tracer.start_as_current_span(
                "AmocrmChatService.__create_lead",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_contact_id": amocrm_contact_id,
                    "amocrm_pipeline_id": amocrm_pipeline_id
                }
        ) as span:
            try:
                self.logger.info("Создаем новую сделку в Amocrm")
                amocrm_lead_id = await self.amocrm_client.create_lead(amocrm_contact_id, amocrm_pipeline_id, common.wewall_ai_lead_source)
                span.set_attribute("amocrm_lead_id", amocrm_lead_id)

                await self.amocrm_chat_repo.create_amocrm_lead(amocrm_lead_id, amocrm_contact_id, amocrm_pipeline_id)
                lead = await self.amocrm_chat_repo.lead_by_amocrm_contact_id(amocrm_contact_id)

                span.set_status(StatusCode.OK)
                return lead
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err

    async def __create_chat(self, amocrm_contact_id: int, amocrm_lead_id: int, first_name: str, last_name: str) -> list[
        model.AmocrmChat]:
        with self.tracer.start_as_current_span(
                "AmocrmChatService.__create_chat",
                kind=SpanKind.INTERNAL,
                attributes={
                    "amocrm_contact_id": amocrm_contact_id,
                    "amocrm_lead_id": amocrm_lead_id,
                    "first_name": first_name,
                    "last_name": last_name,
                }
        ) as span:
            try:
                self.logger.info("Создаем новый чат в Amocrm")
                amocrm_conversation_id = str(uuid.uuid4())
                span.set_attribute("amocrm_conversation_id", amocrm_conversation_id)
                amocrm_chat_id = await self.amocrm_client.create_chat(
                    amocrm_conversation_id,
                    amocrm_contact_id,
                    first_name + " " + last_name,
                )
                span.set_attribute("amocrm_chat_id", amocrm_chat_id)

                await self.amocrm_chat_repo.create_amocrm_chat(
                    amocrm_chat_id,
                    amocrm_conversation_id,
                    amocrm_lead_id
                )
                chat = await self.amocrm_chat_repo.chat_by_amocrm_lead_id(amocrm_lead_id)

                span.set_status(StatusCode.OK)
                return chat
            except Exception as err:
                span.record_exception(err)
                span.set_status(StatusCode.ERROR, str(err))
                raise err
