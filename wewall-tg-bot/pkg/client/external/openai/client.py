import logging
import httpx

import openai

from internal import interface


class GPTClient(interface.ILLMClient):
    def __init__(self, api_key: str):
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            http_client=httpx.AsyncClient()
        )
    # proxy="http://yJJaoHFpzj4tYFoqyWDF:RNW78Fm5@185.162.130.86:10000"
    async def generate(
            self,
            text: str,
            temperature: float,
            system_prompt: str = None,
            _model: str = "gpt-4o"
    ) -> str:

        history = [
            {"role": "user", "content": text}
        ]

        if system_prompt is not None:
            history = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ]

        response = await self.client.chat.completions.create(
            model=_model,
            messages=history,
            temperature=0,
            top_p=0
        )

        llm_response = response.choices[0].message.content

        if isinstance(llm_response, str):
            return str(llm_response).replace("#", "").replace("*", "")

        else:
            logging.warning(f"Ответ от llm не строка, мы такого не ждали: {llm_response}")
            return "Ошибка llm"
