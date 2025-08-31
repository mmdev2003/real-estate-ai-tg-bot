import httpx

import openai
from opentelemetry.trace import Status, StatusCode, SpanKind

from internal import interface
from internal import model


class GPTClient(interface.ILLMClient):
    def __init__(
            self,
            tel: interface.ITelemetry,
            api_key: str
    ):
        self.tracer = tel.tracer()
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            http_client=httpx.AsyncClient()
        )
    async def generate(
            self,
            history: list[model.Message],
            system_prompt: str,
            temperature: float,
            _model: str = "gpt-4o-mini",
            base64img: str = None
    ) -> str:
        with self.tracer.start_as_current_span(
                "GPTClient.generate",
                kind=SpanKind.CLIENT,
        ) as span:
            try:
                system_prompt = [{"role": "user", "content": system_prompt}]

                history = [
                    *system_prompt,
                    *[
                        {"role": message.role, "content": message.text}
                        for message in history
                    ]
                ]

                if base64img is not None:
                    history[-1]["content"] = [
                        {
                            "type": "text",
                            "text": history[-1]["content"],
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{base64img}"},
                        },
                    ]

                response = await self.client.chat.completions.create(
                    model=_model,
                    messages=history,
                    temperature=temperature,
                )
                llm_response = response.choices[0].message.content

                span.set_status(Status(StatusCode.OK))
                return str(llm_response).replace("#", "").replace("*", "")
            except Exception as err:
                span.record_exception(err)
                span.set_status(Status(StatusCode.ERROR, str(err)))
                raise
