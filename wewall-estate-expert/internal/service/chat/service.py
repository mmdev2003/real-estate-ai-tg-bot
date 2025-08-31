from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface
from internal import common
from internal import model


class ChatService(interface.IChatService):

    def __init__(
            self,
            tel: interface.ITelemetry,
            chat_repo: interface.IChatRepo,
            llm_client: interface.ILLMClient,
            prompt_service: interface.IPromptService,
    ):
        self.tracer = tel.tracer()
        self.logger = tel.logger()
        self.chat_repo = chat_repo
        self.llm_client = llm_client
        self.prompt_service = prompt_service

    async def create_chat(self, tg_chat_id: int) -> int:
        with self.tracer.start_as_current_span(
                "ChatService.create_chat",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id,
                }
        ) as span:
            try:
                chat_id = await self.chat_repo.create_chat(tg_chat_id)
                span.set_attribute("chat_id", chat_id)

                span.set_status(Status(StatusCode.OK))
                return chat_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def create_message(self, tg_chat_id: int, text: str, role: str) -> int:
        with self.tracer.start_as_current_span(
                "ChatService.create_message",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id,
                    "text": text,
                    "role": role,
                }
        ) as span:
            try:
                message_id = await self.chat_repo.create_message(tg_chat_id, text, role)
                span.set_attribute("message_id", message_id)

                span.set_status(Status(StatusCode.OK))
                return message_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_message_wewall_expert(self, chat_id: int, text: str) -> str:
        with self.tracer.start_as_current_span(
                "ChatService.send_message_wewall_expert",
                kind=SpanKind.INTERNAL,
                attributes={
                    "chat_id": chat_id,
                    "text": text,
                }
        ) as span:
            try:
                await self.chat_repo.create_message(chat_id, text, common.Roles.user)
                all_message = await self.chat_repo.message_by_chat_id(chat_id)
                system_prompt = await self.prompt_service.wewall_expert_system_prompt()
                llm_response = await self.llm_client.generate(all_message, system_prompt, 0.7)

                if self.__check_command_in_response(llm_response):
                    self.logger.info(f"LLM ответила командой")
                    span.set_status(Status(StatusCode.OK))
                    return llm_response
                else:
                    message_id = await self.chat_repo.create_message(chat_id, llm_response, common.Roles.assistant)
                    span.set_attribute("message_id", message_id)

                    span.set_status(Status(StatusCode.OK))
                    return llm_response
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_message_estate_expert(self, chat_id: int, text: str) -> str:
        with self.tracer.start_as_current_span(
                "ChatService.send_message_estate_expert",
                kind=SpanKind.INTERNAL,
                attributes={
                    "chat_id": chat_id,
                    "text": text,
                }
        ) as span:
            try:
                await self.chat_repo.create_message(chat_id, text, common.Roles.user)
                all_message = await self.chat_repo.message_by_chat_id(chat_id)
                system_prompt = await self.prompt_service.estate_expert_system_prompt()
                llm_response = await self.llm_client.generate(all_message, system_prompt, 0.1, "gpt-4o")

                if self.__check_command_in_response(llm_response):
                    self.logger.info(f"LLM ответила командой")
                    span.set_status(Status(StatusCode.OK))
                    return llm_response
                else:
                    message_id = await self.chat_repo.create_message(chat_id, llm_response, common.Roles.assistant)
                    span.set_attribute("message_id", message_id)

                    span.set_status(Status(StatusCode.OK))
                    return llm_response
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_message_estate_search_expert(self, chat_id: int, text: str) -> str:
        with self.tracer.start_as_current_span(
                "ChatService.send_message_estate_search_expert",
                kind=SpanKind.INTERNAL,
                attributes={
                    "chat_id": chat_id,
                    "text": text,
                }
        ) as span:
            try:
                await self.chat_repo.create_message(chat_id, text, common.Roles.user)
                all_message = await self.chat_repo.message_by_chat_id(chat_id)
                system_prompt = await self.prompt_service.estate_search_expert_prompt()
                llm_response = await self.llm_client.generate(all_message, system_prompt, 0.1, "gpt-4o")

                if self.__check_command_in_response(llm_response):
                    self.logger.info(f"LLM ответила командой")
                    span.set_status(Status(StatusCode.OK))
                    return llm_response
                else:
                    message_id = await self.chat_repo.create_message(chat_id, llm_response, common.Roles.assistant)
                    span.set_attribute("message_id", message_id)

                    span.set_status(Status(StatusCode.OK))
                    return llm_response
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_message_estate_claculator_expert(self, chat_id: int, text: str) -> str:
        with self.tracer.start_as_current_span(
                "ChatService.send_message_estate_claculator_expert",
                kind=SpanKind.INTERNAL,
                attributes={
                    "chat_id": chat_id,
                    "text": text,
                }
        ) as span:
            try:
                await self.chat_repo.create_message(chat_id, text, common.Roles.user)
                all_message = await self.chat_repo.message_by_chat_id(chat_id)
                system_prompt = await self.prompt_service.estate_calculator_expert_prompt()
                llm_response = await self.llm_client.generate(all_message, system_prompt, 0.1, "gpt-4o")

                if self.__check_command_in_response(llm_response):
                    self.logger.info(f"LLM ответила командой")
                    span.set_status(Status(StatusCode.OK))
                    return llm_response
                else:
                    message_id = await self.chat_repo.create_message(chat_id, llm_response, common.Roles.assistant)
                    span.set_attribute("message_id", message_id)

                    span.set_status(Status(StatusCode.OK))
                    return llm_response
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def send_message_contact_collector(self, chat_id: int, text: str) -> str:
        with self.tracer.start_as_current_span(
                "ChatService.send_message_contact_collector",
                kind=SpanKind.INTERNAL,
                attributes={
                    "chat_id": chat_id,
                    "text": text,
                }
        ) as span:
            try:
                await self.chat_repo.create_message(chat_id, text, common.Roles.user)
                all_message = await self.chat_repo.message_by_chat_id(chat_id)
                system_prompt = await self.prompt_service.contact_collector_prompt()
                llm_response = await self.llm_client.generate(all_message, system_prompt, 0.6)

                if self.__check_command_in_response(llm_response):
                    self.logger.info(f"LLM ответила командой")
                    span.set_status(Status(StatusCode.OK))
                    return llm_response
                else:
                    message_id = await self.chat_repo.create_message(chat_id, llm_response, common.Roles.assistant)
                    span.set_attribute("message_id", message_id)

                    span.set_status(Status(StatusCode.OK))
                    return llm_response
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def get_chat_summary(self, chat_id: int) -> str:
        with self.tracer.start_as_current_span(
                "ChatService.get_chat_summary",
                kind=SpanKind.INTERNAL,
                attributes={
                    "chat_id": chat_id
                }
        ) as span:
            try:
                text = (
                    "Это был диалог с нейросети с клиентом. "
                    "Я менеджер, сделай пересказ диалога для меня, чтобы я понял чего хочет клиент. "
                    "Если была ссылка на помещение, то пришли ее тоже"
                )
                message_id = await self.chat_repo.create_message(
                    chat_id,
                    text,
                    common.Roles.user
                )

                all_message = await self.chat_repo.message_by_chat_id(chat_id)
                chat_summary = await self.llm_client.generate(all_message, text, 0.6)
                await self.chat_repo.create_message(chat_id, chat_summary, common.Roles.assistant)

                span.set_status(Status(StatusCode.OK))
                return chat_summary
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def chat_by_tg_chat_id(self, tg_chat_id: int) -> list[model.Chat]:
        with self.tracer.start_as_current_span(
                "ChatService.chat_by_tg_chat_id",
                kind=SpanKind.INTERNAL,
                attributes={
                    "tg_chat_id": tg_chat_id
                }
        ) as span:
            try:
                chat = await self.chat_repo.chat_by_tg_chat_id(tg_chat_id)

                span.set_status(Status(StatusCode.OK))
                return chat
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def delete_all_message(self, chat_id: int) -> None:
        with self.tracer.start_as_current_span(
                "ChatService.delete_all_message",
                kind=SpanKind.INTERNAL,
                attributes={
                    "chat_id": chat_id
                }
        ) as span:
            try:
                await self.chat_repo.delete_all_message(chat_id)
                span.set_status(Status(StatusCode.OK))
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    def __check_command_in_response(self, llm_response: str) -> bool:
        with self.tracer.start_as_current_span(
                "ChatService.__check_command_in_response",
                kind=SpanKind.INTERNAL,
                attributes={
                    "llm_response": llm_response
                }
        ) as span:
            try:
                if any(
                        command in llm_response
                        for command in (
                                common.StateSwitchCommand.to_estate_search_expert,
                                common.StateSwitchCommand.to_estate_expert,
                                common.StateSwitchCommand.to_wewall_expert,
                                common.StateSwitchCommand.to_estate_finance_model_expert,
                        )
                ):
                    span.set_status(Status(StatusCode.OK))
                    return True
                else:
                    span.set_status(Status(StatusCode.OK))
                    return False
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err