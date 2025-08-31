import logging
from openai import OpenAI

from internal import interface
from internal import model


class QwenClient(ILLMClient):
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

    async def generate(
            self,
            history: list[model.Message],
            system_prompt: str,
            temperature: float,
            _model: str = "gpt-4o-mini"
    ) -> str:
        client = OpenAI(
            api_key=self.api_key,
            base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        )
        system_message = {"role": "system", "content": system_prompt}
        history = [system_message] + [
            {"role": message.role, "content": message.text}
            for message in history
        ]

        response = client.chat.completions.create(
            model="qwen-plus-latest",
            messages=history,
            temperature=temperature
        )

        response = response.model_dump()
        llm_response = response["choices"][0]["message"]["content"]

        if isinstance(llm_response, str):
            return str(llm_response).replace("#", "").replace("*", "")

        else:
            logging.warning(f"Ответ от llm не строка, мы такого не ждали: {llm_response}")
            return "Ошибка llm"
