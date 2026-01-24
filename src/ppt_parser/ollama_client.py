import requests
from typing import Optional
from pathlib import Path


class OllamaClient:
    def __init__(
        self,
        model: str = "llama3.1",
        base_url: str = "http://127.0.0.1:11434",
        timeout: int = 60,
    ):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        url = f"{self.base_url}/api/generate"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }

        if system:
            payload["system"] = system

        response = requests.post(
            url,
            json=payload,
            timeout=self.timeout,
        )

        return response.json()["response"]

    def generate_with_file(self, file_path: Path) -> str:
        url = f"{self.base_url}/api/generate"

        prompt = f"<file:{file_path.resolve()}>"

        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
        }

        response = requests.post(
            url,
            json=payload,
            timeout=self.timeout,
        )

        return response.json()["response"]