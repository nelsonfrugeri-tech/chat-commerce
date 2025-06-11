import json
from openai import AsyncOpenAI
from typing import Generator


class OpenAIClient:
    def __init__(self):
        self.client = AsyncOpenAI()

    async def embed(
        self, text: str, model: str = "text-embedding-3-small", dimensions: int = 1536
    ) -> list[float]:
        response = await self.client.embeddings.create(
            model=model,
            input=[text],
            dimensions=dimensions,
            encoding_format="float",
        )

        return response.data[0].embedding

    async def chat_with_json_response(
        self, messages: list[dict], model: str = "gpt-4.1-mini"
    ) -> dict:
        response = await self.client.chat.completions.create(
            model=model, messages=messages, response_format={"type": "json_object"}
        )
        return (
            response.choices[0].message.content
            if isinstance(response.choices[0].message.content, dict)
            else json.loads(response.choices[0].message.content)
        )

    async def stream_chat_completion(self, messages, model="gpt-4.1-mini"):
        stream = await self.client.chat.completions.create(
            model=model, messages=messages, stream=True
        )

        async for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
