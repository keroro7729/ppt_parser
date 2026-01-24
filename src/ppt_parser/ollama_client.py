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
            "options": {
                "temperature": temperature,
            },
            "stream": False,
        }

        if system:
            payload["system"] = system

        response = requests.post(
            url,
            json=payload,
            timeout=self.timeout,
        )
        response.raise_for_status()

        return response.json()["response"]
    
    def generate_with_file(self, file_path: Path) -> str:
        url = f"{self.base_url}/api/generate"

        with open(file_path, "rb") as f:
            response = requests.post(
                url,
                timeout=self.timeout,
                files={
                    "file": f,
                },
                data={
                    "model": self.model,
                    "stream": "false",
                },
            )

        response.raise_for_status()
        return response.json()["response"]

