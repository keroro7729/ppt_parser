import requests

url = "http://localhost:11434/api/generate"

payload = {
    "model": "llama3.1",
    "prompt": "한 문장으로 테스트 응답해줘",
    "stream": False,
}

r = requests.post(url, json=payload)
print(r.status_code)
print(r.text)

