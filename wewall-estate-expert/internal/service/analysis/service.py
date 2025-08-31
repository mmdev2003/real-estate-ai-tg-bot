import io
import base64
from datetime import datetime

from opentelemetry.trace import Status, StatusCode, SpanKind
import pdf2image

from internal import interface
from internal import common
from internal import model

class AnalysisService(interface.IAnalysisService):
    def __init__(
            self,
            tel: interface.ITelemetry,
            analysis_repo: interface.IAnalysisRepo,
            llm_client: interface.ILLMClient
    ):
        self.tracer = tel.tracer()
        self.analysis_repo = analysis_repo
        self.llm_client = llm_client

    async def analysis_from_pdf(self, ctx: dict, pdf_path: str) -> int:
        with self.tracer.start_as_current_span(
                "AnalysisService.analysis_from_pdf",
                kind=SpanKind.INTERNAL,
                attributes={
                    "pdf_path": pdf_path
                }
        ) as span:
            try:
                analysis_summary = ""
                analysis_name = ""
                history = []
                images = self.__pdf2image(pdf_path)
                for current_page, image in enumerate(images):
                    current_page += 1
                    print(f"{current_page}-я страница", flush=True)

                    base64image = base64.b64encode(image.getvalue()).decode('utf-8')

                    if current_page == len(images):
                        history.append(model.Message(0, "", common.Roles.user, "Последняя страница", datetime.now()))
                        llm_response = await self.__send_message(history, base64image)
                        history.append(model.Message(0, "", common.Roles.assistant, llm_response, datetime.now()))

                        analysis_summary += "\n" + llm_response + "\n"
                        history.append(
                            model.Message(0, "", common.Roles.user, "Напиши мне сейчас только название этой презентации",
                                          datetime.now()))
                        analysis_name = await self.__send_message(history)

                    else:
                        history.append(model.Message(0, "", common.Roles.user, f"{current_page}-я страница", datetime.now()))
                        llm_response = await self.__send_message(history, base64image)
                        history.append(model.Message(0, "", common.Roles.assistant, llm_response, datetime.now()))

                        analysis_summary += "\n" + llm_response + "\n"

                    del image
                del images
                analysis_id = await self.analysis_repo.create_analysis(analysis_name, analysis_summary)

                span.set_status(Status(StatusCode.OK))
                return analysis_id
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    async def __send_message(self, history: list, base64img: str = None) -> str:
        with self.tracer.start_as_current_span(
                "AnalysisService.__send_message",
                kind=SpanKind.INTERNAL,
                attributes={
                    "history": history,
                    "base64img": base64img
                }
        ) as span:
            try:
                system_prompt = "Ты аналитик недвижимости. Я буду тебе скидывать страницы презентации аналитического обзора по рынку недвижимости, а ты делай саммари этих страниц, конспектируя всю информацию, которую ты видишь"
                llm_response = await self.llm_client.generate(
                    history,
                    system_prompt,
                    0.7,
                    base64img=base64img
                )

                span.set_status(Status(StatusCode.OK))
                return llm_response
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err

    def __pdf2image(self, pdf_path: str) -> list[io.BytesIO] | None:
        with self.tracer.start_as_current_span(
                "AnalysisService.__pdf2image",
                kind=SpanKind.INTERNAL,
                attributes={
                    "pdf_path": pdf_path
                }
        ) as span:
            try:
                pdf_images = pdf2image.convert_from_path(f"{pdf_path}")

                result = []
                for page in range(len(pdf_images)):
                    image_buffer = io.BytesIO()
                    pdf_images[page].save(image_buffer, 'PNG')
                    image_buffer.seek(0)
                    result.append(image_buffer)

                span.set_status(Status(StatusCode.OK))
                return result
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise err
