from openai import OpenAI
from typing import Optional


class OpenAIClient:
    def __init__(
        self,
        model: str = "gpt-4.1-mini",
        timeout: int = 60,
    ):
        self.model = model
        self.client = OpenAI(timeout=timeout)

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        messages = []

        if system:
            messages.append({
                "role": "system",
                "content": system
            })

        messages.append({
            "role": "user",
            "content": prompt
        })

        response = self.client.responses.create(
            model=self.model,
            input=messages,
            temperature=temperature,
        )

        # 가장 안전한 텍스트 추출
        return response.output_text
